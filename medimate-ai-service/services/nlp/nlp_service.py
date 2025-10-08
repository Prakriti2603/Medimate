"""
Integrated NLP service that combines all medical NLP components.
Main interface for medical text processing, entity extraction, and form auto-fill.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .medical_nlp_engine import MedicalNLPEngine, MedicalEntity
from .medical_terminology import MedicalTerminologyManager
from .medical_codes import MedicalCodeManager, CodeSystem

logger = logging.getLogger(__name__)


class MedicalNLPService:
    """
    Integrated medical NLP service that provides comprehensive
    medical text processing capabilities.
    """
    
    def __init__(self):
        self.nlp_engine = MedicalNLPEngine()
        self.terminology_manager = MedicalTerminologyManager()
        self.code_manager = MedicalCodeManager()
        self.is_initialized = False
        
        # Initialize the service
        asyncio.create_task(self._initialize_service())
    
    async def _initialize_service(self):
        """Initialize all NLP components."""
        try:
            logger.info("Initializing Medical NLP Service...")
            
            # Wait for NLP engine to initialize
            await asyncio.sleep(1)  # Give time for engine initialization
            
            self.is_initialized = True
            logger.info("Medical NLP Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Medical NLP Service: {e}")
    
    async def process_medical_document(self, text: str, document_type: str = None) -> Dict[str, Any]:
        """
        Process a complete medical document and extract all relevant information.
        
        Args:
            text: Medical document text
            document_type: Type of document (optional)
            
        Returns:
            Comprehensive analysis results
        """
        try:
            if not self.is_initialized:
                await self._initialize_service()
            
            start_time = datetime.now()
            
            # Step 1: Basic NLP processing
            nlp_result = await self.nlp_engine.process_medical_text(text)
            
            # Step 2: Enhance entities with terminology normalization
            enhanced_entities = await self._enhance_entities_with_terminology(nlp_result['entities'])
            
            # Step 3: Map entities to medical codes
            code_mappings = await self._map_entities_to_codes(enhanced_entities)
            
            # Step 4: Extract form-fillable fields
            form_fields = await self._extract_form_fields(enhanced_entities, text)
            
            # Step 5: Generate medical insights
            insights = await self._generate_medical_insights(enhanced_entities, code_mappings)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'document_analysis': {
                    'text_length': len(text),
                    'processing_time': processing_time,
                    'document_type': document_type,
                    'confidence': nlp_result['confidence'],
                    'normalized_text': nlp_result['normalized_text']
                },
                'entities': enhanced_entities,
                'medical_codes': code_mappings,
                'form_fields': form_fields,
                'insights': insights,
                'suggestions': await self._generate_suggestions(enhanced_entities, text)
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                'error': str(e),
                'document_analysis': {'processing_time': 0, 'confidence': 0},
                'entities': [],
                'medical_codes': [],
                'form_fields': {},
                'insights': {},
                'suggestions': []
            }
    
    async def _enhance_entities_with_terminology(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance extracted entities with medical terminology normalization."""
        try:
            enhanced_entities = []
            
            for entity in entities:
                enhanced_entity = entity.copy()
                
                # Normalize medical terms
                normalized_term = self.terminology_manager.normalize_term(entity['text'])
                if normalized_term:
                    enhanced_entity['normalized_form'] = normalized_term
                    enhanced_entity['confidence'] *= 1.1  # Boost confidence for recognized terms
                
                # Get medical codes for the entity
                medical_codes = self.terminology_manager.get_medical_codes(entity['text'])
                if medical_codes:
                    enhanced_entity['medical_codes'] = [
                        {
                            'code': code.code,
                            'system': code.system.value,
                            'description': code.description,
                            'category': code.category
                        }
                        for code in medical_codes
                    ]
                
                # Validate medical term
                validation = self.terminology_manager.validate_medical_term(entity['text'])
                enhanced_entity['validation'] = validation
                
                enhanced_entities.append(enhanced_entity)
            
            return enhanced_entities
            
        except Exception as e:
            logger.error(f"Entity enhancement failed: {e}")
            return entities
    
    async def _map_entities_to_codes(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map entities to appropriate medical codes."""
        try:
            code_mappings = []
            
            for entity in entities:
                entity_text = entity.get('normalized_form', entity['text'])
                entity_label = entity['label']
                
                # Determine appropriate coding system based on entity type
                if entity_label in ['CONDITIONS', 'DIAGNOSIS', 'SYMPTOM']:
                    # Use ICD-10 for diagnoses
                    code_suggestions = self.code_manager.suggest_codes_for_text(
                        entity_text, context='diagnosis'
                    )
                    
                    for suggestion in code_suggestions[:3]:  # Top 3 suggestions
                        if suggestion['system'] == 'ICD-10-CM':
                            code_mappings.append({
                                'entity_text': entity['text'],
                                'entity_label': entity_label,
                                'code': suggestion['code'],
                                'system': suggestion['system'],
                                'description': suggestion['description'],
                                'confidence': suggestion['confidence'] * entity['confidence'],
                                'mapping_type': 'diagnosis'
                            })
                
                elif entity_label in ['PROCEDURE', 'TREATMENT']:
                    # Use CPT for procedures
                    code_suggestions = self.code_manager.suggest_codes_for_text(
                        entity_text, context='procedure'
                    )
                    
                    for suggestion in code_suggestions[:2]:
                        if suggestion['system'] == 'CPT':
                            code_mappings.append({
                                'entity_text': entity['text'],
                                'entity_label': entity_label,
                                'code': suggestion['code'],
                                'system': suggestion['system'],
                                'description': suggestion['description'],
                                'confidence': suggestion['confidence'] * entity['confidence'],
                                'mapping_type': 'procedure'
                            })
                
                elif entity_label in ['MEDICATIONS', 'MEDICATION']:
                    # Use RxNorm for medications (if available)
                    code_suggestions = self.code_manager.suggest_codes_for_text(
                        entity_text, context='medication'
                    )
                    
                    for suggestion in code_suggestions[:2]:
                        code_mappings.append({
                            'entity_text': entity['text'],
                            'entity_label': entity_label,
                            'code': suggestion['code'],
                            'system': suggestion['system'],
                            'description': suggestion['description'],
                            'confidence': suggestion['confidence'] * entity['confidence'],
                            'mapping_type': 'medication'
                        })
            
            return code_mappings
            
        except Exception as e:
            logger.error(f"Code mapping failed: {e}")
            return []
    
    async def _extract_form_fields(self, entities: List[Dict[str, Any]], text: str) -> Dict[str, Any]:
        """Extract fields suitable for medical form auto-fill."""
        try:
            form_fields = {
                'patient_demographics': {},
                'medical_history': {},
                'current_visit': {},
                'medications': [],
                'vital_signs': {},
                'insurance_info': {},
                'provider_info': {}
            }
            
            for entity in entities:
                entity_label = entity['label']
                entity_text = entity['text']
                confidence = entity['confidence']
                
                # Patient demographics
                if entity_label == 'PATIENT_NAME':
                    form_fields['patient_demographics']['name'] = {
                        'value': entity_text,
                        'confidence': confidence
                    }
                elif entity_label == 'AGE':
                    form_fields['patient_demographics']['age'] = {
                        'value': entity_text,
                        'confidence': confidence
                    }
                elif entity_label == 'DATE_OF_BIRTH':
                    form_fields['patient_demographics']['date_of_birth'] = {
                        'value': entity_text,
                        'confidence': confidence
                    }
                
                # Medical conditions
                elif entity_label in ['CONDITIONS', 'DIAGNOSIS']:
                    if 'primary_diagnosis' not in form_fields['medical_history']:
                        form_fields['medical_history']['primary_diagnosis'] = {
                            'value': entity.get('normalized_form', entity_text),
                            'confidence': confidence,
                            'codes': entity.get('medical_codes', [])
                        }
                    else:
                        # Add as secondary diagnosis
                        if 'secondary_diagnoses' not in form_fields['medical_history']:
                            form_fields['medical_history']['secondary_diagnoses'] = []
                        form_fields['medical_history']['secondary_diagnoses'].append({
                            'value': entity.get('normalized_form', entity_text),
                            'confidence': confidence,
                            'codes': entity.get('medical_codes', [])
                        })
                
                # Medications
                elif entity_label in ['MEDICATIONS', 'MEDICATION']:
                    medication_info = {
                        'name': entity.get('normalized_form', entity_text),
                        'confidence': confidence
                    }
                    
                    # Look for dosage information nearby
                    dosage_entities = [e for e in entities if e['label'] == 'DOSAGE']
                    for dosage in dosage_entities:
                        if abs(dosage['start'] - entity['end']) < 50:  # Within 50 characters
                            medication_info['dosage'] = {
                                'value': dosage['text'],
                                'confidence': dosage['confidence']
                            }
                            break
                    
                    form_fields['medications'].append(medication_info)
                
                # Vital signs
                elif entity_label == 'BLOOD_PRESSURE':
                    form_fields['vital_signs']['blood_pressure'] = {
                        'value': entity_text,
                        'confidence': confidence
                    }
                elif entity_label == 'TEMPERATURE':
                    form_fields['vital_signs']['temperature'] = {
                        'value': entity_text,
                        'confidence': confidence
                    }
                
                # Insurance information
                elif entity_label == 'INSURANCE_ID':
                    form_fields['insurance_info']['policy_number'] = {
                        'value': entity_text,
                        'confidence': confidence
                    }
            
            return form_fields
            
        except Exception as e:
            logger.error(f"Form field extraction failed: {e}")
            return {}
    
    async def _generate_medical_insights(self, entities: List[Dict[str, Any]], 
                                       code_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate medical insights from extracted information."""
        try:
            insights = {
                'entity_summary': {},
                'code_summary': {},
                'clinical_notes': [],
                'risk_factors': [],
                'recommendations': []
            }
            
            # Entity summary
            entity_counts = {}
            for entity in entities:
                label = entity['label']
                entity_counts[label] = entity_counts.get(label, 0) + 1
            
            insights['entity_summary'] = entity_counts
            
            # Code summary
            code_systems = {}
            for mapping in code_mappings:
                system = mapping['system']
                code_systems[system] = code_systems.get(system, 0) + 1
            
            insights['code_summary'] = code_systems
            
            # Clinical notes
            if 'CONDITIONS' in entity_counts or 'DIAGNOSIS' in entity_counts:
                insights['clinical_notes'].append(
                    f"Document contains {entity_counts.get('CONDITIONS', 0) + entity_counts.get('DIAGNOSIS', 0)} diagnostic entities"
                )
            
            if 'MEDICATIONS' in entity_counts:
                insights['clinical_notes'].append(
                    f"Document mentions {entity_counts['MEDICATIONS']} medications"
                )
            
            # Risk factors (simplified)
            high_risk_conditions = ['diabetes', 'hypertension', 'heart disease', 'stroke']
            for entity in entities:
                entity_text_lower = entity['text'].lower()
                for condition in high_risk_conditions:
                    if condition in entity_text_lower:
                        insights['risk_factors'].append({
                            'condition': condition,
                            'confidence': entity['confidence'],
                            'recommendation': f'Monitor {condition} closely'
                        })
            
            # Recommendations
            if len(code_mappings) > 0:
                insights['recommendations'].append('Review suggested medical codes for accuracy')
            
            if len(entities) > 10:
                insights['recommendations'].append('Complex case - consider specialist consultation')
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return {}
    
    async def _generate_suggestions(self, entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """Generate suggestions for improving documentation or coding."""
        try:
            suggestions = []
            
            # Check for missing information
            has_patient_name = any(e['label'] == 'PATIENT_NAME' for e in entities)
            has_diagnosis = any(e['label'] in ['CONDITIONS', 'DIAGNOSIS'] for e in entities)
            has_age = any(e['label'] == 'AGE' for e in entities)
            
            if not has_patient_name:
                suggestions.append({
                    'type': 'missing_info',
                    'message': 'Patient name not clearly identified',
                    'priority': 'high'
                })
            
            if not has_diagnosis:
                suggestions.append({
                    'type': 'missing_info',
                    'message': 'No clear diagnosis found',
                    'priority': 'high'
                })
            
            if not has_age:
                suggestions.append({
                    'type': 'missing_info',
                    'message': 'Patient age not specified',
                    'priority': 'medium'
                })
            
            # Check for low confidence entities
            low_confidence_entities = [e for e in entities if e['confidence'] < 0.7]
            if low_confidence_entities:
                suggestions.append({
                    'type': 'low_confidence',
                    'message': f'{len(low_confidence_entities)} entities have low confidence scores',
                    'priority': 'medium',
                    'entities': [e['text'] for e in low_confidence_entities[:3]]
                })
            
            # Check for abbreviations that could be expanded
            abbreviations_found = []
            for word in text.split():
                clean_word = word.lower().strip('.,!?;:')
                if clean_word in self.terminology_manager.abbreviations:
                    abbreviations_found.append(clean_word)
            
            if abbreviations_found:
                suggestions.append({
                    'type': 'abbreviations',
                    'message': f'Consider expanding abbreviations: {", ".join(abbreviations_found[:5])}',
                    'priority': 'low'
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []
    
    async def auto_fill_form(self, text: str, form_template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically fill a medical form based on extracted information.
        
        Args:
            text: Medical document text
            form_template: Form template with field definitions
            
        Returns:
            Filled form with confidence scores
        """
        try:
            # Process the document
            analysis = await self.process_medical_document(text)
            form_fields = analysis['form_fields']
            
            filled_form = {}
            
            # Map extracted fields to form template
            for field_name, field_config in form_template.items():
                field_type = field_config.get('type', 'text')
                field_category = field_config.get('category', '')
                
                # Try to find matching extracted field
                filled_value = None
                confidence = 0.0
                
                if field_category == 'demographics':
                    if field_name in form_fields.get('patient_demographics', {}):
                        field_data = form_fields['patient_demographics'][field_name]
                        filled_value = field_data['value']
                        confidence = field_data['confidence']
                
                elif field_category == 'medical':
                    if field_name in form_fields.get('medical_history', {}):
                        field_data = form_fields['medical_history'][field_name]
                        filled_value = field_data['value']
                        confidence = field_data['confidence']
                
                elif field_category == 'medications':
                    if form_fields.get('medications'):
                        # For medication fields, use the first medication
                        med_data = form_fields['medications'][0]
                        filled_value = med_data['name']
                        confidence = med_data['confidence']
                
                elif field_category == 'vitals':
                    if field_name in form_fields.get('vital_signs', {}):
                        field_data = form_fields['vital_signs'][field_name]
                        filled_value = field_data['value']
                        confidence = field_data['confidence']
                
                filled_form[field_name] = {
                    'value': filled_value,
                    'confidence': confidence,
                    'auto_filled': filled_value is not None,
                    'requires_review': confidence < 0.8
                }
            
            return {
                'filled_form': filled_form,
                'overall_confidence': sum(f['confidence'] for f in filled_form.values() if f['value']) / len([f for f in filled_form.values() if f['value']]) if any(f['value'] for f in filled_form.values()) else 0,
                'fields_filled': len([f for f in filled_form.values() if f['value']]),
                'total_fields': len(filled_form),
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Auto-fill failed: {e}")
            return {
                'filled_form': {},
                'overall_confidence': 0,
                'fields_filled': 0,
                'total_fields': 0,
                'error': str(e)
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of the NLP service."""
        try:
            return {
                'is_initialized': self.is_initialized,
                'nlp_engine_available': self.nlp_engine is not None,
                'terminology_stats': self.terminology_manager.get_statistics(),
                'code_stats': self.code_manager.get_statistics(),
                'capabilities': [
                    'medical_entity_extraction',
                    'terminology_normalization',
                    'medical_code_mapping',
                    'form_auto_fill',
                    'clinical_insights'
                ]
            }
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                'is_initialized': False,
                'error': str(e)
            }