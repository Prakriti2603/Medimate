"""
Medical NLP processing engine for entity recognition and terminology processing.
Handles medical text analysis, entity extraction, and medical code mapping.
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Medical NLP libraries (will be imported when available)
try:
    import spacy
    from spacy.matcher import Matcher, PhraseMatcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available. Medical NLP will use fallback methods.")

from config.settings import settings

logger = logging.getLogger(__name__)


class MedicalEntity:
    """Represents a medical entity extracted from text."""
    
    def __init__(self, text: str, label: str, start: int, end: int, 
                 confidence: float = 1.0, normalized_form: str = None,
                 medical_codes: List[Dict] = None):
        self.text = text
        self.label = label
        self.start = start
        self.end = end
        self.confidence = confidence
        self.normalized_form = normalized_form or text
        self.medical_codes = medical_codes or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            'text': self.text,
            'label': self.label,
            'start': self.start,
            'end': self.end,
            'confidence': self.confidence,
            'normalized_form': self.normalized_form,
            'medical_codes': self.medical_codes
        }


class MedicalNLPEngine:
    """Main medical NLP processing engine."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.nlp_model = None
        self.matcher = None
        self.phrase_matcher = None
        self.medical_terminology = {}
        self.abbreviations = {}
        self.medical_codes = {}
        
        # Initialize the engine
        asyncio.create_task(self._initialize_engine())
    
    async def _initialize_engine(self):
        """Initialize the NLP engine with medical models and terminology."""
        try:
            if SPACY_AVAILABLE:
                await self._load_spacy_models()
            
            await self._load_medical_terminology()
            await self._load_medical_abbreviations()
            await self._load_medical_codes()
            
            logger.info("Medical NLP engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize medical NLP engine: {e}")
            # Continue with fallback methods
    
    async def _load_spacy_models(self):
        """Load spaCy models for medical NLP."""
        try:
            # Try to load medical-specific models first
            model_names = [
                'en_core_sci_sm',  # Scientific/medical model
                'en_core_web_sm',  # General English model
                'en_core_web_md'   # Medium English model
            ]
            
            for model_name in model_names:
                try:
                    self.nlp_model = spacy.load(model_name)
                    logger.info(f"Loaded spaCy model: {model_name}")
                    break
                except OSError:
                    continue
            
            if self.nlp_model is None:
                logger.warning("No spaCy models available. Using fallback NLP methods.")
                return
            
            # Initialize matchers
            self.matcher = Matcher(self.nlp_model.vocab)
            self.phrase_matcher = PhraseMatcher(self.nlp_model.vocab, attr="LOWER")
            
            # Add medical patterns
            await self._add_medical_patterns()
            
        except Exception as e:
            logger.error(f"Failed to load spaCy models: {e}")
    
    async def _add_medical_patterns(self):
        """Add medical-specific patterns to matchers."""
        try:
            # Medication patterns
            medication_patterns = [
                [{"LOWER": {"REGEX": r".*mg$"}},],  # Dosage patterns
                [{"LOWER": {"REGEX": r".*ml$"}},],
                [{"LOWER": {"REGEX": r".*mcg$"}},],
                [{"LOWER": {"IN": ["tablet", "tablets", "capsule", "capsules"]}},],
                [{"LOWER": {"IN": ["twice", "once", "thrice"]}}, {"LOWER": "daily"}],
                [{"LOWER": {"REGEX": r"\d+"}}, {"LOWER": "times"}, {"LOWER": {"IN": ["daily", "weekly"]}}],
            ]
            
            for i, pattern in enumerate(medication_patterns):
                self.matcher.add(f"MEDICATION_PATTERN_{i}", [pattern])
            
            # Vital signs patterns
            vital_patterns = [
                [{"LOWER": {"REGEX": r"\d+"}}, {"LOWER": "/"}, {"LOWER": {"REGEX": r"\d+"}}],  # Blood pressure
                [{"LOWER": {"REGEX": r"\d+"}}, {"LOWER": {"IN": ["bpm", "beats"]}},],  # Heart rate
                [{"LOWER": {"REGEX": r"\d+\.?\d*"}}, {"LOWER": {"IN": ["°f", "°c", "degrees"]}},],  # Temperature
            ]
            
            for i, pattern in enumerate(vital_patterns):
                self.matcher.add(f"VITAL_SIGNS_PATTERN_{i}", [pattern])
            
            logger.info("Medical patterns added to matchers")
            
        except Exception as e:
            logger.error(f"Failed to add medical patterns: {e}")
    
    async def _load_medical_terminology(self):
        """Load medical terminology database."""
        try:
            # Load from file or create basic terminology
            terminology_path = Path(__file__).parent / "data" / "medical_terminology.json"
            
            if terminology_path.exists():
                with open(terminology_path, 'r', encoding='utf-8') as f:
                    self.medical_terminology = json.load(f)
            else:
                # Create basic medical terminology
                self.medical_terminology = {
                    "conditions": {
                        "hypertension": ["high blood pressure", "htn", "elevated bp"],
                        "diabetes": ["diabetes mellitus", "dm", "diabetic"],
                        "myocardial infarction": ["heart attack", "mi", "cardiac arrest"],
                        "pneumonia": ["lung infection", "respiratory infection"],
                        "fracture": ["broken bone", "break", "fx"],
                        "migraine": ["severe headache", "headache"],
                        "asthma": ["breathing difficulty", "wheezing"],
                        "depression": ["depressive disorder", "mood disorder"]
                    },
                    "medications": {
                        "metformin": ["glucophage", "fortamet"],
                        "lisinopril": ["prinivil", "zestril"],
                        "atorvastatin": ["lipitor"],
                        "metoprolol": ["lopressor", "toprol"],
                        "amlodipine": ["norvasc"],
                        "omeprazole": ["prilosec"],
                        "levothyroxine": ["synthroid"],
                        "albuterol": ["proventil", "ventolin"]
                    },
                    "body_parts": {
                        "chest": ["thorax", "thoracic"],
                        "abdomen": ["belly", "abdominal", "stomach"],
                        "head": ["cranium", "cranial"],
                        "heart": ["cardiac", "cardio"],
                        "lung": ["pulmonary", "respiratory"],
                        "kidney": ["renal", "nephro"],
                        "liver": ["hepatic", "hepato"]
                    }
                }
            
            logger.info(f"Loaded medical terminology: {len(self.medical_terminology)} categories")
            
        except Exception as e:
            logger.error(f"Failed to load medical terminology: {e}")
    
    async def _load_medical_abbreviations(self):
        """Load medical abbreviations dictionary."""
        try:
            # Common medical abbreviations
            self.abbreviations = {
                # Vital signs
                "bp": "blood pressure",
                "hr": "heart rate",
                "rr": "respiratory rate",
                "temp": "temperature",
                "o2sat": "oxygen saturation",
                "bmi": "body mass index",
                
                # Conditions
                "htn": "hypertension",
                "dm": "diabetes mellitus",
                "mi": "myocardial infarction",
                "copd": "chronic obstructive pulmonary disease",
                "chf": "congestive heart failure",
                "afib": "atrial fibrillation",
                "cad": "coronary artery disease",
                "ckd": "chronic kidney disease",
                
                # Medications
                "asa": "aspirin",
                "acei": "ace inhibitor",
                "arb": "angiotensin receptor blocker",
                "ppi": "proton pump inhibitor",
                "nsaid": "nonsteroidal anti-inflammatory drug",
                
                # Units
                "mg": "milligrams",
                "ml": "milliliters",
                "mcg": "micrograms",
                "iu": "international units",
                "bid": "twice daily",
                "tid": "three times daily",
                "qid": "four times daily",
                "prn": "as needed",
                
                # Time
                "qd": "once daily",
                "qod": "every other day",
                "qhs": "at bedtime",
                "ac": "before meals",
                "pc": "after meals",
                
                # Routes
                "po": "by mouth",
                "iv": "intravenous",
                "im": "intramuscular",
                "sq": "subcutaneous",
                "sl": "sublingual",
                "pr": "per rectum"
            }
            
            logger.info(f"Loaded {len(self.abbreviations)} medical abbreviations")
            
        except Exception as e:
            logger.error(f"Failed to load medical abbreviations: {e}")
    
    async def _load_medical_codes(self):
        """Load medical coding systems (ICD-10, CPT, etc.)."""
        try:
            # Basic medical codes - in production, this would be a comprehensive database
            self.medical_codes = {
                "icd10": {
                    "I10": {"description": "Essential hypertension", "category": "cardiovascular"},
                    "E11": {"description": "Type 2 diabetes mellitus", "category": "endocrine"},
                    "I21": {"description": "Acute myocardial infarction", "category": "cardiovascular"},
                    "J44": {"description": "Chronic obstructive pulmonary disease", "category": "respiratory"},
                    "N18": {"description": "Chronic kidney disease", "category": "genitourinary"},
                    "F32": {"description": "Major depressive disorder", "category": "mental"},
                    "M79": {"description": "Other soft tissue disorders", "category": "musculoskeletal"},
                    "R50": {"description": "Fever", "category": "symptoms"}
                },
                "cpt": {
                    "99213": {"description": "Office visit, established patient", "category": "evaluation"},
                    "99214": {"description": "Office visit, established patient, detailed", "category": "evaluation"},
                    "93000": {"description": "Electrocardiogram", "category": "diagnostic"},
                    "80053": {"description": "Comprehensive metabolic panel", "category": "laboratory"},
                    "85025": {"description": "Complete blood count", "category": "laboratory"},
                    "36415": {"description": "Venipuncture", "category": "procedure"}
                }
            }
            
            logger.info(f"Loaded medical codes: {len(self.medical_codes)} systems")
            
        except Exception as e:
            logger.error(f"Failed to load medical codes: {e}")
    
    async def process_medical_text(self, text: str) -> Dict[str, Any]:
        """
        Process medical text and extract entities, terminology, and codes.
        
        Args:
            text: Medical text to process
            
        Returns:
            Dictionary containing extracted entities and analysis
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Run processing in executor to avoid blocking
            result = await loop.run_in_executor(
                self.executor, self._process_text_sync, text
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Medical text processing failed: {e}")
            return {
                'entities': [],
                'normalized_text': text,
                'medical_codes': [],
                'confidence': 0.0,
                'processing_time': 0.0
            }
    
    def _process_text_sync(self, text: str) -> Dict[str, Any]:
        """Synchronous text processing implementation."""
        import time
        start_time = time.time()
        
        try:
            entities = []
            normalized_text = text
            medical_codes = []
            
            # Step 1: Expand abbreviations
            normalized_text = self._expand_abbreviations(text)
            
            # Step 2: Extract entities using spaCy (if available)
            if self.nlp_model is not None:
                spacy_entities = self._extract_spacy_entities(normalized_text)
                entities.extend(spacy_entities)
            
            # Step 3: Extract entities using pattern matching
            pattern_entities = self._extract_pattern_entities(normalized_text)
            entities.extend(pattern_entities)
            
            # Step 4: Extract entities using terminology matching
            terminology_entities = self._extract_terminology_entities(normalized_text)
            entities.extend(terminology_entities)
            
            # Step 5: Normalize and deduplicate entities
            entities = self._normalize_entities(entities)
            
            # Step 6: Map to medical codes
            medical_codes = self._map_to_medical_codes(entities)
            
            # Step 7: Calculate overall confidence
            confidence = self._calculate_confidence(entities)
            
            processing_time = time.time() - start_time
            
            return {
                'entities': [entity.to_dict() for entity in entities],
                'normalized_text': normalized_text,
                'medical_codes': medical_codes,
                'confidence': confidence,
                'processing_time': processing_time,
                'entity_count': len(entities),
                'abbreviations_expanded': len(self._find_abbreviations(text))
            }
            
        except Exception as e:
            logger.error(f"Synchronous text processing failed: {e}")
            return {
                'entities': [],
                'normalized_text': text,
                'medical_codes': [],
                'confidence': 0.0,
                'processing_time': time.time() - start_time
            }
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand medical abbreviations in text."""
        try:
            expanded_text = text
            
            # Find and expand abbreviations
            words = text.split()
            expanded_words = []
            
            for word in words:
                # Clean word (remove punctuation for matching)
                clean_word = re.sub(r'[^\w]', '', word.lower())
                
                if clean_word in self.abbreviations:
                    # Replace with expansion, preserving original case and punctuation
                    expansion = self.abbreviations[clean_word]
                    if word.isupper():
                        expansion = expansion.upper()
                    elif word.istitle():
                        expansion = expansion.title()
                    
                    # Preserve punctuation
                    punctuation = re.findall(r'[^\w]', word)
                    if punctuation:
                        expansion += ''.join(punctuation)
                    
                    expanded_words.append(expansion)
                else:
                    expanded_words.append(word)
            
            expanded_text = ' '.join(expanded_words)
            return expanded_text
            
        except Exception as e:
            logger.error(f"Abbreviation expansion failed: {e}")
            return text
    
    def _find_abbreviations(self, text: str) -> List[str]:
        """Find abbreviations in text."""
        found_abbrevs = []
        words = text.split()
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.abbreviations:
                found_abbrevs.append(clean_word)
        
        return found_abbrevs
    
    def _extract_spacy_entities(self, text: str) -> List[MedicalEntity]:
        """Extract entities using spaCy NER."""
        entities = []
        
        try:
            if self.nlp_model is None:
                return entities
            
            doc = self.nlp_model(text)
            
            # Extract named entities
            for ent in doc.ents:
                entity = MedicalEntity(
                    text=ent.text,
                    label=self._map_spacy_label(ent.label_),
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.8  # Default confidence for spaCy entities
                )
                entities.append(entity)
            
            # Extract pattern matches
            if self.matcher is not None:
                matches = self.matcher(doc)
                for match_id, start, end in matches:
                    span = doc[start:end]
                    label = self.nlp_model.vocab.strings[match_id]
                    
                    entity = MedicalEntity(
                        text=span.text,
                        label=self._map_pattern_label(label),
                        start=span.start_char,
                        end=span.end_char,
                        confidence=0.7  # Pattern match confidence
                    )
                    entities.append(entity)
            
        except Exception as e:
            logger.error(f"spaCy entity extraction failed: {e}")
        
        return entities
    
    def _extract_pattern_entities(self, text: str) -> List[MedicalEntity]:
        """Extract entities using regex patterns."""
        entities = []
        
        try:
            # Medication dosage patterns
            dosage_pattern = r'\b(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g|units?)\b'
            for match in re.finditer(dosage_pattern, text, re.IGNORECASE):
                entity = MedicalEntity(
                    text=match.group(),
                    label='DOSAGE',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                )
                entities.append(entity)
            
            # Blood pressure pattern
            bp_pattern = r'\b(\d{2,3})/(\d{2,3})\b'
            for match in re.finditer(bp_pattern, text):
                entity = MedicalEntity(
                    text=match.group(),
                    label='BLOOD_PRESSURE',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95
                )
                entities.append(entity)
            
            # Temperature pattern
            temp_pattern = r'\b(\d{2,3}(?:\.\d)?)\s*°?[FC]\b'
            for match in re.finditer(temp_pattern, text, re.IGNORECASE):
                entity = MedicalEntity(
                    text=match.group(),
                    label='TEMPERATURE',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                )
                entities.append(entity)
            
            # Age pattern
            age_pattern = r'\b(?:age|aged?)\s+(\d{1,3})\b'
            for match in re.finditer(age_pattern, text, re.IGNORECASE):
                entity = MedicalEntity(
                    text=match.group(1),
                    label='AGE',
                    start=match.start(1),
                    end=match.end(1),
                    confidence=0.95
                )
                entities.append(entity)
            
        except Exception as e:
            logger.error(f"Pattern entity extraction failed: {e}")
        
        return entities
    
    def _extract_terminology_entities(self, text: str) -> List[MedicalEntity]:
        """Extract entities using medical terminology matching."""
        entities = []
        
        try:
            text_lower = text.lower()
            
            # Search for medical terms
            for category, terms in self.medical_terminology.items():
                for main_term, synonyms in terms.items():
                    # Check main term
                    if main_term in text_lower:
                        start = text_lower.find(main_term)
                        entity = MedicalEntity(
                            text=text[start:start + len(main_term)],
                            label=category.upper(),
                            start=start,
                            end=start + len(main_term),
                            confidence=0.85,
                            normalized_form=main_term
                        )
                        entities.append(entity)
                    
                    # Check synonyms
                    for synonym in synonyms:
                        if synonym in text_lower:
                            start = text_lower.find(synonym)
                            entity = MedicalEntity(
                                text=text[start:start + len(synonym)],
                                label=category.upper(),
                                start=start,
                                end=start + len(synonym),
                                confidence=0.8,
                                normalized_form=main_term
                            )
                            entities.append(entity)
            
        except Exception as e:
            logger.error(f"Terminology entity extraction failed: {e}")
        
        return entities
    
    def _normalize_entities(self, entities: List[MedicalEntity]) -> List[MedicalEntity]:
        """Normalize and deduplicate entities."""
        try:
            # Sort by start position
            entities.sort(key=lambda x: x.start)
            
            # Remove overlapping entities (keep highest confidence)
            normalized = []
            for entity in entities:
                # Check for overlap with existing entities
                overlaps = False
                for existing in normalized:
                    if (entity.start < existing.end and entity.end > existing.start):
                        # Overlapping entities - keep the one with higher confidence
                        if entity.confidence > existing.confidence:
                            normalized.remove(existing)
                            normalized.append(entity)
                        overlaps = True
                        break
                
                if not overlaps:
                    normalized.append(entity)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Entity normalization failed: {e}")
            return entities
    
    def _map_to_medical_codes(self, entities: List[MedicalEntity]) -> List[Dict[str, Any]]:
        """Map entities to medical codes (ICD-10, CPT, etc.)."""
        medical_codes = []
        
        try:
            for entity in entities:
                # Simple mapping based on entity text and label
                entity_text_lower = entity.normalized_form.lower()
                
                # Search ICD-10 codes
                for code, info in self.medical_codes.get('icd10', {}).items():
                    if entity_text_lower in info['description'].lower():
                        medical_codes.append({
                            'entity_text': entity.text,
                            'code_system': 'ICD-10',
                            'code': code,
                            'description': info['description'],
                            'category': info['category'],
                            'confidence': entity.confidence * 0.8
                        })
                
                # Search CPT codes for procedures
                if entity.label in ['PROCEDURE', 'TEST', 'EXAMINATION']:
                    for code, info in self.medical_codes.get('cpt', {}).items():
                        if any(word in info['description'].lower() 
                              for word in entity_text_lower.split()):
                            medical_codes.append({
                                'entity_text': entity.text,
                                'code_system': 'CPT',
                                'code': code,
                                'description': info['description'],
                                'category': info['category'],
                                'confidence': entity.confidence * 0.7
                            })
            
        except Exception as e:
            logger.error(f"Medical code mapping failed: {e}")
        
        return medical_codes
    
    def _calculate_confidence(self, entities: List[MedicalEntity]) -> float:
        """Calculate overall confidence score for the extraction."""
        if not entities:
            return 0.0
        
        total_confidence = sum(entity.confidence for entity in entities)
        return total_confidence / len(entities)
    
    def _map_spacy_label(self, spacy_label: str) -> str:
        """Map spaCy labels to medical labels."""
        mapping = {
            'PERSON': 'PATIENT_NAME',
            'ORG': 'ORGANIZATION',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'QUANTITY': 'MEASUREMENT',
            'CARDINAL': 'NUMBER'
        }
        return mapping.get(spacy_label, spacy_label)
    
    def _map_pattern_label(self, pattern_label: str) -> str:
        """Map pattern labels to medical labels."""
        if 'MEDICATION' in pattern_label:
            return 'MEDICATION'
        elif 'VITAL' in pattern_label:
            return 'VITAL_SIGNS'
        else:
            return pattern_label.replace('_PATTERN_', '_').replace('_0', '').replace('_1', '').replace('_2', '')
    
    async def get_medical_suggestions(self, text: str, field_type: str) -> List[Dict[str, Any]]:
        """Get medical suggestions for form field auto-completion."""
        try:
            # Process the text to extract entities
            processing_result = await self.process_medical_text(text)
            entities = processing_result['entities']
            
            suggestions = []
            
            # Filter entities by field type
            for entity in entities:
                if self._entity_matches_field_type(entity['label'], field_type):
                    suggestions.append({
                        'value': entity['normalized_form'] or entity['text'],
                        'display_text': entity['text'],
                        'confidence': entity['confidence'],
                        'type': entity['label'],
                        'medical_codes': entity.get('medical_codes', [])
                    })
            
            # Sort by confidence
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Medical suggestions failed: {e}")
            return []
    
    def _entity_matches_field_type(self, entity_label: str, field_type: str) -> bool:
        """Check if entity label matches the expected field type."""
        mappings = {
            'patient_name': ['PATIENT_NAME', 'PERSON'],
            'age': ['AGE', 'NUMBER'],
            'diagnosis': ['CONDITIONS', 'DIAGNOSIS'],
            'medication': ['MEDICATIONS', 'MEDICATION'],
            'dosage': ['DOSAGE', 'MEASUREMENT'],
            'blood_pressure': ['BLOOD_PRESSURE', 'VITAL_SIGNS'],
            'temperature': ['TEMPERATURE', 'VITAL_SIGNS'],
            'procedure': ['PROCEDURE', 'TREATMENT']
        }
        
        expected_labels = mappings.get(field_type.lower(), [])
        return entity_label in expected_labels