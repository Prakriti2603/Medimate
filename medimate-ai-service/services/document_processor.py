"""
Document preprocessing pipeline for medical documents.
Handles PDF extraction, OCR, and image preprocessing.
"""

import logging
import io
import os
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import PyPDF2
import pdfplumber
from pdf2image import convert_from_bytes

from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main document processing class for medical documents."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.supported_formats = settings.supported_formats
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
        
    async def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a document and extract text content.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Validate file
            self._validate_file(file_content, filename)
            
            # Determine file type and process accordingly
            file_extension = Path(filename).suffix.lower().lstrip('.')
            
            if file_extension == 'pdf':
                result = await self._process_pdf(file_content, filename)
            elif file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp']:
                result = await self._process_image(file_content, filename)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            logger.info(f"Document processed successfully: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed for {filename}: {e}")
            raise
    
    def _validate_file(self, file_content: bytes, filename: str) -> None:
        """Validate file size and format."""
        if len(file_content) > self.max_file_size:
            raise ValueError(f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB")
        
        file_extension = Path(filename).suffix.lower().lstrip('.')
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def _process_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process PDF documents using multiple extraction methods."""
        loop = asyncio.get_event_loop()
        
        # Try text extraction first (for digital PDFs)
        text_content = await loop.run_in_executor(
            self.executor, self._extract_pdf_text, file_content
        )
        
        # If text extraction yields minimal content, use OCR
        if len(text_content.strip()) < 100:
            logger.info(f"PDF {filename} has minimal text, using OCR")
            ocr_content = await loop.run_in_executor(
                self.executor, self._extract_pdf_ocr, file_content
            )
            text_content = ocr_content
        
        return {
            'text_content': text_content,
            'extraction_method': 'pdf_text' if len(text_content.strip()) >= 100 else 'pdf_ocr',
            'page_count': self._get_pdf_page_count(file_content),
            'filename': filename,
            'file_type': 'pdf'
        }
    
    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF using pdfplumber and PyPDF2."""
        text_content = ""
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            except Exception as e2:
                logger.error(f"PyPDF2 extraction also failed: {e2}")
                raise
        
        return text_content.strip()
    
    def _extract_pdf_ocr(self, file_content: bytes) -> str:
        """Extract text from PDF using OCR (for scanned PDFs)."""
        try:
            # Convert PDF to images
            images = convert_from_bytes(file_content, dpi=300)
            
            text_content = ""
            for i, image in enumerate(images):
                # Preprocess image for better OCR
                processed_image = self._preprocess_image_for_ocr(np.array(image))
                
                # Perform OCR
                page_text = pytesseract.image_to_string(
                    processed_image,
                    config='--psm 6 --oem 3'  # Assume uniform block of text
                )
                text_content += f"Page {i+1}:\n{page_text}\n\n"
            
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"PDF OCR extraction failed: {e}")
            raise
    
    def _get_pdf_page_count(self, file_content: bytes) -> int:
        """Get the number of pages in a PDF."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            return len(pdf_reader.pages)
        except:
            return 1  # Default fallback
    
    async def _process_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process image documents using OCR."""
        loop = asyncio.get_event_loop()
        
        text_content = await loop.run_in_executor(
            self.executor, self._extract_image_text, file_content
        )
        
        return {
            'text_content': text_content,
            'extraction_method': 'ocr',
            'filename': filename,
            'file_type': 'image'
        }
    
    def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from image using OCR with preprocessing."""
        try:
            # Load image
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to numpy array for preprocessing
            image_array = np.array(image)
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image_array)
            
            # Perform OCR
            text_content = pytesseract.image_to_string(
                processed_image,
                config='--psm 6 --oem 3'
            )
            
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Image OCR extraction failed: {e}")
            raise


class ImagePreprocessor:
    """Advanced image preprocessing for better OCR results."""
    
    @staticmethod
    def preprocess_image_for_ocr(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image to improve OCR accuracy.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()
            
            # Noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Binarization (convert to black and white)
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image
    
    @staticmethod
    def enhance_image_quality(image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better processing."""
        try:
            # Convert to PIL Image for enhancement
            pil_image = Image.fromarray(image)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(pil_image)
            sharpened = enhancer.enhance(1.5)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(sharpened)
            contrasted = enhancer.enhance(1.2)
            
            # Apply unsharp mask filter
            filtered = contrasted.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            return np.array(filtered)
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return image
    
    @staticmethod
    def detect_and_correct_skew(image: np.ndarray) -> np.ndarray:
        """Detect and correct skew in scanned documents."""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Hough line detection
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calculate average angle
                angles = []
                for rho, theta in lines[:10]:  # Use first 10 lines
                    angle = theta * 180 / np.pi
                    if angle > 90:
                        angle = angle - 180
                    angles.append(angle)
                
                if angles:
                    avg_angle = np.mean(angles)
                    
                    # Rotate image if skew is significant
                    if abs(avg_angle) > 0.5:
                        height, width = gray.shape
                        center = (width // 2, height // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                        corrected = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                        return corrected
            
            return image
            
        except Exception as e:
            logger.error(f"Skew correction failed: {e}")
            return image


# Add the preprocessing method to DocumentProcessor
DocumentProcessor._preprocess_image_for_ocr = ImagePreprocessor.preprocess_image_for_ocr