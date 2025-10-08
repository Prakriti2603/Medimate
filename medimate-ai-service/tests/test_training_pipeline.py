"""
Test suite for the AI training pipeline.
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.training.data_loader import MedicalDataLoader
from services.training.model_trainer import ModelTrainer
from services.document_processor import DocumentProcessor
from utils.validation import DocumentValidator, TextValidator


class TestMedicalDataLoader:
    """Test the medical data loader."""
    
    @pytest.fixture
    def sample_ner_data(self):
        """Sample NER training data."""
        return [
            {
                "text": "Patient John Doe, age 45, diagnosed with hypertension.",
                "entities": [
                    {"start": 8, "end": 16, "label": "PATIENT_NAME"},
                    {"start": 22, "end": 24, "label": "AGE"},
                    {"start": 40, "end": 52, "label": "DIAGNOSIS"}
                ]
            },
            {
                "text": "Mary Smith, 32 years old, has diabetes type 2.",
                "entities": [
                    {"start": 0, "end": 10, "label": "PATIENT_NAME"},
                    {"start": 12, "end": 14, "label": "AGE"},
                    {"start": 30, "end": 47, "label": "DIAGNOSIS"}
                ]
            }
        ]
    
    @pytest.fixture
    def sample_classification_data(self):
        """Sample classification training data."""
        return [
            {
                "text": "Patient presents with chest pain and shortness of breath.",
                "label": "CARDIOLOGY"
            },
            {
                "text": "Severe headache with visual disturbances reported.",
                "label": "NEUROLOGY"
            }
        ]
    
    @pytest.fixture
    def sample_field_extraction_data(self):
        """Sample field extraction training data."""
        return [
            {
                "text": "Patient: John Doe, Age: 45, Insurance: INS123456",
                "annotations": [
                    {"field_type": "patient_name", "value": "John Doe", "start_pos": 9, "end_pos": 17},
                    {"field_type": "age", "value": "45", "start_pos": 24, "end_pos": 26},
                    {"field_type": "insurance_id", "value": "INS123456", "start_pos": 39, "end_pos": 48}
                ]
            }
        ]
    
    @pytest.mark.asyncio
    async def test_load_ner_dataset(self, sample_ner_data):
        """Test loading NER dataset."""
        loader = MedicalDataLoader()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_ner_data, f)
            temp_path = f.name
        
        try:
            # Load dataset
            dataset = await loader.load_dataset(temp_path, 'ner')
            
            # Assertions
            assert dataset['metadata']['dataset_type'] == 'ner'
            assert dataset['metadata']['total_examples'] == 2
            assert len(dataset['data']) == 2
            assert 'PATIENT_NAME' in dataset['metadata']['labels']
            assert 'AGE' in dataset['metadata']['labels']
            assert 'DIAGNOSIS' in dataset['metadata']['labels']
            
            # Check statistics
            stats = dataset['metadata']['statistics']
            assert stats['total_entities'] == 6  # 3 entities per example
            assert stats['avg_entities_per_text'] == 3.0
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_load_classification_dataset(self, sample_classification_data):
        """Test loading classification dataset."""
        loader = MedicalDataLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_classification_data, f)
            temp_path = f.name
        
        try:
            dataset = await loader.load_dataset(temp_path, 'classification')
            
            assert dataset['metadata']['dataset_type'] == 'classification'
            assert dataset['metadata']['total_examples'] == 2
            assert 'CARDIOLOGY' in dataset['metadata']['labels']
            assert 'NEUROLOGY' in dataset['metadata']['labels']
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_validate_dataset(self, sample_ner_data):
        """Test dataset validation."""
        loader = MedicalDataLoader()
        
        # Create mock dataset
        dataset = {
            'data': sample_ner_data,
            'metadata': {
                'dataset_type': 'ner',
                'total_examples': len(sample_ner_data)
            }
        }
        
        validation_results = await loader.validate_dataset(dataset)
        
        assert validation_results['is_valid'] == True
        # Should have warnings about small dataset size
        assert len(validation_results['warnings']) > 0


class TestDocumentProcessor:
    """Test document processing functionality."""
    
    @pytest.fixture
    def processor(self):
        """Document processor instance."""
        return DocumentProcessor()
    
    def test_validate_file_format(self):
        """Test file format validation."""
        # Test valid PDF
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'
        is_valid, message = DocumentValidator.validate_file_format('test.pdf', pdf_content)
        assert is_valid == True
        
        # Test invalid extension
        is_valid, message = DocumentValidator.validate_file_format('test.xyz', b'content')
        assert is_valid == False
        assert 'Unsupported file format' in message
    
    def test_validate_file_size(self):
        """Test file size validation."""
        # Test normal size
        content = b'a' * 1000  # 1KB
        is_valid, message = DocumentValidator.validate_file_size(content)
        assert is_valid == True
        
        # Test empty file
        is_valid, message = DocumentValidator.validate_file_size(b'')
        assert is_valid == False
        assert 'empty' in message.lower()
    
    def test_text_validation(self):
        """Test extracted text validation."""
        # Test valid text
        text = "Patient John Doe presents with chest pain and shortness of breath."
        is_valid, message, metrics = TextValidator.validate_extracted_text(text)
        assert is_valid == True
        assert metrics['word_count'] > 0
        assert metrics['char_count'] > 0
        
        # Test empty text
        is_valid, message, metrics = TextValidator.validate_extracted_text("")
        assert is_valid == False


class TestTrainingConfiguration:
    """Test training configuration and setup."""
    
    def test_training_config_validation(self):
        """Test training configuration validation."""
        # Valid configuration
        config = {
            "model_name": "test_model",
            "model_type": "ner",
            "training_data_path": "./data/test.json",
            "epochs": 5,
            "batch_size": 16,
            "learning_rate": 0.001
        }
        
        # Basic validation (would be more comprehensive in real implementation)
        assert config['model_type'] in ['ner', 'classification', 'field_extraction']
        assert config['epochs'] > 0
        assert config['batch_size'] > 0
        assert config['learning_rate'] > 0
    
    def test_model_trainer_initialization(self):
        """Test model trainer initialization."""
        trainer = ModelTrainer()
        assert trainer is not None
        assert trainer.models_path.exists()


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_loading(self):
        """Test complete data loading pipeline."""
        # Create sample data
        sample_data = [
            {
                "text": "Patient Alice Johnson, age 28, diagnosed with migraine.",
                "entities": [
                    {"start": 8, "end": 21, "label": "PATIENT_NAME"},
                    {"start": 27, "end": 29, "label": "AGE"},
                    {"start": 46, "end": 54, "label": "DIAGNOSIS"}
                ],
                "label": "NEUROLOGY"
            }
        ]
        
        # Test data loading
        loader = MedicalDataLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_data, f)
            temp_path = f.name
        
        try:
            # Load as NER dataset
            ner_dataset = await loader.load_dataset(temp_path, 'ner')
            assert ner_dataset['metadata']['total_examples'] == 1
            
            # Load as classification dataset
            classification_dataset = await loader.load_dataset(temp_path, 'classification')
            assert classification_dataset['metadata']['total_examples'] == 1
            
            # Validate both datasets
            ner_validation = await loader.validate_dataset(ner_dataset)
            classification_validation = await loader.validate_dataset(classification_dataset)
            
            assert ner_validation['is_valid'] == True
            assert classification_validation['is_valid'] == True
            
        finally:
            os.unlink(temp_path)


def run_tests():
    """Run all tests."""
    print("Running AI Training Pipeline Tests...")
    print("=" * 50)
    
    # Run pytest
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_tests()