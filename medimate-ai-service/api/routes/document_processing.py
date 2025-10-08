"""Document processing endpoints for AI extraction and form filling."""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.document_processor import DocumentProcessor
from services.file_handler import FileHandler
from services.nlp.nlp_service import MedicalNLPService
from models.medical_models import MedicalDocumentClassifier, MedicalFieldExtractor, MedicalFormMapper
from utils.validation import DocumentValidator, TextValidator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
file_handler = FileHandler()
nlp_service = MedicalNLPService()
document_classifier = MedicalDocumentClassifier()
field_extractor = MedicalFieldExtractor()
form_mapper = MedicalFormMapper()


class ExtractionRequest(BaseModel):
    """Request model for document extraction."""
    document_id: str
    extraction_options: Dict[str, Any] = {}


class ExtractedField(BaseModel):
    """Model for extracted field data."""
    field_name: str
    value: Any
    confidence: float
    source: Dict[str, Any]
    alternatives: List[Dict[str, Any]] = []


class ExtractionResult(BaseModel):
    """Response model for document extraction results."""
    document_id: str
    extraction_id: str
    status: str
    extracted_fields: List[ExtractedField]
    confidence_scores: Dict[str, float]
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}


@router.post("/upload", response_model=Dict[str, str])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a medical document for AI processing.
    Supports PDF, images, and other medical document formats.
    """
    try:
        # Validate file type and size
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # TODO: Implement file validation and storage
        # TODO: Trigger background processing
        
        document_id = f"doc_{int(datetime.now().timestamp())}"
        
        logger.info(f"Document uploaded: {file.filename} -> {document_id}")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Document uploaded successfully, processing started"
        }
        
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/extract", response_model=ExtractionResult)
async def extract_fields(request: ExtractionRequest):
    """
    Extract medical information from uploaded document.
    Returns structured data with confidence scores.
    """
    try:
        start_time = datetime.now()
        
        # Load document content
        file_content = await file_handler.load_file(request.document_id)
        if not file_content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process document to extract text
        processing_result = await document_processor.process_document(
            file_content, request.document_id
        )
        
        if not processing_result or not processing_result.get('text_content'):
            raise HTTPException(status_code=400, detail="Failed to extract text from document")
        
        text_content = processing_result['text_content']
        
        # Classify document
        classification = await document_classifier.classify_document(text_content)
        
        # Extract medical entities using NLP
        nlp_result = await nlp_service.process_medical_document(
            text_content, classification.get('document_type')
        )
        
        # Extract specific fields
        field_extraction = await field_extractor.extract_fields(text_content)
        
        # Combine results
        extracted_fields = []
        
        # Add NLP entities
        for entity in nlp_result.get('entities', []):
            extracted_fields.append(ExtractedField(
                field_name=entity['label'].lower(),
                value=entity['text'],
                confidence=entity['confidence'],
                source={
                    "method": "NLP",
                    "start": entity.get('start', 0),
                    "end": entity.get('end', 0)
                },
                alternatives=[{
                    "value": entity.get('normalized_form', entity['text']),
                    "confidence": entity['confidence'] * 0.9
                }] if entity.get('normalized_form') else []
            ))
        
        # Add pattern-extracted fields
        for field_name, field_data in field_extraction.get('extracted_fields', {}).items():
            extracted_fields.append(ExtractedField(
                field_name=field_name,
                value=field_data['value'],
                confidence=field_data['confidence'],
                source={
                    "method": "Pattern",
                    "pattern": field_data.get('pattern_used', ''),
                    "start": field_data.get('start_pos', 0),
                    "end": field_data.get('end_pos', 0)
                }
            ))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate confidence scores
        confidence_scores = {
            "overall": nlp_result.get('document_analysis', {}).get('confidence', 0.0),
            "classification": classification.get('confidence', 0.0),
            "field_extraction": sum(f.confidence for f in extracted_fields) / len(extracted_fields) if extracted_fields else 0.0
        }
        
        result = ExtractionResult(
            document_id=request.document_id,
            extraction_id=f"ext_{int(datetime.now().timestamp())}",
            status="completed",
            extracted_fields=extracted_fields,
            confidence_scores=confidence_scores,
            processing_time=processing_time,
            timestamp=datetime.now(),
            metadata={
                "document_type": classification.get('document_type', 'unknown'),
                "specialty": classification.get('specialty', 'general'),
                "text_length": len(text_content),
                "entities_found": len(nlp_result.get('entities', [])),
                "fields_extracted": len(field_extraction.get('extracted_fields', {}))
            }
        )
        
        logger.info(f"Extraction completed for document: {request.document_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/status/{document_id}")
async def get_processing_status(document_id: str):
    """Get the processing status of a document."""
    try:
        # TODO: Implement status tracking
        
        return {
            "document_id": document_id,
            "status": "processing",
            "progress": 75,
            "estimated_completion": "30 seconds"
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/results/{extraction_id}")
async def get_extraction_results(extraction_id: str):
    """Retrieve extraction results by extraction ID."""
    try:
        # TODO: Implement result retrieval from database
        
        return {
            "extraction_id": extraction_id,
            "status": "completed",
            "results": "Extraction results would be here"
        }
        
    except Exception as e:
        logger.error(f"Result retrieval failed: {e}")
        raise HTTPException(status_code=404, detail="Extraction results not found")


class FormFillRequest(BaseModel):
    """Request model for form auto-fill."""
    document_id: str
    form_type: str
    form_template: Optional[Dict[str, Any]] = None


class FormFillResult(BaseModel):
    """Response model for form auto-fill results."""
    document_id: str
    form_type: str
    filled_form: Dict[str, Any]
    completion_rate: float
    fields_filled: int
    total_fields: int
    validation_results: Dict[str, Any]
    confidence_score: float
    timestamp: datetime


@router.post("/auto-fill", response_model=FormFillResult)
async def auto_fill_form(request: FormFillRequest):
    """
    Automatically fill a medical form based on extracted document information.
    """
    try:
        start_time = datetime.now()
        
        # Load document content
        file_content = await file_handler.load_file(request.document_id)
        if not file_content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process document to extract text
        processing_result = await document_processor.process_document(
            file_content, request.document_id
        )
        
        text_content = processing_result['text_content']
        
        # Use custom form template if provided, otherwise use standard template
        if request.form_template:
            form_result = await nlp_service.auto_fill_form(text_content, request.form_template)
        else:
            # Extract fields and map to form
            field_extraction = await field_extractor.extract_fields(text_content)
            form_result = await form_mapper.map_to_form(
                field_extraction.get('extracted_fields', {}), 
                request.form_type
            )
        
        # Calculate overall confidence
        confidence_scores = [
            field_data.get('confidence', 0) 
            for field_data in form_result.get('mapped_fields', {}).values()
            if field_data.get('value')
        ]
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        result = FormFillResult(
            document_id=request.document_id,
            form_type=request.form_type,
            filled_form=form_result.get('mapped_fields', {}),
            completion_rate=form_result.get('completion_rate', 0),
            fields_filled=form_result.get('fields_filled', 0),
            total_fields=form_result.get('total_fields', 0),
            validation_results=form_result.get('validation', {}),
            confidence_score=overall_confidence,
            timestamp=datetime.now()
        )
        
        logger.info(f"Form auto-fill completed for document: {request.document_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Form auto-fill failed: {e}")
        raise HTTPException(status_code=500, detail=f"Form auto-fill failed: {str(e)}")


@router.get("/forms/templates")
async def get_form_templates():
    """Get available form templates."""
    try:
        templates = form_mapper.get_available_forms()
        template_details = {}
        
        for template_name in templates:
            template_details[template_name] = form_mapper.get_form_template(template_name)
        
        return {
            "available_forms": templates,
            "templates": template_details
        }
        
    except Exception as e:
        logger.error(f"Failed to get form templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.post("/classify")
async def classify_document(request: ExtractionRequest):
    """Classify a medical document by type and specialty."""
    try:
        # Load document content
        file_content = await file_handler.load_file(request.document_id)
        if not file_content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process document to extract text
        processing_result = await document_processor.process_document(
            file_content, request.document_id
        )
        
        text_content = processing_result['text_content']
        
        # Classify document
        classification = await document_classifier.classify_document(text_content)
        
        return {
            "document_id": request.document_id,
            "classification": classification,
            "text_length": len(text_content),
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document classification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.post("/analyze")
async def analyze_document(request: ExtractionRequest):
    """Comprehensive document analysis including classification, extraction, and insights."""
    try:
        start_time = datetime.now()
        
        # Load document content
        file_content = await file_handler.load_file(request.document_id)
        if not file_content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process document to extract text
        processing_result = await document_processor.process_document(
            file_content, request.document_id
        )
        
        text_content = processing_result['text_content']
        
        # Comprehensive analysis
        classification = await document_classifier.classify_document(text_content)
        nlp_analysis = await nlp_service.process_medical_document(
            text_content, classification.get('document_type')
        )
        field_extraction = await field_extractor.extract_fields(text_content)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "document_id": request.document_id,
            "analysis": {
                "classification": classification,
                "nlp_analysis": nlp_analysis,
                "field_extraction": field_extraction,
                "processing_time": processing_time,
                "text_length": len(text_content)
            },
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/suggestions/{document_id}")
async def get_form_suggestions(document_id: str):
    """Get form type suggestions based on document content."""
    try:
        # Load document content
        file_content = await file_handler.load_file(document_id)
        if not file_content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process document to extract text
        processing_result = await document_processor.process_document(
            file_content, document_id
        )
        
        text_content = processing_result['text_content']
        
        # Classify document to suggest appropriate forms
        classification = await document_classifier.classify_document(text_content)
        
        # Map document types to suggested forms
        form_suggestions = {
            'discharge_summary': ['discharge_summary', 'patient_intake'],
            'progress_note': ['patient_intake'],
            'consultation_report': ['patient_intake', 'insurance_claim'],
            'lab_report': ['insurance_claim'],
            'insurance_form': ['insurance_claim'],
            'prescription': ['patient_intake']
        }
        
        document_type = classification.get('document_type', 'unknown')
        suggested_forms = form_suggestions.get(document_type, ['patient_intake'])
        
        return {
            "document_id": document_id,
            "document_type": document_type,
            "specialty": classification.get('specialty', 'general'),
            "confidence": classification.get('confidence', 0),
            "suggested_forms": suggested_forms,
            "available_forms": form_mapper.get_available_forms()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Form suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")