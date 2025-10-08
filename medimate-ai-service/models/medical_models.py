"""
Medical AI models for document classification, NER, and field extraction.
"""

import logging
import json
import pickle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class MedicalDocumentClassifier:
    """Classify medical documents by type and specialty."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.is_trained = False
        self.model_path = model_path
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Document type categories
        self.document_types = [
            'discharge_summary',
            'progress_note',
            'consultation_report',
            'lab_report',
            'radiology_report',
            'prescription',
            'insurance_form',
            'consent_form'
        ]
        
        # Medical specialties
        self.specialties = [
            'cardiology',
            'neurology',
            'orthopedics',
            'pediatrics',
            'emergency',
            'internal_medicine',
            'surgery',
            'radiology'
        ]
        
        if model_path and Path(model_path).exists():
            asyncio.create_task(self._load_model())
    
    async def _load_model(self):
        """Load pre-trained model."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self._load_model_sync)
            logger.info("Medical document classifier loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load classifier model: {e}")
    
    def _load_model_sync(self):
        """Synchronous model loading."""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.label_encoder = model_data['label_encoder']
            self.is_trained = True
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise
    
    async def classify_document(self, text: str) -> Dict[str, Any]:
        """
        Classify a medical document.
        
        Args:
            text: Document text
            
        Returns:
            Classification results with confidence scores
        """
        try:
            if not self.is_trained:
                # Use rule-based classification as fallback
                return await self._rule_based_classification(text)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self._classify_sync, text
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Document classification failed: {e}")
            return {
                'document_type': 'unknown',
                'specialty': 'general',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _classify_sync(self, text: str) -> Dict[str, Any]:
        """Synchronous classification."""
        try:
            # Vectorize text
            text_vector = self.vectorizer.transform([text])
            
            # Predict
            prediction = self.model.predict(text_vector)[0]
            probabilities = self.model.predict_proba(text_vector)[0]
            
            # Decode prediction
            predicted_label = self.label_encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities)
            
            # Parse label (format: "document_type|specialty")
            if '|' in predicted_label:
                document_type, specialty = predicted_label.split('|', 1)
            else:
                document_type = predicted_label
                specialty = 'general'
            
            return {
                'document_type': document_type,
                'specialty': specialty,
                'confidence': float(confidence),
                'all_probabilities': {
                    self.label_encoder.inverse_transform([i])[0]: float(prob)
                    for i, prob in enumerate(probabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"Synchronous classification failed: {e}")
            raise
    
    async def _rule_based_classification(self, text: str) -> Dict[str, Any]:
        """Rule-based classification fallback."""
        try:
            text_lower = text.lower()
            
            # Document type keywords
            type_keywords = {
                'discharge_summary': ['discharge', 'summary', 'hospital course', 'disposition'],
                'progress_note': ['progress', 'soap', 'assessment', 'plan'],
                'consultation_report': ['consultation', 'consult', 'referred', 'opinion'],
                'lab_report': ['laboratory', 'lab results', 'blood work', 'urinalysis'],
                'radiology_report': ['x-ray', 'ct scan', 'mri', 'ultrasound', 'radiology'],
                'prescription': ['prescription', 'medication', 'rx', 'dispense'],
                'insurance_form': ['insurance', 'claim', 'policy', 'coverage'],
                'consent_form': ['consent', 'authorization', 'permission', 'agree']
            }
            
            # Specialty keywords
            specialty_keywords = {
                'cardiology': ['heart', 'cardiac', 'cardio', 'chest pain', 'hypertension'],
                'neurology': ['brain', 'neurological', 'headache', 'seizure', 'stroke'],
                'orthopedics': ['bone', 'fracture', 'joint', 'orthopedic', 'musculoskeletal'],
                'pediatrics': ['pediatric', 'child', 'infant', 'adolescent'],
                'emergency': ['emergency', 'trauma', 'urgent', 'acute'],
                'internal_medicine': ['internal medicine', 'primary care', 'general'],
                'surgery': ['surgical', 'operation', 'procedure', 'incision'],
                'radiology': ['imaging', 'scan', 'x-ray', 'radiology']
            }
            
            # Score document types
            type_scores = {}
            for doc_type, keywords in type_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    type_scores[doc_type] = score / len(keywords)
            
            # Score specialties
            specialty_scores = {}
            for specialty, keywords in specialty_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    specialty_scores[specialty] = score / len(keywords)
            
            # Determine best matches
            best_type = max(type_scores.items(), key=lambda x: x[1]) if type_scores else ('unknown', 0)
            best_specialty = max(specialty_scores.items(), key=lambda x: x[1]) if specialty_scores else ('general', 0)
            
            return {
                'document_type': best_type[0],
                'specialty': best_specialty[0],
                'confidence': (best_type[1] + best_specialty[1]) / 2,
                'method': 'rule_based',
                'type_scores': type_scores,
                'specialty_scores': specialty_scores
            }
            
        except Exception as e:
            logger.error(f"Rule-based classification failed: {e}")
            return {
                'document_type': 'unknown',
                'specialty': 'general',
                'confidence': 0.0,
                'error': str(e)
            }


class MedicalFieldExtractor:
    """Extract specific fields from medical documents for form auto-fill."""
    
    def __init__(self):
        self.field_patterns = self._initialize_field_patterns()
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _initialize_field_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for field extraction."""
        return {
            'patient_name': [
                r'Patient:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'Name:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(?:age|DOB|born)'
            ],
            'date_of_birth': [
                r'DOB:?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Date of Birth:?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Born:?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ],
            'age': [
                r'age:?\s+(\d{1,3})',
                r'(\d{1,3})\s*(?:year|yr|y)[\s-]*old',
                r'(\d{1,3})\s*yo'
            ],
            'medical_record_number': [
                r'MRN:?\s+(\d+)',
                r'Medical Record:?\s+(\d+)',
                r'Record #:?\s+(\d+)'
            ],
            'insurance_id': [
                r'Insurance:?\s+([A-Z0-9]+)',
                r'Policy:?\s+([A-Z0-9]+)',
                r'Member ID:?\s+([A-Z0-9]+)'
            ],
            'primary_diagnosis': [
                r'Primary Diagnosis:?\s+([^\n\r]+)',
                r'Diagnosis:?\s+([^\n\r]+)',
                r'Impression:?\s+([^\n\r]+)'
            ],
            'chief_complaint': [
                r'Chief Complaint:?\s+([^\n\r]+)',
                r'CC:?\s+([^\n\r]+)',
                r'Presenting complaint:?\s+([^\n\r]+)'
            ],
            'medications': [
                r'Medications?:?\s*\n((?:[^\n]+\n?)+?)(?:\n\s*\n|\n[A-Z]|\Z)',
                r'Current Meds:?\s*\n((?:[^\n]+\n?)+?)(?:\n\s*\n|\n[A-Z]|\Z)',
                r'Rx:?\s*\n((?:[^\n]+\n?)+?)(?:\n\s*\n|\n[A-Z]|\Z)'
            ],
            'allergies': [
                r'Allergies:?\s+([^\n\r]+)',
                r'Drug Allergies:?\s+([^\n\r]+)',
                r'NKDA|No known drug allergies'
            ],
            'blood_pressure': [
                r'BP:?\s+(\d{2,3}/\d{2,3})',
                r'Blood Pressure:?\s+(\d{2,3}/\d{2,3})',
                r'(\d{2,3}/\d{2,3})\s*mmHg'
            ],
            'heart_rate': [
                r'HR:?\s+(\d{2,3})',
                r'Heart Rate:?\s+(\d{2,3})',
                r'Pulse:?\s+(\d{2,3})'
            ],
            'temperature': [
                r'Temp:?\s+(\d{2,3}(?:\.\d)?)\s*°?[FC]',
                r'Temperature:?\s+(\d{2,3}(?:\.\d)?)\s*°?[FC]',
                r'(\d{2,3}(?:\.\d)?)\s*°[FC]'
            ],
            'weight': [
                r'Weight:?\s+(\d{2,3}(?:\.\d)?)\s*(?:lbs?|kg)',
                r'Wt:?\s+(\d{2,3}(?:\.\d)?)\s*(?:lbs?|kg)',
                r'(\d{2,3}(?:\.\d)?)\s*(?:lbs?|kg)'
            ],
            'height': [
                r'Height:?\s+(\d+\'?\s*\d*"?|\d+\s*(?:cm|in))',
                r'Ht:?\s+(\d+\'?\s*\d*"?|\d+\s*(?:cm|in))',
                r'(\d+\'?\s*\d*"?)\s*tall'
            ]
        }
    
    async def extract_fields(self, text: str, field_types: List[str] = None) -> Dict[str, Any]:
        """
        Extract specified fields from medical text.
        
        Args:
            text: Medical document text
            field_types: List of field types to extract (None for all)
            
        Returns:
            Extracted fields with confidence scores
        """
        try:
            if field_types is None:
                field_types = list(self.field_patterns.keys())
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self._extract_fields_sync, text, field_types
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            return {'extracted_fields': {}, 'error': str(e)}
    
    def _extract_fields_sync(self, text: str, field_types: List[str]) -> Dict[str, Any]:
        """Synchronous field extraction."""
        import re
        
        try:
            extracted_fields = {}
            
            for field_type in field_types:
                if field_type not in self.field_patterns:
                    continue
                
                patterns = self.field_patterns[field_type]
                field_matches = []
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        value = match.group(1).strip() if match.groups() else match.group().strip()
                        
                        # Clean up the value
                        value = self._clean_field_value(value, field_type)
                        
                        if value:
                            field_matches.append({
                                'value': value,
                                'confidence': self._calculate_field_confidence(match, pattern, text),
                                'start_pos': match.start(),
                                'end_pos': match.end(),
                                'pattern_used': pattern
                            })
                
                # Select best match for this field
                if field_matches:
                    best_match = max(field_matches, key=lambda x: x['confidence'])
                    extracted_fields[field_type] = best_match
            
            return {
                'extracted_fields': extracted_fields,
                'total_fields_found': len(extracted_fields),
                'extraction_method': 'pattern_based'
            }
            
        except Exception as e:
            logger.error(f"Synchronous field extraction failed: {e}")
            raise
    
    def _clean_field_value(self, value: str, field_type: str) -> str:
        """Clean and normalize extracted field values."""
        try:
            value = value.strip()
            
            if field_type == 'patient_name':
                # Remove titles and suffixes
                value = re.sub(r'\b(?:Mr|Mrs|Ms|Dr|MD|RN|Jr|Sr)\.?\b', '', value, flags=re.IGNORECASE)
                value = ' '.join(value.split())  # Normalize whitespace
            
            elif field_type in ['date_of_birth']:
                # Normalize date format
                value = re.sub(r'[/-]', '/', value)
            
            elif field_type == 'age':
                # Extract just the number
                age_match = re.search(r'\d+', value)
                value = age_match.group() if age_match else value
            
            elif field_type in ['medications', 'allergies']:
                # Clean medication lists
                lines = [line.strip() for line in value.split('\n') if line.strip()]
                value = '\n'.join(lines)
            
            elif field_type in ['primary_diagnosis', 'chief_complaint']:
                # Remove trailing punctuation and normalize
                value = re.sub(r'[.,:;]+$', '', value)
            
            return value.strip()
            
        except Exception as e:
            logger.error(f"Field value cleaning failed: {e}")
            return value
    
    def _calculate_field_confidence(self, match, pattern: str, text: str) -> float:
        """Calculate confidence score for extracted field."""
        try:
            base_confidence = 0.8
            
            # Boost confidence for exact label matches
            if ':' in pattern:
                base_confidence += 0.1
            
            # Boost confidence for specific patterns
            if 'Patient:' in pattern or 'Name:' in pattern:
                base_confidence += 0.1
            
            # Reduce confidence for very short matches
            match_text = match.group()
            if len(match_text) < 3:
                base_confidence -= 0.2
            
            # Boost confidence for matches near document start
            if match.start() < len(text) * 0.2:  # First 20% of document
                base_confidence += 0.05
            
            return min(1.0, max(0.1, base_confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5


class MedicalFormMapper:
    """Map extracted medical information to specific form templates."""
    
    def __init__(self):
        self.form_templates = self._load_form_templates()
        self.field_mappings = self._initialize_field_mappings()
    
    def _load_form_templates(self) -> Dict[str, Dict]:
        """Load standard medical form templates."""
        return {
            'patient_intake': {
                'fields': {
                    'patient_name': {'required': True, 'type': 'text'},
                    'date_of_birth': {'required': True, 'type': 'date'},
                    'age': {'required': False, 'type': 'number'},
                    'insurance_id': {'required': True, 'type': 'text'},
                    'chief_complaint': {'required': True, 'type': 'textarea'},
                    'medications': {'required': False, 'type': 'textarea'},
                    'allergies': {'required': False, 'type': 'text'}
                }
            },
            'discharge_summary': {
                'fields': {
                    'patient_name': {'required': True, 'type': 'text'},
                    'medical_record_number': {'required': True, 'type': 'text'},
                    'primary_diagnosis': {'required': True, 'type': 'text'},
                    'medications': {'required': True, 'type': 'textarea'},
                    'discharge_instructions': {'required': True, 'type': 'textarea'}
                }
            },
            'insurance_claim': {
                'fields': {
                    'patient_name': {'required': True, 'type': 'text'},
                    'date_of_birth': {'required': True, 'type': 'date'},
                    'insurance_id': {'required': True, 'type': 'text'},
                    'primary_diagnosis': {'required': True, 'type': 'text'},
                    'procedure_codes': {'required': False, 'type': 'text'},
                    'provider_name': {'required': True, 'type': 'text'}
                }
            }
        }
    
    def _initialize_field_mappings(self) -> Dict[str, List[str]]:
        """Initialize mappings between extracted fields and form fields."""
        return {
            'patient_name': ['patient_name', 'name', 'full_name'],
            'date_of_birth': ['date_of_birth', 'dob', 'birth_date'],
            'age': ['age', 'patient_age'],
            'medical_record_number': ['mrn', 'medical_record_number', 'record_number'],
            'insurance_id': ['insurance_id', 'policy_number', 'member_id'],
            'primary_diagnosis': ['primary_diagnosis', 'diagnosis', 'main_diagnosis'],
            'chief_complaint': ['chief_complaint', 'complaint', 'presenting_problem'],
            'medications': ['medications', 'current_medications', 'meds'],
            'allergies': ['allergies', 'drug_allergies', 'known_allergies']
        }
    
    async def map_to_form(self, extracted_fields: Dict[str, Any], 
                         form_type: str) -> Dict[str, Any]:
        """
        Map extracted fields to a specific form template.
        
        Args:
            extracted_fields: Fields extracted from document
            form_type: Type of form to map to
            
        Returns:
            Mapped form data with validation results
        """
        try:
            if form_type not in self.form_templates:
                raise ValueError(f"Unknown form type: {form_type}")
            
            template = self.form_templates[form_type]
            mapped_form = {}
            validation_results = {
                'is_valid': True,
                'missing_required': [],
                'field_warnings': [],
                'confidence_scores': {}
            }
            
            # Map each template field
            for form_field, field_config in template['fields'].items():
                mapped_value = None
                confidence = 0.0
                
                # Find matching extracted field
                for extracted_field, extracted_data in extracted_fields.items():
                    if self._fields_match(extracted_field, form_field):
                        mapped_value = extracted_data['value']
                        confidence = extracted_data['confidence']
                        break
                
                # Store mapped field
                mapped_form[form_field] = {
                    'value': mapped_value,
                    'confidence': confidence,
                    'required': field_config['required'],
                    'type': field_config['type'],
                    'auto_filled': mapped_value is not None
                }
                
                # Validation
                if field_config['required'] and not mapped_value:
                    validation_results['missing_required'].append(form_field)
                    validation_results['is_valid'] = False
                
                if mapped_value and confidence < 0.7:
                    validation_results['field_warnings'].append({
                        'field': form_field,
                        'message': 'Low confidence extraction',
                        'confidence': confidence
                    })
                
                validation_results['confidence_scores'][form_field] = confidence
            
            # Calculate overall form completion
            filled_fields = len([f for f in mapped_form.values() if f['value']])
            total_fields = len(mapped_form)
            completion_rate = filled_fields / total_fields if total_fields > 0 else 0
            
            return {
                'form_type': form_type,
                'mapped_fields': mapped_form,
                'validation': validation_results,
                'completion_rate': completion_rate,
                'fields_filled': filled_fields,
                'total_fields': total_fields
            }
            
        except Exception as e:
            logger.error(f"Form mapping failed: {e}")
            return {
                'form_type': form_type,
                'mapped_fields': {},
                'validation': {'is_valid': False, 'error': str(e)},
                'completion_rate': 0,
                'fields_filled': 0,
                'total_fields': 0
            }
    
    def _fields_match(self, extracted_field: str, form_field: str) -> bool:
        """Check if extracted field matches form field."""
        if extracted_field == form_field:
            return True
        
        if extracted_field in self.field_mappings:
            return form_field in self.field_mappings[extracted_field]
        
        return False
    
    def get_available_forms(self) -> List[str]:
        """Get list of available form templates."""
        return list(self.form_templates.keys())
    
    def get_form_template(self, form_type: str) -> Dict[str, Any]:
        """Get form template definition."""
        return self.form_templates.get(form_type, {})