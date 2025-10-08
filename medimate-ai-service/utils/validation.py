"""
Validation utilities for document processing.
"""

import logging
import mimetypes
from typing import List, Tuple, Optional
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentValidator:
    """Validate documents before processing."""
    
    MIME_TYPE_MAPPING = {
        'application/pdf': ['pdf'],
        'image/png': ['png'],
        'image/jpeg': ['jpg', 'jpeg'],
        'image/tiff': ['tiff', 'tif'],
        'image/bmp': ['bmp'],
        'image/gif': ['gif']
    }
    
    @staticmethod
    def validate_file_format(filename: str, file_content: bytes) -> Tuple[bool, str]:
        """
        Validate file format based on extension and content.
        
        Args:
            filename: Original filename
            file_content: File content bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file extension
            file_extension = Path(filename).suffix.lower().lstrip('.')
            
            if not file_extension:
                return False, "File has no extension"
            
            if file_extension not in settings.supported_formats:
                return False, f"Unsupported file format: {file_extension}"
            
            # Validate MIME type from content
            mime_type = DocumentValidator._detect_mime_type(file_content)
            
            if mime_type:
                expected_extensions = DocumentValidator.MIME_TYPE_MAPPING.get(mime_type, [])
                if file_extension not in expected_extensions:
                    return False, f"File extension {file_extension} doesn't match content type {mime_type}"
            
            return True, "Valid file format"
            
        except Exception as e:
            logger.error(f"File format validation failed: {e}")
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_file_size(file_content: bytes) -> Tuple[bool, str]:
        """
        Validate file size.
        
        Args:
            file_content: File content bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            file_size_mb = len(file_content) / (1024 * 1024)
            max_size_mb = settings.max_file_size_mb
            
            if file_size_mb > max_size_mb:
                return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
            
            if len(file_content) == 0:
                return False, "File is empty"
            
            return True, f"Valid file size: {file_size_mb:.1f}MB"
            
        except Exception as e:
            logger.error(f"File size validation failed: {e}")
            return False, f"Size validation error: {str(e)}"
    
    @staticmethod
    def validate_pdf_content(file_content: bytes) -> Tuple[bool, str]:
        """
        Validate PDF file content.
        
        Args:
            file_content: PDF file content bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check PDF header
            if not file_content.startswith(b'%PDF-'):
                return False, "Invalid PDF header"
            
            # Check for PDF trailer
            if b'%%EOF' not in file_content[-1024:]:
                return False, "PDF trailer not found"
            
            # Basic structure validation
            if b'xref' not in file_content:
                return False, "PDF cross-reference table not found"
            
            return True, "Valid PDF content"
            
        except Exception as e:
            logger.error(f"PDF content validation failed: {e}")
            return False, f"PDF validation error: {str(e)}"
    
    @staticmethod
    def validate_image_content(file_content: bytes) -> Tuple[bool, str]:
        """
        Validate image file content.
        
        Args:
            file_content: Image file content bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check common image headers
            image_headers = {
                b'\x89PNG\r\n\x1a\n': 'PNG',
                b'\xff\xd8\xff': 'JPEG',
                b'GIF87a': 'GIF87a',
                b'GIF89a': 'GIF89a',
                b'BM': 'BMP',
                b'II*\x00': 'TIFF (little endian)',
                b'MM\x00*': 'TIFF (big endian)'
            }
            
            for header, format_name in image_headers.items():
                if file_content.startswith(header):
                    return True, f"Valid {format_name} image"
            
            return False, "Unrecognized image format"
            
        except Exception as e:
            logger.error(f"Image content validation failed: {e}")
            return False, f"Image validation error: {str(e)}"
    
    @staticmethod
    def _detect_mime_type(file_content: bytes) -> Optional[str]:
        """Detect MIME type from file content."""
        try:
            # Check magic bytes for common formats
            if file_content.startswith(b'%PDF-'):
                return 'application/pdf'
            elif file_content.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'image/png'
            elif file_content.startswith(b'\xff\xd8\xff'):
                return 'image/jpeg'
            elif file_content.startswith(b'GIF87a') or file_content.startswith(b'GIF89a'):
                return 'image/gif'
            elif file_content.startswith(b'BM'):
                return 'image/bmp'
            elif file_content.startswith(b'II*\x00') or file_content.startswith(b'MM\x00*'):
                return 'image/tiff'
            
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def comprehensive_validation(filename: str, file_content: bytes) -> Tuple[bool, List[str]]:
        """
        Perform comprehensive validation of uploaded file.
        
        Args:
            filename: Original filename
            file_content: File content bytes
            
        Returns:
            Tuple of (is_valid, list_of_messages)
        """
        messages = []
        is_valid = True
        
        # File format validation
        format_valid, format_msg = DocumentValidator.validate_file_format(filename, file_content)
        messages.append(format_msg)
        if not format_valid:
            is_valid = False
        
        # File size validation
        size_valid, size_msg = DocumentValidator.validate_file_size(file_content)
        messages.append(size_msg)
        if not size_valid:
            is_valid = False
        
        # Content-specific validation
        file_extension = Path(filename).suffix.lower().lstrip('.')
        
        if file_extension == 'pdf':
            content_valid, content_msg = DocumentValidator.validate_pdf_content(file_content)
            messages.append(content_msg)
            if not content_valid:
                is_valid = False
        elif file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']:
            content_valid, content_msg = DocumentValidator.validate_image_content(file_content)
            messages.append(content_msg)
            if not content_valid:
                is_valid = False
        
        return is_valid, messages


class TextValidator:
    """Validate extracted text content."""
    
    @staticmethod
    def validate_extracted_text(text: str) -> Tuple[bool, str, Dict[str, any]]:
        """
        Validate extracted text quality and content.
        
        Args:
            text: Extracted text content
            
        Returns:
            Tuple of (is_valid, message, quality_metrics)
        """
        try:
            if not text or not text.strip():
                return False, "No text extracted", {}
            
            # Calculate quality metrics
            metrics = TextValidator._calculate_text_metrics(text)
            
            # Determine if text quality is acceptable
            is_valid = (
                metrics['char_count'] >= 10 and
                metrics['word_count'] >= 3 and
                metrics['readable_ratio'] >= 0.5
            )
            
            message = f"Text quality: {metrics['quality_score']:.2f}"
            
            return is_valid, message, metrics
            
        except Exception as e:
            logger.error(f"Text validation failed: {e}")
            return False, f"Text validation error: {str(e)}", {}
    
    @staticmethod
    def _calculate_text_metrics(text: str) -> Dict[str, any]:
        """Calculate text quality metrics."""
        try:
            char_count = len(text)
            word_count = len(text.split())
            line_count = len(text.splitlines())
            
            # Calculate readable character ratio
            readable_chars = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,!?;:-()[]{}')
            readable_ratio = readable_chars / char_count if char_count > 0 else 0
            
            # Calculate average word length
            words = text.split()
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Simple quality score (0-1)
            quality_score = min(1.0, (
                (readable_ratio * 0.4) +
                (min(avg_word_length / 6, 1.0) * 0.3) +
                (min(word_count / 100, 1.0) * 0.3)
            ))
            
            return {
                'char_count': char_count,
                'word_count': word_count,
                'line_count': line_count,
                'readable_ratio': readable_ratio,
                'avg_word_length': avg_word_length,
                'quality_score': quality_score
            }
            
        except Exception as e:
            logger.error(f"Text metrics calculation failed: {e}")
            return {
                'char_count': 0,
                'word_count': 0,
                'line_count': 0,
                'readable_ratio': 0,
                'avg_word_length': 0,
                'quality_score': 0
            }