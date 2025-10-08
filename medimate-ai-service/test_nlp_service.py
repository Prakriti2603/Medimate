#!/usr/bin/env python3
"""
Test the Medical NLP Service functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from services.nlp.nlp_service import MedicalNLPService
from services.nlp.medical_codes import CodeSystem


async def test_nlp_service():
    """Test the integrated NLP service."""
    print("🧪 Testing Medical NLP Service")
    print("=" * 50)
    
    # Initialize service
    nlp_service = MedicalNLPService()
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Test 1: Service Status
    print("\n📊 Testing Service Status...")
    status = await nlp_service.get_service_status()
    print(f"✅ Service initialized: {status['is_initialized']}")
    print(f"📈 Terminology terms: {status['terminology_stats'].get('total_terms', 0)}")
    print(f"🏥 Medical codes: {status['code_stats'].get('total_codes', 0)}")
    
    # Test 2: Process Medical Document
    print("\n📄 Testing Medical Document Processing...")
    
    sample_text = """
    Patient John Doe, age 45, presents with chest pain and shortness of breath.
    Blood pressure is 160/95 mmHg. Patient has a history of hypertension and diabetes.
    Prescribed metoprolol 50mg twice daily and lisinopril 10mg once daily.
    Insurance ID: INS123456. Follow-up in 2 weeks.
    """
    
    try:
        result = await nlp_service.process_medical_document(sample_text, "clinical_note")
        
        print(f"✅ Processing completed in {result['document_analysis']['processing_time']:.2f}s")
        print(f"📊 Confidence: {result['document_analysis']['confidence']:.2f}")
        print(f"🏷️  Entities found: {len(result['entities'])}")
        print(f"🏥 Medical codes: {len(result['medical_codes'])}")
        
        # Show some entities
        print("\n🏷️  Sample Entities:")
        for entity in result['entities'][:5]:
            print(f"  - {entity['text']} ({entity['label']}) - {entity['confidence']:.2f}")
        
        # Show form fields
        print("\n📝 Form Fields Extracted:")
        form_fields = result['form_fields']
        if form_fields.get('patient_demographics'):
            demo = form_fields['patient_demographics']
            if 'name' in demo:
                print(f"  Patient Name: {demo['name']['value']} ({demo['name']['confidence']:.2f})")
            if 'age' in demo:
                print(f"  Age: {demo['age']['value']} ({demo['age']['confidence']:.2f})")
        
        if form_fields.get('vital_signs'):
            vitals = form_fields['vital_signs']
            if 'blood_pressure' in vitals:
                print(f"  Blood Pressure: {vitals['blood_pressure']['value']} ({vitals['blood_pressure']['confidence']:.2f})")
        
        if form_fields.get('medications'):
            print(f"  Medications: {len(form_fields['medications'])} found")
            for med in form_fields['medications'][:2]:
                print(f"    - {med['name']} ({med['confidence']:.2f})")
        
        # Show insights
        print("\n💡 Clinical Insights:")
        insights = result['insights']
        for note in insights.get('clinical_notes', []):
            print(f"  - {note}")
        
        for risk in insights.get('risk_factors', []):
            print(f"  ⚠️  Risk: {risk['condition']} ({risk['confidence']:.2f})")
        
        # Show suggestions
        print("\n💭 Suggestions:")
        for suggestion in result['suggestions']:
            priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🟢"
            print(f"  {priority_icon} {suggestion['message']}")
        
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        return False
    
    # Test 3: Auto-fill Form
    print("\n📋 Testing Form Auto-Fill...")
    
    form_template = {
        'patient_name': {'type': 'text', 'category': 'demographics'},
        'patient_age': {'type': 'number', 'category': 'demographics'},
        'primary_diagnosis': {'type': 'text', 'category': 'medical'},
        'blood_pressure': {'type': 'text', 'category': 'vitals'},
        'current_medications': {'type': 'text', 'category': 'medications'},
        'insurance_number': {'type': 'text', 'category': 'insurance'}
    }
    
    try:
        form_result = await nlp_service.auto_fill_form(sample_text, form_template)
        
        print(f"✅ Form auto-fill completed")
        print(f"📊 Overall confidence: {form_result['overall_confidence']:.2f}")
        print(f"📝 Fields filled: {form_result['fields_filled']}/{form_result['total_fields']}")
        
        print("\n📋 Filled Form Fields:")
        for field_name, field_data in form_result['filled_form'].items():
            if field_data['value']:
                status = "✅" if not field_data['requires_review'] else "⚠️"
                print(f"  {status} {field_name}: {field_data['value']} ({field_data['confidence']:.2f})")
            else:
                print(f"  ❌ {field_name}: Not filled")
        
    except Exception as e:
        print(f"❌ Form auto-fill failed: {e}")
        return False
    
    # Test 4: Medical Code Search
    print("\n🔍 Testing Medical Code Search...")
    
    try:
        # Test code search
        search_results = nlp_service.code_manager.search_codes("hypertension", limit=3)
        print(f"✅ Found {len(search_results)} codes for 'hypertension':")
        for result in search_results:
            print(f"  - {result['code']} ({result['system']}): {result['description']} ({result['confidence']:.2f})")
        
        # Test code validation
        validation = nlp_service.code_manager.validate_code("I10", CodeSystem.ICD10_CM)
        if validation['is_valid']:
            print(f"✅ Code I10 validated: {validation['description']}")
        else:
            print(f"❌ Code validation failed: {validation['message']}")
        
    except Exception as e:
        print(f"❌ Code search failed: {e}")
        return False
    
    # Test 5: Terminology Normalization
    print("\n📚 Testing Medical Terminology...")
    
    try:
        # Test term normalization
        test_terms = ["htn", "dm", "high blood pressure", "heart attack"]
        
        print("✅ Term Normalization Results:")
        for term in test_terms:
            normalized = nlp_service.terminology_manager.normalize_term(term)
            if normalized:
                print(f"  '{term}' → '{normalized}'")
            else:
                print(f"  '{term}' → Not recognized")
        
        # Test term suggestions
        suggestions = nlp_service.terminology_manager.get_term_suggestions("diab", limit=3)
        print(f"\n✅ Suggestions for 'diab': {len(suggestions)} found")
        for suggestion in suggestions:
            print(f"  - {suggestion['term']} ({suggestion['category']}) - {suggestion['confidence']:.2f}")
        
    except Exception as e:
        print(f"❌ Terminology test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All NLP Service Tests Completed Successfully!")
    print("=" * 50)
    
    return True


async def test_complex_document():
    """Test with a more complex medical document."""
    print("\n🏥 Testing Complex Medical Document...")
    
    complex_text = """
    DISCHARGE SUMMARY
    
    Patient: Sarah Wilson
    DOB: 03/15/1978
    MRN: 12345678
    Insurance: BC123789
    
    CHIEF COMPLAINT: Severe headache for 3 days
    
    HISTORY OF PRESENT ILLNESS:
    45-year-old female presents with severe headache, photophobia, and nausea.
    Patient has history of migraines but states this is different and more severe.
    Blood pressure on admission was 180/110 mmHg.
    
    PAST MEDICAL HISTORY:
    - Hypertension
    - Diabetes mellitus type 2
    - Migraine headaches
    
    MEDICATIONS:
    - Lisinopril 10mg daily
    - Metformin 1000mg twice daily
    - Sumatriptan 50mg as needed for migraines
    
    PHYSICAL EXAMINATION:
    Vital Signs: BP 180/110, HR 88, RR 16, Temp 98.6°F
    Patient appears uncomfortable, photophobic
    
    ASSESSMENT AND PLAN:
    1. Hypertensive crisis - increase lisinopril to 20mg daily
    2. Severe headache - rule out secondary causes
    3. Diabetes - continue current regimen
    
    DISCHARGE MEDICATIONS:
    - Lisinopril 20mg daily
    - Metformin 1000mg BID
    - Sumatriptan 50mg PRN
    
    Follow-up with primary care in 1 week.
    """
    
    nlp_service = MedicalNLPService()
    await asyncio.sleep(1)  # Wait for initialization
    
    try:
        result = await nlp_service.process_medical_document(complex_text, "discharge_summary")
        
        print(f"✅ Complex document processed")
        print(f"📊 Entities: {len(result['entities'])}")
        print(f"🏥 Medical codes: {len(result['medical_codes'])}")
        print(f"💡 Insights: {len(result['insights']['clinical_notes'])}")
        
        # Show key extracted information
        form_fields = result['form_fields']
        
        print("\n📋 Key Information Extracted:")
        if form_fields.get('patient_demographics', {}).get('name'):
            print(f"  Patient: {form_fields['patient_demographics']['name']['value']}")
        
        if form_fields.get('medical_history', {}).get('primary_diagnosis'):
            print(f"  Primary Diagnosis: {form_fields['medical_history']['primary_diagnosis']['value']}")
        
        medications = form_fields.get('medications', [])
        if medications:
            print(f"  Medications: {len(medications)} found")
            for med in medications[:3]:
                dosage_info = f" - {med['dosage']['value']}" if 'dosage' in med else ""
                print(f"    • {med['name']}{dosage_info}")
        
        vitals = form_fields.get('vital_signs', {})
        if vitals:
            print("  Vital Signs:")
            for vital_name, vital_data in vitals.items():
                print(f"    • {vital_name}: {vital_data['value']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complex document test failed: {e}")
        return False


async def main():
    """Run all NLP tests."""
    print("🚀 Starting Medical NLP Service Tests")
    print("=" * 60)
    
    try:
        # Basic service tests
        success1 = await test_nlp_service()
        
        # Complex document test
        success2 = await test_complex_document()
        
        if success1 and success2:
            print("\n🎉 ALL TESTS PASSED! Medical NLP Service is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)