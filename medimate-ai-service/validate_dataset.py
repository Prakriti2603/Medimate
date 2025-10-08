#!/usr/bin/env python3
"""
Simple dataset validation script that doesn't require external dependencies.
"""

import json
import argparse
from pathlib import Path


def validate_dataset(file_path, dataset_type):
    """Validate dataset format."""
    print(f"🧪 Validating dataset: {file_path}")
    print(f"📊 Dataset type: {dataset_type}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ Dataset should be a list of examples")
            return False
        
        if len(data) == 0:
            print("❌ Dataset is empty")
            return False
        
        print(f"📈 Total examples: {len(data)}")
        
        # Validate structure based on type
        issues = []
        labels = set()
        field_types = set()
        entity_types = set()
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                issues.append(f"Example {i}: Not a dictionary")
                continue
            
            # Check text field
            if 'text' not in item or not item['text']:
                issues.append(f"Example {i}: Missing or empty 'text' field")
            
            # Type-specific validation
            if dataset_type == 'classification':
                if 'label' not in item:
                    issues.append(f"Example {i}: Missing 'label' field")
                else:
                    labels.add(item['label'])
            
            elif dataset_type == 'ner':
                if 'entities' not in item:
                    issues.append(f"Example {i}: Missing 'entities' field")
                elif not isinstance(item['entities'], list):
                    issues.append(f"Example {i}: 'entities' should be a list")
                else:
                    for j, entity in enumerate(item['entities']):
                        if not isinstance(entity, dict):
                            issues.append(f"Example {i}, Entity {j}: Not a dictionary")
                            continue
                        
                        required_fields = ['start', 'end', 'label']
                        for field in required_fields:
                            if field not in entity:
                                issues.append(f"Example {i}, Entity {j}: Missing '{field}' field")
                        
                        if 'label' in entity:
                            entity_types.add(entity['label'])
            
            elif dataset_type == 'field_extraction':
                if 'annotations' not in item:
                    issues.append(f"Example {i}: Missing 'annotations' field")
                elif not isinstance(item['annotations'], list):
                    issues.append(f"Example {i}: 'annotations' should be a list")
                else:
                    for j, annotation in enumerate(item['annotations']):
                        if not isinstance(annotation, dict):
                            issues.append(f"Example {i}, Annotation {j}: Not a dictionary")
                            continue
                        
                        required_fields = ['field_type', 'value', 'start_pos', 'end_pos']
                        for field in required_fields:
                            if field not in annotation:
                                issues.append(f"Example {i}, Annotation {j}: Missing '{field}' field")
                        
                        if 'field_type' in annotation:
                            field_types.add(annotation['field_type'])
        
        # Report issues
        if issues:
            print(f"⚠️  Found {len(issues)} validation issues:")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"   - {issue}")
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more issues")
        
        # Show statistics
        if dataset_type == 'classification' and labels:
            print(f"🏷️  Labels found: {sorted(labels)}")
            
            # Count label distribution
            label_counts = {}
            for item in data:
                label = item.get('label', 'UNKNOWN')
                label_counts[label] = label_counts.get(label, 0) + 1
            
            print("📊 Label distribution:")
            for label, count in sorted(label_counts.items()):
                print(f"   {label}: {count}")
        
        elif dataset_type == 'ner' and entity_types:
            print(f"🏷️  Entity types found: {sorted(entity_types)}")
            
            # Count entities
            total_entities = sum(len(item.get('entities', [])) for item in data)
            avg_entities = total_entities / len(data) if data else 0
            print(f"📊 Total entities: {total_entities}")
            print(f"📊 Average entities per example: {avg_entities:.1f}")
        
        elif dataset_type == 'field_extraction' and field_types:
            print(f"🏷️  Field types found: {sorted(field_types)}")
            
            # Count fields
            total_fields = sum(len(item.get('annotations', [])) for item in data)
            avg_fields = total_fields / len(data) if data else 0
            print(f"📊 Total field annotations: {total_fields}")
            print(f"📊 Average fields per example: {avg_fields:.1f}")
        
        # Calculate text statistics
        text_lengths = [len(item.get('text', '')) for item in data]
        avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        min_length = min(text_lengths) if text_lengths else 0
        max_length = max(text_lengths) if text_lengths else 0
        
        print(f"📝 Text statistics:")
        print(f"   Average length: {avg_length:.1f} characters")
        print(f"   Min length: {min_length} characters")
        print(f"   Max length: {max_length} characters")
        
        # Final assessment
        if len(issues) == 0:
            print("✅ Dataset validation passed!")
            return True
        elif len(issues) < len(data) * 0.1:  # Less than 10% issues
            print("⚠️  Dataset has minor issues but is mostly valid")
            return True
        else:
            print("❌ Dataset has significant issues")
            return False
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def create_sample_dataset(output_path, dataset_type, num_samples=10):
    """Create a sample dataset for testing."""
    print(f"🔧 Creating sample dataset: {output_path}")
    print(f"📊 Type: {dataset_type}, Samples: {num_samples}")
    
    sample_data = []
    
    if dataset_type == 'classification':
        categories = ['CARDIOLOGY', 'NEUROLOGY', 'ORTHOPEDICS', 'PEDIATRICS', 'EMERGENCY']
        sample_texts = [
            "Patient presents with chest pain and shortness of breath.",
            "Severe headache with visual disturbances reported.",
            "Fractured left tibia from sports injury.",
            "Child with fever and sore throat symptoms.",
            "Emergency trauma case with multiple injuries."
        ]
        
        for i in range(num_samples):
            sample_data.append({
                'text': sample_texts[i % len(sample_texts)] + f" Case #{i+1}",
                'label': categories[i % len(categories)]
            })
    
    elif dataset_type == 'ner':
        for i in range(num_samples):
            name = f"John Doe {i}"
            age = 25 + i % 50
            condition = f"condition {i}"
            medication = f"medication {i}"
            
            text = f"Patient {name}, age {age}, diagnosed with {condition}. Prescribed {medication}."
            
            entities = [
                {'start': text.find(name), 'end': text.find(name) + len(name), 'label': 'PATIENT_NAME'},
                {'start': text.find(str(age)), 'end': text.find(str(age)) + len(str(age)), 'label': 'AGE'},
                {'start': text.find(condition), 'end': text.find(condition) + len(condition), 'label': 'DIAGNOSIS'},
                {'start': text.find(medication), 'end': text.find(medication) + len(medication), 'label': 'MEDICATION'}
            ]
            
            sample_data.append({
                'text': text,
                'entities': entities
            })
    
    elif dataset_type == 'field_extraction':
        for i in range(num_samples):
            name = f"John Doe {i}"
            age = 25 + i % 50
            insurance = f"INS{1000 + i}"
            
            text = f"Patient: {name}, Age: {age}, Insurance: {insurance}"
            
            annotations = [
                {'field_type': 'patient_name', 'value': name, 'start_pos': text.find(name), 'end_pos': text.find(name) + len(name)},
                {'field_type': 'age', 'value': str(age), 'start_pos': text.find(str(age)), 'end_pos': text.find(str(age)) + len(str(age))},
                {'field_type': 'insurance_id', 'value': insurance, 'start_pos': text.find(insurance), 'end_pos': text.find(insurance) + len(insurance)}
            ]
            
            sample_data.append({
                'text': text,
                'annotations': annotations
            })
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sample dataset created: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample dataset: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Validate medical training datasets')
    parser.add_argument('--action', choices=['validate', 'sample'], required=True,
                       help='Action to perform')
    parser.add_argument('--input', help='Input dataset file (for validate)')
    parser.add_argument('--output', help='Output file path (for sample)')
    parser.add_argument('--type', choices=['ner', 'classification', 'field_extraction'], 
                       required=True, help='Dataset type')
    parser.add_argument('--samples', type=int, default=10, help='Number of samples (for sample action)')
    
    args = parser.parse_args()
    
    if args.action == 'validate':
        if not args.input:
            print("❌ --input is required for validate action")
            return 1
        
        success = validate_dataset(args.input, args.type)
        return 0 if success else 1
    
    elif args.action == 'sample':
        if not args.output:
            print("❌ --output is required for sample action")
            return 1
        
        success = create_sample_dataset(args.output, args.type, args.samples)
        return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)