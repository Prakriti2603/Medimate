"""
Data loading utilities for medical training datasets.
Handles various medical data formats and preprocessing.
"""

import logging
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from config.settings import settings

logger = logging.getLogger(__name__)


class MedicalDataLoader:
    """Load and preprocess medical training datasets."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.supported_formats = ['.json', '.csv', '.xlsx', '.txt']
    
    async def load_dataset(self, data_path: str, dataset_type: str) -> Dict[str, Any]:
        """
        Load medical dataset based on type.
        
        Args:
            data_path: Path to dataset file
            dataset_type: Type of dataset (ner, classification, field_extraction)
            
        Returns:
            Loaded and preprocessed dataset
        """
        try:
            file_path = Path(data_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Dataset file not found: {data_path}")
            
            if file_path.suffix not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Load data based on file format
            loop = asyncio.get_event_loop()
            raw_data = await loop.run_in_executor(
                self.executor, self._load_file, str(file_path)
            )
            
            # Process data based on dataset type
            processed_data = await self._process_dataset(raw_data, dataset_type)
            
            logger.info(f"Dataset loaded successfully: {len(processed_data['data'])} examples")
            
            return {
                'data': processed_data['data'],
                'metadata': {
                    'source_file': str(file_path),
                    'dataset_type': dataset_type,
                    'total_examples': len(processed_data['data']),
                    'labels': processed_data.get('labels', []),
                    'statistics': processed_data.get('statistics', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Dataset loading failed: {e}")
            raise
    
    def _load_file(self, file_path: str) -> Union[List[Dict], pd.DataFrame]:
        """Load file based on format."""
        try:
            path = Path(file_path)
            
            if path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif path.suffix == '.csv':
                return pd.read_csv(file_path)
            
            elif path.suffix == '.xlsx':
                return pd.read_excel(file_path)
            
            elif path.suffix == '.txt':
                # Assume line-separated JSON objects
                data = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data.append(json.loads(line.strip()))
                return data
            
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
                
        except Exception as e:
            logger.error(f"File loading failed: {e}")
            raise
    
    async def _process_dataset(self, raw_data: Union[List[Dict], pd.DataFrame], dataset_type: str) -> Dict[str, Any]:
        """Process dataset based on type."""
        try:
            if dataset_type == 'ner':
                return await self._process_ner_dataset(raw_data)
            elif dataset_type == 'classification':
                return await self._process_classification_dataset(raw_data)
            elif dataset_type == 'field_extraction':
                return await self._process_field_extraction_dataset(raw_data)
            else:
                raise ValueError(f"Unsupported dataset type: {dataset_type}")
                
        except Exception as e:
            logger.error(f"Dataset processing failed: {e}")
            raise
    
    async def _process_ner_dataset(self, raw_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """Process NER dataset."""
        try:
            processed_data = []
            all_labels = set()
            
            if isinstance(raw_data, pd.DataFrame):
                # Convert DataFrame to list of dicts
                data_list = raw_data.to_dict('records')
            else:
                data_list = raw_data
            
            for item in data_list:
                # Extract text and entities
                text = item.get('text', '')
                entities = item.get('entities', [])
                
                # Validate and normalize entities
                normalized_entities = []
                for entity in entities:
                    if isinstance(entity, dict):
                        start = entity.get('start', 0)
                        end = entity.get('end', 0)
                        label = entity.get('label', 'UNKNOWN')
                        
                        normalized_entities.append({
                            'start': start,
                            'end': end,
                            'label': label,
                            'text': text[start:end] if start < len(text) and end <= len(text) else ''
                        })
                        all_labels.add(label)
                    elif isinstance(entity, (list, tuple)) and len(entity) >= 3:
                        # Format: [start, end, label]
                        start, end, label = entity[0], entity[1], entity[2]
                        normalized_entities.append({
                            'start': start,
                            'end': end,
                            'label': label,
                            'text': text[start:end] if start < len(text) and end <= len(text) else ''
                        })
                        all_labels.add(label)
                
                processed_data.append({
                    'text': text,
                    'entities': normalized_entities
                })
            
            # Calculate statistics
            statistics = {
                'total_entities': sum(len(item['entities']) for item in processed_data),
                'avg_entities_per_text': sum(len(item['entities']) for item in processed_data) / len(processed_data) if processed_data else 0,
                'avg_text_length': sum(len(item['text']) for item in processed_data) / len(processed_data) if processed_data else 0,
                'label_distribution': self._calculate_label_distribution(processed_data, 'entities')
            }
            
            return {
                'data': processed_data,
                'labels': list(all_labels),
                'statistics': statistics
            }
            
        except Exception as e:
            logger.error(f"NER dataset processing failed: {e}")
            raise
    
    async def _process_classification_dataset(self, raw_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """Process classification dataset."""
        try:
            processed_data = []
            all_labels = set()
            
            if isinstance(raw_data, pd.DataFrame):
                data_list = raw_data.to_dict('records')
            else:
                data_list = raw_data
            
            for item in data_list:
                text = item.get('text', '')
                label = item.get('label', item.get('category', 'UNKNOWN'))
                
                processed_data.append({
                    'text': text,
                    'label': label
                })
                all_labels.add(label)
            
            # Calculate statistics
            statistics = {
                'avg_text_length': sum(len(item['text']) for item in processed_data) / len(processed_data) if processed_data else 0,
                'label_distribution': self._calculate_label_distribution(processed_data, 'label')
            }
            
            return {
                'data': processed_data,
                'labels': list(all_labels),
                'statistics': statistics
            }
            
        except Exception as e:
            logger.error(f"Classification dataset processing failed: {e}")
            raise
    
    async def _process_field_extraction_dataset(self, raw_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """Process field extraction dataset."""
        try:
            processed_data = []
            all_field_types = set()
            
            if isinstance(raw_data, pd.DataFrame):
                data_list = raw_data.to_dict('records')
            else:
                data_list = raw_data
            
            for item in data_list:
                text = item.get('text', '')
                annotations = item.get('annotations', item.get('fields', []))
                
                # Normalize annotations
                normalized_annotations = []
                for annotation in annotations:
                    if isinstance(annotation, dict):
                        field_type = annotation.get('field_type', annotation.get('type', 'UNKNOWN'))
                        value = annotation.get('value', '')
                        start_pos = annotation.get('start', annotation.get('start_pos', 0))
                        end_pos = annotation.get('end', annotation.get('end_pos', 0))
                        
                        normalized_annotations.append({
                            'field_type': field_type,
                            'value': value,
                            'start_pos': start_pos,
                            'end_pos': end_pos,
                            'confidence': annotation.get('confidence', 1.0)
                        })
                        all_field_types.add(field_type)
                
                processed_data.append({
                    'text': text,
                    'annotations': normalized_annotations
                })
            
            # Calculate statistics
            statistics = {
                'total_fields': sum(len(item['annotations']) for item in processed_data),
                'avg_fields_per_document': sum(len(item['annotations']) for item in processed_data) / len(processed_data) if processed_data else 0,
                'avg_text_length': sum(len(item['text']) for item in processed_data) / len(processed_data) if processed_data else 0,
                'field_type_distribution': self._calculate_field_distribution(processed_data)
            }
            
            return {
                'data': processed_data,
                'labels': list(all_field_types),
                'statistics': statistics
            }
            
        except Exception as e:
            logger.error(f"Field extraction dataset processing failed: {e}")
            raise
    
    def _calculate_label_distribution(self, data: List[Dict], label_key: str) -> Dict[str, int]:
        """Calculate label distribution in dataset."""
        try:
            distribution = {}
            
            for item in data:
                if label_key == 'entities':
                    # For NER data
                    for entity in item.get('entities', []):
                        label = entity.get('label', 'UNKNOWN')
                        distribution[label] = distribution.get(label, 0) + 1
                else:
                    # For classification data
                    label = item.get(label_key, 'UNKNOWN')
                    distribution[label] = distribution.get(label, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Label distribution calculation failed: {e}")
            return {}
    
    def _calculate_field_distribution(self, data: List[Dict]) -> Dict[str, int]:
        """Calculate field type distribution for field extraction data."""
        try:
            distribution = {}
            
            for item in data:
                for annotation in item.get('annotations', []):
                    field_type = annotation.get('field_type', 'UNKNOWN')
                    distribution[field_type] = distribution.get(field_type, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Field distribution calculation failed: {e}")
            return {}
    
    async def validate_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dataset quality and completeness."""
        try:
            validation_results = {
                'is_valid': True,
                'warnings': [],
                'errors': [],
                'recommendations': []
            }
            
            data = dataset.get('data', [])
            dataset_type = dataset.get('metadata', {}).get('dataset_type', '')
            
            if not data:
                validation_results['errors'].append("Dataset is empty")
                validation_results['is_valid'] = False
                return validation_results
            
            # Check for minimum dataset size
            if len(data) < 100:
                validation_results['warnings'].append(f"Small dataset size: {len(data)} examples. Consider adding more data for better performance.")
            
            # Type-specific validation
            if dataset_type == 'ner':
                await self._validate_ner_dataset(data, validation_results)
            elif dataset_type == 'classification':
                await self._validate_classification_dataset(data, validation_results)
            elif dataset_type == 'field_extraction':
                await self._validate_field_extraction_dataset(data, validation_results)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Dataset validation failed: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'recommendations': []
            }
    
    async def _validate_ner_dataset(self, data: List[Dict], results: Dict[str, Any]):
        """Validate NER dataset."""
        empty_texts = 0
        no_entities = 0
        
        for item in data:
            text = item.get('text', '')
            entities = item.get('entities', [])
            
            if not text.strip():
                empty_texts += 1
            
            if not entities:
                no_entities += 1
        
        if empty_texts > 0:
            results['warnings'].append(f"{empty_texts} examples have empty text")
        
        if no_entities > len(data) * 0.5:
            results['warnings'].append(f"{no_entities} examples have no entities (>{50}% of dataset)")
    
    async def _validate_classification_dataset(self, data: List[Dict], results: Dict[str, Any]):
        """Validate classification dataset."""
        empty_texts = 0
        missing_labels = 0
        label_counts = {}
        
        for item in data:
            text = item.get('text', '')
            label = item.get('label', '')
            
            if not text.strip():
                empty_texts += 1
            
            if not label:
                missing_labels += 1
            else:
                label_counts[label] = label_counts.get(label, 0) + 1
        
        if empty_texts > 0:
            results['warnings'].append(f"{empty_texts} examples have empty text")
        
        if missing_labels > 0:
            results['errors'].append(f"{missing_labels} examples have missing labels")
            results['is_valid'] = False
        
        # Check for class imbalance
        if label_counts:
            max_count = max(label_counts.values())
            min_count = min(label_counts.values())
            if max_count / min_count > 10:
                results['warnings'].append("Significant class imbalance detected. Consider balancing your dataset.")
    
    async def _validate_field_extraction_dataset(self, data: List[Dict], results: Dict[str, Any]):
        """Validate field extraction dataset."""
        empty_texts = 0
        no_annotations = 0
        
        for item in data:
            text = item.get('text', '')
            annotations = item.get('annotations', [])
            
            if not text.strip():
                empty_texts += 1
            
            if not annotations:
                no_annotations += 1
        
        if empty_texts > 0:
            results['warnings'].append(f"{empty_texts} examples have empty text")
        
        if no_annotations > len(data) * 0.3:
            results['warnings'].append(f"{no_annotations} examples have no field annotations")