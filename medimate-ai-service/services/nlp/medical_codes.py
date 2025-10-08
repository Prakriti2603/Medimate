"""
Medical coding systems integration (ICD-10, CPT, SNOMED, etc.).
Handles medical code validation, mapping, and lookup functionality.
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


class CodeSystem(Enum):
    """Supported medical coding systems."""
    ICD10_CM = "ICD-10-CM"
    ICD10_PCS = "ICD-10-PCS"
    CPT = "CPT"
    HCPCS = "HCPCS"
    SNOMED_CT = "SNOMED-CT"
    LOINC = "LOINC"
    RxNorm = "RxNorm"
    NDC = "NDC"


@dataclass
class MedicalCode:
    """Represents a medical code from any coding system."""
    code: str
    system: CodeSystem
    description: str
    category: str
    effective_date: Optional[str] = None
    status: str = "active"
    synonyms: List[str] = None
    parent_codes: List[str] = None
    child_codes: List[str] = None
    modifiers: List[str] = None
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.parent_codes is None:
            self.parent_codes = []
        if self.child_codes is None:
            self.child_codes = []
        if self.modifiers is None:
            self.modifiers = []


class MedicalCodeManager:
    """Manages medical coding systems and code validation."""
    
    def __init__(self):
        self.codes: Dict[str, Dict[str, MedicalCode]] = {}
        self.code_mappings: Dict[str, Dict[str, List[str]]] = {}  # Cross-system mappings
        self.search_index: Dict[str, List[Tuple[str, str]]] = {}  # Text to (system, code) mapping
        
        # Initialize with basic medical codes
        self._initialize_basic_codes()
    
    def _initialize_basic_codes(self):
        """Initialize with basic medical codes for common conditions."""
        try:
            # ICD-10-CM Diagnosis Codes
            icd10_codes = [
                MedicalCode("I10", CodeSystem.ICD10_CM, "Essential (primary) hypertension", "cardiovascular",
                           synonyms=["hypertension", "high blood pressure", "htn"]),
                MedicalCode("E11.9", CodeSystem.ICD10_CM, "Type 2 diabetes mellitus without complications", "endocrine",
                           synonyms=["diabetes", "diabetes mellitus", "dm", "type 2 diabetes"]),
                MedicalCode("I21.9", CodeSystem.ICD10_CM, "Acute myocardial infarction, unspecified", "cardiovascular",
                           synonyms=["heart attack", "myocardial infarction", "mi", "acute mi"]),
                MedicalCode("J44.1", CodeSystem.ICD10_CM, "Chronic obstructive pulmonary disease with acute exacerbation", "respiratory",
                           synonyms=["copd", "chronic obstructive pulmonary disease", "emphysema"]),
                MedicalCode("N18.6", CodeSystem.ICD10_CM, "End stage renal disease", "genitourinary",
                           synonyms=["kidney failure", "renal failure", "esrd", "end stage renal disease"]),
                MedicalCode("F32.9", CodeSystem.ICD10_CM, "Major depressive disorder, single episode, unspecified", "mental",
                           synonyms=["depression", "major depression", "depressive disorder"]),
                MedicalCode("M79.3", CodeSystem.ICD10_CM, "Panniculitis, unspecified", "musculoskeletal",
                           synonyms=["muscle pain", "myalgia", "muscle ache"]),
                MedicalCode("R50.9", CodeSystem.ICD10_CM, "Fever, unspecified", "symptoms",
                           synonyms=["fever", "pyrexia", "elevated temperature"]),
                MedicalCode("G43.909", CodeSystem.ICD10_CM, "Migraine, unspecified, not intractable, without status migrainosus", "neurological",
                           synonyms=["migraine", "headache", "severe headache"]),
                MedicalCode("J18.9", CodeSystem.ICD10_CM, "Pneumonia, unspecified organism", "respiratory",
                           synonyms=["pneumonia", "lung infection", "respiratory infection"])
            ]
            
            # CPT Procedure Codes
            cpt_codes = [
                MedicalCode("99213", CodeSystem.CPT, "Office or other outpatient visit for evaluation and management", "evaluation",
                           synonyms=["office visit", "outpatient visit", "consultation"]),
                MedicalCode("99214", CodeSystem.CPT, "Office or other outpatient visit for evaluation and management", "evaluation",
                           synonyms=["detailed office visit", "comprehensive visit"]),
                MedicalCode("93000", CodeSystem.CPT, "Electrocardiogram, routine ECG with at least 12 leads", "diagnostic",
                           synonyms=["ecg", "ekg", "electrocardiogram", "heart test"]),
                MedicalCode("80053", CodeSystem.CPT, "Comprehensive metabolic panel", "laboratory",
                           synonyms=["cmp", "metabolic panel", "blood chemistry", "basic metabolic panel"]),
                MedicalCode("85025", CodeSystem.CPT, "Blood count; complete (CBC), automated", "laboratory",
                           synonyms=["cbc", "complete blood count", "blood count", "full blood count"]),
                MedicalCode("36415", CodeSystem.CPT, "Collection of venous blood by venipuncture", "procedure",
                           synonyms=["blood draw", "venipuncture", "phlebotomy"]),
                MedicalCode("71020", CodeSystem.CPT, "Radiologic examination, chest, 2 views", "radiology",
                           synonyms=["chest x-ray", "chest xray", "cxr", "chest radiograph"]),
                MedicalCode("73060", CodeSystem.CPT, "Radiologic examination; knee, 1 or 2 views", "radiology",
                           synonyms=["knee x-ray", "knee xray", "knee radiograph"]),
                MedicalCode("76700", CodeSystem.CPT, "Ultrasound, abdominal, real time with image documentation", "radiology",
                           synonyms=["abdominal ultrasound", "ultrasound abdomen", "abdominal us"]),
                MedicalCode("90471", CodeSystem.CPT, "Immunization administration", "immunization",
                           synonyms=["vaccination", "immunization", "vaccine administration", "shot"])
            ]
            
            # HCPCS Codes
            hcpcs_codes = [
                MedicalCode("J7050", CodeSystem.HCPCS, "Infusion, normal saline solution, 1000 cc", "medication",
                           synonyms=["normal saline", "saline infusion", "iv saline"]),
                MedicalCode("A4253", CodeSystem.HCPCS, "Blood glucose test or reagent strips", "supplies",
                           synonyms=["glucose strips", "blood sugar strips", "test strips"]),
                MedicalCode("E0424", CodeSystem.HCPCS, "Stationary compressed gaseous oxygen system", "equipment",
                           synonyms=["oxygen concentrator", "oxygen system", "home oxygen"])
            ]
            
            # Add all codes to the system
            all_codes = icd10_codes + cpt_codes + hcpcs_codes
            for code in all_codes:
                self.add_code(code)
            
            logger.info(f"Initialized basic medical codes: {len(all_codes)} codes across {len(set(code.system for code in all_codes))} systems")
            
        except Exception as e:
            logger.error(f"Failed to initialize basic codes: {e}")
    
    def add_code(self, code: MedicalCode):
        """Add a medical code to the system."""
        try:
            system_name = code.system.value
            
            # Initialize system if not exists
            if system_name not in self.codes:
                self.codes[system_name] = {}
            
            # Add code
            self.codes[system_name][code.code] = code
            
            # Build search index
            search_terms = [code.description.lower()] + [syn.lower() for syn in code.synonyms]
            for term in search_terms:
                if term not in self.search_index:
                    self.search_index[term] = []
                self.search_index[term].append((system_name, code.code))
            
        except Exception as e:
            logger.error(f"Failed to add code {code.code}: {e}")
    
    def lookup_code(self, code: str, system: CodeSystem) -> Optional[MedicalCode]:
        """Look up a specific medical code."""
        try:
            system_name = system.value
            if system_name in self.codes and code in self.codes[system_name]:
                return self.codes[system_name][code]
            return None
            
        except Exception as e:
            logger.error(f"Code lookup failed for {code} in {system}: {e}")
            return None
    
    def search_codes(self, query: str, system: CodeSystem = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for medical codes by description or synonyms."""
        try:
            query_lower = query.lower()
            results = []
            
            # Direct search in index
            if query_lower in self.search_index:
                for system_name, code in self.search_index[query_lower]:
                    if system is None or system.value == system_name:
                        code_obj = self.codes[system_name][code]
                        results.append({
                            'code': code_obj.code,
                            'system': code_obj.system.value,
                            'description': code_obj.description,
                            'category': code_obj.category,
                            'confidence': 1.0,
                            'match_type': 'exact'
                        })
            
            # Partial matching
            for term, code_list in self.search_index.items():
                if query_lower in term and query_lower != term:
                    for system_name, code in code_list:
                        if system is None or system.value == system_name:
                            code_obj = self.codes[system_name][code]
                            
                            # Calculate confidence based on match quality
                            confidence = len(query_lower) / len(term)
                            
                            results.append({
                                'code': code_obj.code,
                                'system': code_obj.system.value,
                                'description': code_obj.description,
                                'category': code_obj.category,
                                'confidence': confidence,
                                'match_type': 'partial'
                            })
            
            # Remove duplicates and sort by confidence
            unique_results = {}
            for result in results:
                key = f"{result['system']}:{result['code']}"
                if key not in unique_results or result['confidence'] > unique_results[key]['confidence']:
                    unique_results[key] = result
            
            sorted_results = sorted(unique_results.values(), 
                                  key=lambda x: x['confidence'], reverse=True)
            
            return sorted_results[:limit]
            
        except Exception as e:
            logger.error(f"Code search failed for '{query}': {e}")
            return []
    
    def validate_code(self, code: str, system: CodeSystem) -> Dict[str, Any]:
        """Validate if a medical code exists and is valid."""
        try:
            code_obj = self.lookup_code(code, system)
            
            if not code_obj:
                return {
                    'is_valid': False,
                    'message': f'Code {code} not found in {system.value}',
                    'suggestions': self.search_codes(code, system, limit=3)
                }
            
            return {
                'is_valid': True,
                'code': code_obj.code,
                'system': code_obj.system.value,
                'description': code_obj.description,
                'category': code_obj.category,
                'status': code_obj.status,
                'effective_date': code_obj.effective_date
            }
            
        except Exception as e:
            logger.error(f"Code validation failed for {code}: {e}")
            return {
                'is_valid': False,
                'message': f'Validation error: {str(e)}'
            }
    
    def get_codes_by_category(self, category: str, system: CodeSystem = None) -> List[MedicalCode]:
        """Get all codes in a specific category."""
        try:
            results = []
            
            systems_to_search = [system.value] if system else self.codes.keys()
            
            for system_name in systems_to_search:
                if system_name in self.codes:
                    for code_obj in self.codes[system_name].values():
                        if code_obj.category.lower() == category.lower():
                            results.append(code_obj)
            
            return results
            
        except Exception as e:
            logger.error(f"Category search failed for '{category}': {e}")
            return []
    
    def suggest_codes_for_text(self, text: str, context: str = None) -> List[Dict[str, Any]]:
        """Suggest appropriate medical codes for given text."""
        try:
            suggestions = []
            text_lower = text.lower()
            
            # Search for direct matches
            direct_matches = self.search_codes(text, limit=5)
            suggestions.extend(direct_matches)
            
            # Search for individual words
            words = re.findall(r'\b\w+\b', text_lower)
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_matches = self.search_codes(word, limit=2)
                    for match in word_matches:
                        match['match_type'] = 'word_match'
                        match['confidence'] *= 0.7  # Lower confidence for word matches
                    suggestions.extend(word_matches)
            
            # Context-based suggestions
            if context:
                context_matches = self.search_codes(context, limit=3)
                for match in context_matches:
                    match['match_type'] = 'context_match'
                    match['confidence'] *= 0.6
                suggestions.extend(context_matches)
            
            # Remove duplicates and sort
            unique_suggestions = {}
            for suggestion in suggestions:
                key = f"{suggestion['system']}:{suggestion['code']}"
                if key not in unique_suggestions or suggestion['confidence'] > unique_suggestions[key]['confidence']:
                    unique_suggestions[key] = suggestion
            
            sorted_suggestions = sorted(unique_suggestions.values(), 
                                      key=lambda x: x['confidence'], reverse=True)
            
            return sorted_suggestions[:10]
            
        except Exception as e:
            logger.error(f"Code suggestion failed for '{text}': {e}")
            return []
    
    def get_code_hierarchy(self, code: str, system: CodeSystem) -> Dict[str, Any]:
        """Get the hierarchical relationship of a code."""
        try:
            code_obj = self.lookup_code(code, system)
            if not code_obj:
                return {}
            
            hierarchy = {
                'code': code_obj.code,
                'description': code_obj.description,
                'system': code_obj.system.value,
                'category': code_obj.category,
                'parent_codes': [],
                'child_codes': [],
                'sibling_codes': []
            }
            
            # Get parent codes
            for parent_code in code_obj.parent_codes:
                parent_obj = self.lookup_code(parent_code, system)
                if parent_obj:
                    hierarchy['parent_codes'].append({
                        'code': parent_obj.code,
                        'description': parent_obj.description
                    })
            
            # Get child codes
            for child_code in code_obj.child_codes:
                child_obj = self.lookup_code(child_code, system)
                if child_obj:
                    hierarchy['child_codes'].append({
                        'code': child_obj.code,
                        'description': child_obj.description
                    })
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Hierarchy lookup failed for {code}: {e}")
            return {}
    
    def cross_map_codes(self, code: str, source_system: CodeSystem, target_system: CodeSystem) -> List[Dict[str, Any]]:
        """Map codes between different coding systems."""
        try:
            # This is a simplified cross-mapping
            # In production, this would use official crosswalk tables
            
            source_code = self.lookup_code(code, source_system)
            if not source_code:
                return []
            
            # Search for similar codes in target system based on description
            target_matches = self.search_codes(source_code.description, target_system, limit=5)
            
            # Also search synonyms
            for synonym in source_code.synonyms:
                synonym_matches = self.search_codes(synonym, target_system, limit=3)
                target_matches.extend(synonym_matches)
            
            # Remove duplicates and add mapping confidence
            unique_matches = {}
            for match in target_matches:
                key = match['code']
                if key not in unique_matches:
                    match['mapping_confidence'] = match['confidence'] * 0.8  # Cross-mapping is less certain
                    match['source_code'] = code
                    match['source_system'] = source_system.value
                    unique_matches[key] = match
            
            return list(unique_matches.values())
            
        except Exception as e:
            logger.error(f"Cross-mapping failed from {code} ({source_system}) to {target_system}: {e}")
            return []
    
    def get_billable_codes(self, diagnosis_codes: List[str], procedure_codes: List[str] = None) -> Dict[str, Any]:
        """Get billable code combinations for given diagnoses and procedures."""
        try:
            if procedure_codes is None:
                procedure_codes = []
            
            billable_info = {
                'primary_diagnosis': None,
                'secondary_diagnoses': [],
                'procedures': [],
                'billing_notes': [],
                'estimated_reimbursement': None
            }
            
            # Validate diagnosis codes
            valid_diagnoses = []
            for dx_code in diagnosis_codes:
                validation = self.validate_code(dx_code, CodeSystem.ICD10_CM)
                if validation['is_valid']:
                    valid_diagnoses.append(validation)
            
            if valid_diagnoses:
                billable_info['primary_diagnosis'] = valid_diagnoses[0]
                billable_info['secondary_diagnoses'] = valid_diagnoses[1:]
            
            # Validate procedure codes
            for proc_code in procedure_codes:
                validation = self.validate_code(proc_code, CodeSystem.CPT)
                if validation['is_valid']:
                    billable_info['procedures'].append(validation)
            
            # Add billing notes
            if not valid_diagnoses:
                billable_info['billing_notes'].append("No valid diagnosis codes provided")
            
            if len(valid_diagnoses) > 1:
                billable_info['billing_notes'].append("Multiple diagnoses - verify primary diagnosis")
            
            return billable_info
            
        except Exception as e:
            logger.error(f"Billable codes analysis failed: {e}")
            return {}
    
    def load_code_set(self, file_path: str, system: CodeSystem):
        """Load a complete code set from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            loaded_count = 0
            for code_data in data.get('codes', []):
                code = MedicalCode(
                    code=code_data['code'],
                    system=system,
                    description=code_data['description'],
                    category=code_data.get('category', ''),
                    effective_date=code_data.get('effective_date'),
                    status=code_data.get('status', 'active'),
                    synonyms=code_data.get('synonyms', []),
                    parent_codes=code_data.get('parent_codes', []),
                    child_codes=code_data.get('child_codes', [])
                )
                self.add_code(code)
                loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} codes for {system.value} from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load code set from {file_path}: {e}")
    
    def export_codes(self, file_path: str, system: CodeSystem = None):
        """Export codes to file."""
        try:
            export_data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'systems': list(self.codes.keys()) if system is None else [system.value]
                },
                'codes': []
            }
            
            systems_to_export = [system.value] if system else self.codes.keys()
            
            for system_name in systems_to_export:
                if system_name in self.codes:
                    for code_obj in self.codes[system_name].values():
                        code_data = {
                            'code': code_obj.code,
                            'system': code_obj.system.value,
                            'description': code_obj.description,
                            'category': code_obj.category,
                            'effective_date': code_obj.effective_date,
                            'status': code_obj.status,
                            'synonyms': code_obj.synonyms,
                            'parent_codes': code_obj.parent_codes,
                            'child_codes': code_obj.child_codes
                        }
                        export_data['codes'].append(code_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(export_data['codes'])} codes to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export codes: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded codes."""
        try:
            stats = {
                'total_codes': sum(len(codes) for codes in self.codes.values()),
                'systems': {},
                'categories': {},
                'search_terms': len(self.search_index)
            }
            
            # System statistics
            for system_name, codes in self.codes.items():
                stats['systems'][system_name] = len(codes)
            
            # Category statistics
            for codes in self.codes.values():
                for code_obj in codes.values():
                    category = code_obj.category
                    if category not in stats['categories']:
                        stats['categories'][category] = 0
                    stats['categories'][category] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}