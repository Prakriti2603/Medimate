"""
Medical terminology management and normalization.
Handles medical term standardization, code mapping, and vocabulary management.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class MedicalCodeSystem(Enum):
    """Medical coding systems."""
    ICD10 = "ICD-10"
    ICD11 = "ICD-11"
    CPT = "CPT"
    SNOMED = "SNOMED-CT"
    LOINC = "LOINC"
    RxNorm = "RxNorm"


@dataclass
class MedicalCode:
    """Represents a medical code."""
    code: str
    system: MedicalCodeSystem
    description: str
    category: str
    synonyms: List[str] = None
    parent_codes: List[str] = None
    child_codes: List[str] = None
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.parent_codes is None:
            self.parent_codes = []
        if self.child_codes is None:
            self.child_codes = []


@dataclass
class MedicalTerm:
    """Represents a standardized medical term."""
    term: str
    category: str
    synonyms: List[str]
    abbreviations: List[str]
    codes: List[MedicalCode]
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.abbreviations is None:
            self.abbreviations = []
        if self.codes is None:
            self.codes = []


class MedicalTerminologyManager:
    """Manages medical terminology, standardization, and code mapping."""
    
    def __init__(self):
        self.terms: Dict[str, MedicalTerm] = {}
        self.codes: Dict[str, Dict[str, MedicalCode]] = {}
        self.abbreviations: Dict[str, str] = {}
        self.synonyms: Dict[str, str] = {}  # Maps synonym to standard term
        self.categories: Dict[str, List[str]] = {}
        
        # Initialize with basic medical terminology
        self._initialize_basic_terminology()
    
    def _initialize_basic_terminology(self):
        """Initialize with basic medical terminology."""
        try:
            # Medical conditions
            conditions = [
                MedicalTerm(
                    term="hypertension",
                    category="cardiovascular",
                    synonyms=["high blood pressure", "elevated blood pressure"],
                    abbreviations=["htn", "hbp"],
                    codes=[
                        MedicalCode("I10", MedicalCodeSystem.ICD10, "Essential hypertension", "cardiovascular")
                    ]
                ),
                MedicalTerm(
                    term="diabetes mellitus",
                    category="endocrine",
                    synonyms=["diabetes", "diabetic condition"],
                    abbreviations=["dm", "diabetes"],
                    codes=[
                        MedicalCode("E11", MedicalCodeSystem.ICD10, "Type 2 diabetes mellitus", "endocrine")
                    ]
                ),
                MedicalTerm(
                    term="myocardial infarction",
                    category="cardiovascular",
                    synonyms=["heart attack", "cardiac arrest", "mi"],
                    abbreviations=["mi", "ami"],
                    codes=[
                        MedicalCode("I21", MedicalCodeSystem.ICD10, "Acute myocardial infarction", "cardiovascular")
                    ]
                ),
                MedicalTerm(
                    term="pneumonia",
                    category="respiratory",
                    synonyms=["lung infection", "respiratory infection"],
                    abbreviations=["pna"],
                    codes=[
                        MedicalCode("J18", MedicalCodeSystem.ICD10, "Pneumonia, unspecified organism", "respiratory")
                    ]
                ),
                MedicalTerm(
                    term="chronic obstructive pulmonary disease",
                    category="respiratory",
                    synonyms=["copd", "chronic bronchitis", "emphysema"],
                    abbreviations=["copd"],
                    codes=[
                        MedicalCode("J44", MedicalCodeSystem.ICD10, "Other chronic obstructive pulmonary disease", "respiratory")
                    ]
                )
            ]
            
            # Medications
            medications = [
                MedicalTerm(
                    term="metformin",
                    category="medication",
                    synonyms=["glucophage", "fortamet", "glumetza"],
                    abbreviations=["met"],
                    codes=[]
                ),
                MedicalTerm(
                    term="lisinopril",
                    category="medication",
                    synonyms=["prinivil", "zestril"],
                    abbreviations=["acei"],
                    codes=[]
                ),
                MedicalTerm(
                    term="atorvastatin",
                    category="medication",
                    synonyms=["lipitor"],
                    abbreviations=["statin"],
                    codes=[]
                ),
                MedicalTerm(
                    term="metoprolol",
                    category="medication",
                    synonyms=["lopressor", "toprol"],
                    abbreviations=["bb", "beta blocker"],
                    codes=[]
                ),
                MedicalTerm(
                    term="amlodipine",
                    category="medication",
                    synonyms=["norvasc"],
                    abbreviations=["ccb", "calcium channel blocker"],
                    codes=[]
                )
            ]
            
            # Body parts and anatomy
            anatomy = [
                MedicalTerm(
                    term="heart",
                    category="anatomy",
                    synonyms=["cardiac", "cardio"],
                    abbreviations=["cardiac"],
                    codes=[]
                ),
                MedicalTerm(
                    term="lung",
                    category="anatomy",
                    synonyms=["pulmonary", "respiratory"],
                    abbreviations=["pulm", "resp"],
                    codes=[]
                ),
                MedicalTerm(
                    term="kidney",
                    category="anatomy",
                    synonyms=["renal", "nephro"],
                    abbreviations=["renal"],
                    codes=[]
                ),
                MedicalTerm(
                    term="liver",
                    category="anatomy",
                    synonyms=["hepatic", "hepato"],
                    abbreviations=["hepatic"],
                    codes=[]
                )
            ]
            
            # Add all terms
            all_terms = conditions + medications + anatomy
            for term in all_terms:
                self.add_term(term)
            
            logger.info(f"Initialized basic medical terminology: {len(all_terms)} terms")
            
        except Exception as e:
            logger.error(f"Failed to initialize basic terminology: {e}")
    
    def add_term(self, term: MedicalTerm):
        """Add a medical term to the terminology database."""
        try:
            # Add main term
            self.terms[term.term.lower()] = term
            
            # Add synonyms mapping
            for synonym in term.synonyms:
                self.synonyms[synonym.lower()] = term.term.lower()
            
            # Add abbreviations mapping
            for abbrev in term.abbreviations:
                self.abbreviations[abbrev.lower()] = term.term.lower()
            
            # Add to category
            if term.category not in self.categories:
                self.categories[term.category] = []
            self.categories[term.category].append(term.term.lower())
            
            # Add codes
            for code in term.codes:
                system_name = code.system.value
                if system_name not in self.codes:
                    self.codes[system_name] = {}
                self.codes[system_name][code.code] = code
            
        except Exception as e:
            logger.error(f"Failed to add term {term.term}: {e}")
    
    def normalize_term(self, text: str) -> Optional[str]:
        """Normalize a medical term to its standard form."""
        try:
            text_lower = text.lower().strip()
            
            # Direct match
            if text_lower in self.terms:
                return self.terms[text_lower].term
            
            # Synonym match
            if text_lower in self.synonyms:
                return self.synonyms[text_lower]
            
            # Abbreviation match
            if text_lower in self.abbreviations:
                return self.abbreviations[text_lower]
            
            # Partial match (fuzzy matching)
            return self._fuzzy_match(text_lower)
            
        except Exception as e:
            logger.error(f"Term normalization failed for '{text}': {e}")
            return None
    
    def _fuzzy_match(self, text: str) -> Optional[str]:
        """Perform fuzzy matching for medical terms."""
        try:
            # Simple fuzzy matching based on word overlap
            text_words = set(text.split())
            best_match = None
            best_score = 0
            
            for term_key, term in self.terms.items():
                # Check main term
                term_words = set(term_key.split())
                overlap = len(text_words.intersection(term_words))
                score = overlap / max(len(text_words), len(term_words))
                
                if score > best_score and score > 0.5:  # Minimum 50% overlap
                    best_score = score
                    best_match = term.term
                
                # Check synonyms
                for synonym in term.synonyms:
                    synonym_words = set(synonym.lower().split())
                    overlap = len(text_words.intersection(synonym_words))
                    score = overlap / max(len(text_words), len(synonym_words))
                    
                    if score > best_score and score > 0.5:
                        best_score = score
                        best_match = term.term
            
            return best_match if best_score > 0.6 else None  # Return only high-confidence matches
            
        except Exception as e:
            logger.error(f"Fuzzy matching failed: {e}")
            return None
    
    def get_medical_codes(self, term: str) -> List[MedicalCode]:
        """Get medical codes for a given term."""
        try:
            normalized_term = self.normalize_term(term)
            if not normalized_term:
                return []
            
            if normalized_term in self.terms:
                return self.terms[normalized_term].codes
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get medical codes for '{term}': {e}")
            return []
    
    def search_by_category(self, category: str) -> List[MedicalTerm]:
        """Search terms by medical category."""
        try:
            if category.lower() not in self.categories:
                return []
            
            terms = []
            for term_key in self.categories[category.lower()]:
                if term_key in self.terms:
                    terms.append(self.terms[term_key])
            
            return terms
            
        except Exception as e:
            logger.error(f"Category search failed for '{category}': {e}")
            return []
    
    def search_by_code(self, code: str, system: MedicalCodeSystem) -> Optional[MedicalCode]:
        """Search for a medical code."""
        try:
            system_name = system.value
            if system_name in self.codes and code in self.codes[system_name]:
                return self.codes[system_name][code]
            
            return None
            
        except Exception as e:
            logger.error(f"Code search failed for '{code}' in {system}: {e}")
            return None
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand medical abbreviations in text."""
        try:
            words = text.split()
            expanded_words = []
            
            for word in words:
                # Clean word for matching
                clean_word = re.sub(r'[^\w]', '', word.lower())
                
                if clean_word in self.abbreviations:
                    # Get the standard term
                    standard_term = self.abbreviations[clean_word]
                    
                    # Preserve original case and punctuation
                    if word.isupper():
                        expanded = standard_term.upper()
                    elif word.istitle():
                        expanded = standard_term.title()
                    else:
                        expanded = standard_term
                    
                    # Add back punctuation
                    punctuation = re.findall(r'[^\w]', word)
                    if punctuation:
                        expanded += ''.join(punctuation)
                    
                    expanded_words.append(expanded)
                else:
                    expanded_words.append(word)
            
            return ' '.join(expanded_words)
            
        except Exception as e:
            logger.error(f"Abbreviation expansion failed: {e}")
            return text
    
    def get_term_suggestions(self, partial_text: str, category: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get term suggestions for auto-completion."""
        try:
            suggestions = []
            partial_lower = partial_text.lower()
            
            # Search in main terms
            for term_key, term in self.terms.items():
                if category and term.category != category.lower():
                    continue
                
                if term_key.startswith(partial_lower):
                    suggestions.append({
                        'term': term.term,
                        'category': term.category,
                        'confidence': 1.0,
                        'type': 'exact_match'
                    })
            
            # Search in synonyms
            for synonym, standard_term in self.synonyms.items():
                if category and self.terms[standard_term].category != category.lower():
                    continue
                
                if synonym.startswith(partial_lower):
                    suggestions.append({
                        'term': self.terms[standard_term].term,
                        'category': self.terms[standard_term].category,
                        'confidence': 0.9,
                        'type': 'synonym_match'
                    })
            
            # Search in abbreviations
            for abbrev, standard_term in self.abbreviations.items():
                if category and self.terms[standard_term].category != category.lower():
                    continue
                
                if abbrev.startswith(partial_lower):
                    suggestions.append({
                        'term': self.terms[standard_term].term,
                        'category': self.terms[standard_term].category,
                        'confidence': 0.8,
                        'type': 'abbreviation_match'
                    })
            
            # Remove duplicates and sort by confidence
            unique_suggestions = {}
            for suggestion in suggestions:
                key = suggestion['term']
                if key not in unique_suggestions or suggestion['confidence'] > unique_suggestions[key]['confidence']:
                    unique_suggestions[key] = suggestion
            
            sorted_suggestions = sorted(unique_suggestions.values(), 
                                      key=lambda x: x['confidence'], reverse=True)
            
            return sorted_suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Term suggestions failed: {e}")
            return []
    
    def validate_medical_term(self, term: str, expected_category: str = None) -> Dict[str, Any]:
        """Validate if a term is a recognized medical term."""
        try:
            normalized = self.normalize_term(term)
            
            if not normalized:
                return {
                    'is_valid': False,
                    'confidence': 0.0,
                    'message': 'Term not recognized in medical vocabulary'
                }
            
            term_obj = self.terms[normalized]
            
            # Check category if specified
            if expected_category and term_obj.category != expected_category.lower():
                return {
                    'is_valid': False,
                    'confidence': 0.5,
                    'message': f'Term found but belongs to category "{term_obj.category}", expected "{expected_category}"',
                    'normalized_term': normalized,
                    'actual_category': term_obj.category
                }
            
            return {
                'is_valid': True,
                'confidence': term_obj.confidence,
                'normalized_term': normalized,
                'category': term_obj.category,
                'synonyms': term_obj.synonyms,
                'codes': [{'code': code.code, 'system': code.system.value, 'description': code.description} 
                         for code in term_obj.codes]
            }
            
        except Exception as e:
            logger.error(f"Term validation failed for '{term}': {e}")
            return {
                'is_valid': False,
                'confidence': 0.0,
                'message': f'Validation error: {str(e)}'
            }
    
    def load_custom_terminology(self, file_path: str):
        """Load custom medical terminology from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for term_data in data.get('terms', []):
                # Create MedicalCode objects
                codes = []
                for code_data in term_data.get('codes', []):
                    code = MedicalCode(
                        code=code_data['code'],
                        system=MedicalCodeSystem(code_data['system']),
                        description=code_data['description'],
                        category=code_data.get('category', ''),
                        synonyms=code_data.get('synonyms', [])
                    )
                    codes.append(code)
                
                # Create MedicalTerm object
                term = MedicalTerm(
                    term=term_data['term'],
                    category=term_data['category'],
                    synonyms=term_data.get('synonyms', []),
                    abbreviations=term_data.get('abbreviations', []),
                    codes=codes,
                    confidence=term_data.get('confidence', 1.0)
                )
                
                self.add_term(term)
            
            logger.info(f"Loaded custom terminology from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load custom terminology: {e}")
    
    def export_terminology(self, file_path: str):
        """Export current terminology to file."""
        try:
            export_data = {
                'terms': [],
                'metadata': {
                    'total_terms': len(self.terms),
                    'categories': list(self.categories.keys()),
                    'export_timestamp': str(datetime.now())
                }
            }
            
            for term in self.terms.values():
                term_data = {
                    'term': term.term,
                    'category': term.category,
                    'synonyms': term.synonyms,
                    'abbreviations': term.abbreviations,
                    'confidence': term.confidence,
                    'codes': [
                        {
                            'code': code.code,
                            'system': code.system.value,
                            'description': code.description,
                            'category': code.category,
                            'synonyms': code.synonyms
                        }
                        for code in term.codes
                    ]
                }
                export_data['terms'].append(term_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported terminology to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export terminology: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get terminology database statistics."""
        try:
            stats = {
                'total_terms': len(self.terms),
                'total_synonyms': len(self.synonyms),
                'total_abbreviations': len(self.abbreviations),
                'categories': {cat: len(terms) for cat, terms in self.categories.items()},
                'code_systems': {system: len(codes) for system, codes in self.codes.items()},
                'top_categories': sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}