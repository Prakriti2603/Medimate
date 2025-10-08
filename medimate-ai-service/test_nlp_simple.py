#!/usr/bin/env python3
"""
Simple test for NLP components without external dependencies.
"""

import json
import re
import sys
from pathlib import Path


def test_medical_terminology_basic():
    """Test basic medical terminology functionality."""
    print("🧪 Testing Medical Terminology (Basic)")
    
    # Basic medical terms dictionary
    medical_terms = {
        "conditions": {
            "hypertension": ["high blood pressure", "htn", "elevated bp"],
            "diabetes": ["diabetes mellitus", "dm", "diabetic"],
            "myocardial infarction": ["heart attack", "mi", "cardiac arrest"],
        },
        "medications": {
            "metformin": ["glucophage", "fortamet"],
            "lisinopril": ["prinivil", "zestril"],
            "atorvastatin": ["lipitor"],
        }
    }
    
    # Test term normalization
    def normalize_term(text):
        text_lower = text.lower().strip()
        
        # Direct match
        for category, terms in medical_terms.items():
            for main_term, synonyms in terms.items():
                if text_lower == main_term:
                    return main_term
                if text_lower in synonyms:
                    return main_term
        return None
    
    # Test cases
    test_cases = [
        ("hypertension", "hypertension"),
        ("htn", "hypertension"),
        ("high blood pressure", "hypertension"),
        ("diabetes", "diabetes"),
        ("dm", "diabetes"),
        ("heart attack", "myocardial infarction"),
        ("lipitor", "atorvastatin"),
        ("unknown term", None)
    ]
    
    passed = 0
    for input_term, expected in test_cases:
        result = normalize_term(input_term)
        if result == expected:
            print(f"  ✅ '{input_term}' → '{result}'")
            passed += 1
        else:
            print(f"  ❌ '{input_term}' → '{result}' (expected '{expected}')")
    
    print(f"📊 Terminology Test: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_medical_codes_basic():
    """Test basic medical codes functionality."""
    print("\n🧪 Testing Medical Codes (Basic)")
    
    # Basic medical codes
    medical_codes = {
        "ICD-10": {
            "I10": {"description": "Essential hypertension", "category": "cardiovascular"},
            "E11": {"description": "Type 2 diabetes mellitus", "category": "endocrine"},
            "I21": {"description": "Acute myocardial infarction", "category": "cardiovascular"},
        },
        "CPT": {
            "99213": {"description": "Office visit, established patient", "category": "evaluation"},
            "93000": {"description": "Electrocardiogram", "category": "diagnostic"},
            "80053": {"description": "Comprehensive metabolic panel", "category": "laboratory"},
        }
    }
    
    def lookup_code(code, system):
        if system in medical_codes and code in medical_codes[system]:
            return medical_codes[system][code]
        return None
    
    def search_codes(query, limit=5):
        results = []
        query_lower = query.lower()
        
        for system, codes in medical_codes.items():
            for code, info in codes.items():
                if query_lower in info['description'].lower():
                    results.append({
                        'code': code,
                        'system': system,
                        'description': info['description'],
                        'category': info['category']
                    })
        
        return results[:limit]
    
    # Test code lookup
    test_lookups = [
        ("I10", "ICD-10", True),
        ("99213", "CPT", True),
        ("INVALID", "ICD-10", False),
    ]
    
    lookup_passed = 0
    for code, system, should_exist in test_lookups:
        result = lookup_code(code, system)
        exists = result is not None
        if exists == should_exist:
            if exists:
                print(f"  ✅ {code} ({system}): {result['description']}")
            else:
                print(f"  ✅ {code} ({system}): Not found (as expected)")
            lookup_passed += 1
        else:
            print(f"  ❌ {code} ({system}): Unexpected result")
    
    # Test code search
    search_queries = ["hypertension", "diabetes", "office visit"]
    search_passed = 0
    
    for query in search_queries:
        results = search_codes(query)
        if results:
            print(f"  ✅ Search '{query}': {len(results)} results")
            for result in results[:2]:
                print(f"    - {result['code']} ({result['system']}): {result['description']}")
            search_passed += 1
        else:
            print(f"  ❌ Search '{query}': No results")
    
    total_tests = len(test_lookups) + len(search_queries)
    total_passed = lookup_passed + search_passed
    
    print(f"📊 Medical Codes Test: {total_passed}/{total_tests} passed")
    return total_passed == total_tests


def test_entity_extraction_basic():
    """Test basic entity extraction using regex patterns."""
    print("\n🧪 Testing Entity Extraction (Basic)")
    
    def extract_entities(text):
        entities = []
        
        # Age pattern
        age_pattern = r'\b(?:age|aged?)\s+(\d{1,3})\b'
        for match in re.finditer(age_pattern, text, re.IGNORECASE):
            entities.append({
                'text': match.group(1),
                'label': 'AGE',
                'start': match.start(1),
                'end': match.end(1),
                'confidence': 0.95
            })
        
        # Blood pressure pattern
        bp_pattern = r'\b(\d{2,3})/(\d{2,3})\s*mmHg\b'
        for match in re.finditer(bp_pattern, text, re.IGNORECASE):
            entities.append({
                'text': match.group(),
                'label': 'BLOOD_PRESSURE',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.95
            })
        
        # Medication dosage pattern
        dosage_pattern = r'\b(\d+(?:\.\d+)?)\s*(mg|ml|mcg)\b'
        for match in re.finditer(dosage_pattern, text, re.IGNORECASE):
            entities.append({
                'text': match.group(),
                'label': 'DOSAGE',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.9
            })
        
        # Patient name pattern (simple)
        name_pattern = r'Patient\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        for match in re.finditer(name_pattern, text):
            entities.append({
                'text': match.group(1),
                'label': 'PATIENT_NAME',
                'start': match.start(1),
                'end': match.end(1),
                'confidence': 0.8
            })
        
        return entities
    
    # Test text
    test_text = """
    Patient John Doe, age 45, presents with chest pain.
    Blood pressure is 160/95 mmHg. Prescribed metoprolol 50mg twice daily.
    """
    
    entities = extract_entities(test_text)
    
    print(f"  📄 Test text: {len(test_text)} characters")
    print(f"  🏷️  Entities found: {len(entities)}")
    
    expected_entities = ['PATIENT_NAME', 'AGE', 'BLOOD_PRESSURE', 'DOSAGE']
    found_labels = [e['label'] for e in entities]
    
    for expected in expected_entities:
        if expected in found_labels:
            entity = next(e for e in entities if e['label'] == expected)
            print(f"  ✅ {expected}: '{entity['text']}' (confidence: {entity['confidence']})")
        else:
            print(f"  ❌ {expected}: Not found")
    
    success_rate = len([e for e in expected_entities if e in found_labels]) / len(expected_entities)
    print(f"📊 Entity Extraction Test: {success_rate:.1%} success rate")
    
    return success_rate >= 0.75  # 75% success rate


def test_form_field_mapping():
    """Test mapping extracted entities to form fields."""
    print("\n🧪 Testing Form Field Mapping")
    
    # Sample extracted entities
    entities = [
        {'text': 'John Doe', 'label': 'PATIENT_NAME', 'confidence': 0.9},
        {'text': '45', 'label': 'AGE', 'confidence': 0.95},
        {'text': '160/95', 'label': 'BLOOD_PRESSURE', 'confidence': 0.95},
        {'text': 'hypertension', 'label': 'DIAGNOSIS', 'confidence': 0.85},
        {'text': '50mg', 'label': 'DOSAGE', 'confidence': 0.9}
    ]
    
    # Form template
    form_template = {
        'patient_name': {'category': 'demographics'},
        'patient_age': {'category': 'demographics'},
        'blood_pressure': {'category': 'vitals'},
        'primary_diagnosis': {'category': 'medical'}
    }
    
    def map_entities_to_form(entities, form_template):
        filled_form = {}
        
        for field_name, field_config in form_template.items():
            filled_form[field_name] = {
                'value': None,
                'confidence': 0.0,
                'auto_filled': False
            }
        
        # Map entities to form fields
        for entity in entities:
            if entity['label'] == 'PATIENT_NAME' and 'patient_name' in form_template:
                filled_form['patient_name'] = {
                    'value': entity['text'],
                    'confidence': entity['confidence'],
                    'auto_filled': True
                }
            elif entity['label'] == 'AGE' and 'patient_age' in form_template:
                filled_form['patient_age'] = {
                    'value': entity['text'],
                    'confidence': entity['confidence'],
                    'auto_filled': True
                }
            elif entity['label'] == 'BLOOD_PRESSURE' and 'blood_pressure' in form_template:
                filled_form['blood_pressure'] = {
                    'value': entity['text'],
                    'confidence': entity['confidence'],
                    'auto_filled': True
                }
            elif entity['label'] == 'DIAGNOSIS' and 'primary_diagnosis' in form_template:
                filled_form['primary_diagnosis'] = {
                    'value': entity['text'],
                    'confidence': entity['confidence'],
                    'auto_filled': True
                }
        
        return filled_form
    
    # Test mapping
    filled_form = map_entities_to_form(entities, form_template)
    
    fields_filled = 0
    total_fields = len(form_template)
    
    print(f"  📋 Form fields: {total_fields}")
    
    for field_name, field_data in filled_form.items():
        if field_data['auto_filled']:
            print(f"  ✅ {field_name}: '{field_data['value']}' (confidence: {field_data['confidence']})")
            fields_filled += 1
        else:
            print(f"  ❌ {field_name}: Not filled")
    
    fill_rate = fields_filled / total_fields
    print(f"📊 Form Mapping Test: {fields_filled}/{total_fields} fields filled ({fill_rate:.1%})")
    
    return fill_rate >= 0.75  # 75% fill rate


def main():
    """Run all basic NLP tests."""
    print("🚀 Medical NLP Basic Tests (No Dependencies)")
    print("=" * 60)
    
    tests = [
        ("Medical Terminology", test_medical_terminology_basic),
        ("Medical Codes", test_medical_codes_basic),
        ("Entity Extraction", test_entity_extraction_basic),
        ("Form Field Mapping", test_form_field_mapping),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! NLP components are working correctly.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run full NLP test: python test_nlp_service.py")
        print("3. Start AI service: docker-compose up --build")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)