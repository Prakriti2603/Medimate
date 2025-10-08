#!/usr/bin/env python3
"""
Dataset preparation script for medical training data.
Converts various formats to the required training format.
"""

import argparse
import json
import pandas as pd
import logging
from pathlib import Path
import sys

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from services.training.data_loader import MedicalDataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_csv_to_training_format(csv_path: str, output_path: str, format_type: str):
    """Convert CSV data to training format."""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")
        
        training_data = []
        
        if format_type == 'classification':
            # Expect columns: text, label
            for _, row in df.iterrows():
                training_data.append({
                    'text': str(row.get('text', '')),
                    'label': str(row.get('label', row.get('category', 'UNKNOWN')))
                })
        
        elif format_type == 'ner':
            # Expect columns: text, entities (JSON string)
            for _, row in df.iterrows():
                entities_str = row.get('entities', '[]')
                try:
                    entities = json.loads(entities_str) if isinstance(entities_str, str) else entities_str
                except:
                    entities = []
                
                training_data.append({
                    'text': str(row.get('text', '')),
                    'entities': entities
                })
        
        elif format_type == 'field_extraction':
            # Expect columns: text, annotations (JSON string)
            for _, row in df.iterrows():
                annotations_str = row.get('annotations', row.get('fields', '[]'))
                try:
                    annotations = json.loads(annotations_str) if isinstance(annotations_str, str) else annotations_str
                except:
                    annotations = []
                
                training_data.append({
                    'text': str(row.get('text', '')),
                    'annotations': annotations
                })
        
        # Save converted data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Converted {len(training_data)} examples to {output_path}")
        
    except Exception as e:
        logger.error(f"CSV conversion failed: {e}")
        raise


def validate_training_data(data_path: str, data_type: str):
    """Validate training data format."""
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Validating {len(data)} examples...")
        
        issues = []
        
        for i, item in enumerate(data[:10]):  # Check first 10 items
            if not isinstance(item, dict):
                issues.append(f"Item {i}: Not a dictionary")
                continue
            
            if 'text' not in item or not item['text']:
                issues.append(f"Item {i}: Missing or empty 'text' field")
            
            if data_type == 'classification':
                if 'label' not in item:
                    issues.append(f"Item {i}: Missing 'label' field")
            
            elif data_type == 'ner':
                if 'entities' not in item:
                    issues.append(f"Item {i}: Missing 'entities' field")
                elif not isinstance(item['entities'], list):
                    issues.append(f"Item {i}: 'entities' should be a list")
            
            elif data_type == 'field_extraction':
                if 'annotations' not in item:
                    issues.append(f"Item {i}: Missing 'annotations' field")
                elif not isinstance(item['annotations'], list):
                    issues.append(f"Item {i}: 'annotations' should be a list")
        
        if issues:
            logger.warning("Validation issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("Validation passed!")
        
        # Print statistics
        if data_type == 'classification':
            labels = [item.get('label', 'UNKNOWN') for item in data]
            label_counts = {}
            for label in labels:
                label_counts[label] = label_counts.get(label, 0) + 1
            
            logger.info("Label distribution:")
            for label, count in sorted(label_counts.items()):
                logger.info(f"  {label}: {count}")
        
        elif data_type == 'ner':
            entity_types = set()
            total_entities = 0
            for item in data:
                entities = item.get('entities', [])
                total_entities += len(entities)
                for entity in entities:
                    if isinstance(entity, dict) and 'label' in entity:
                        entity_types.add(entity['label'])
            
            logger.info(f"Total entities: {total_entities}")
            logger.info(f"Entity types: {sorted(entity_types)}")
        
        elif data_type == 'field_extraction':
            field_types = set()
            total_fields = 0
            for item in data:
                annotations = item.get('annotations', [])
                total_fields += len(annotations)
                for annotation in annotations:
                    if isinstance(annotation, dict) and 'field_type' in annotation:
                        field_types.add(annotation['field_type'])
            
            logger.info(f"Total field annotations: {total_fields}")
            logger.info(f"Field types: {sorted(field_types)}")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise


def create_sample_dataset(output_path: str, data_type: str, num_samples: int = 100):
    """Create a sample dataset for testing."""
    try:
        sample_data = []
        
        if data_type == 'classification':
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
        
        elif data_type == 'ner':
            for i in range(num_samples):
                text = f"Patient John Doe {i}, age {25 + i % 50}, diagnosed with condition {i}. Prescribed medication {i}."
                entities = [
                    {'start': 8, 'end': 8 + len(f"John Doe {i}"), 'label': 'PATIENT_NAME'},
                    {'start': text.find(f'{25 + i % 50}'), 'end': text.find(f'{25 + i % 50}') + len(str(25 + i % 50)), 'label': 'AGE'}
                ]
                sample_data.append({
                    'text': text,
                    'entities': entities
                })
        
        elif data_type == 'field_extraction':
            for i in range(num_samples):
                text = f"Patient: John Doe {i}, Age: {25 + i % 50}, Diagnosis: Condition {i}"
                annotations = [
                    {'field_type': 'patient_name', 'value': f'John Doe {i}', 'start_pos': 9, 'end_pos': 9 + len(f"John Doe {i}")},
                    {'field_type': 'age', 'value': str(25 + i % 50), 'start_pos': text.find(str(25 + i % 50)), 'end_pos': text.find(str(25 + i % 50)) + len(str(25 + i % 50))}
                ]
                sample_data.append({
                    'text': text,
                    'annotations': annotations
                })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created sample dataset with {num_samples} examples: {output_path}")
        
    except Exception as e:
        logger.error(f"Sample dataset creation failed: {e}")
        raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Prepare medical training datasets')
    parser.add_argument('--action', choices=['convert', 'validate', 'sample'], required=True,
                       help='Action to perform')
    parser.add_argument('--input', help='Input file path (for convert/validate)')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--type', choices=['ner', 'classification', 'field_extraction'], 
                       required=True, help='Dataset type')
    parser.add_argument('--samples', type=int, default=100, help='Number of samples for sample dataset')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'convert':
            if not args.input or not args.output:
                logger.error("Both --input and --output are required for convert action")
                return
            
            convert_csv_to_training_format(args.input, args.output, args.type)
        
        elif args.action == 'validate':
            if not args.input:
                logger.error("--input is required for validate action")
                return
            
            validate_training_data(args.input, args.type)
        
        elif args.action == 'sample':
            if not args.output:
                logger.error("--output is required for sample action")
                return
            
            create_sample_dataset(args.output, args.type, args.samples)
        
        logger.info("Operation completed successfully!")
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise


if __name__ == "__main__":
    main()