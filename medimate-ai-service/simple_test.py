#!/usr/bin/env python3
"""
Simple test runner that validates the AI training pipeline structure
without requiring external dependencies.
"""

import json
import os
import sys
from pathlib import Path


def test_file_structure():
    """Test that all required files are present."""
    print("🧪 Testing file structure...")
    
    base_path = Path(__file__).parent
    required_files = [
        "main.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "config/settings.py",
        "services/training/model_trainer.py",
        "services/training/data_loader.py",
        "services/document_processor.py",
        "utils/validation.py",
        "api/routes/document_processing.py",
        "api/routes/model_management.py",
        "scripts/train_model.py",
        "scripts/prepare_dataset.py",
        "data/training/example_medical_dataset.json",
        "data/training/training_config_examples.json",
        "TRAINING_GUIDE.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True


def test_example_dataset():
    """Test the example medical dataset format."""
    print("\n🧪 Testing example dataset...")
    
    dataset_path = Path(__file__).parent / "data" / "training" / "example_medical_dataset.json"
    
    if not dataset_path.exists():
        print("❌ Example dataset not found")
        return False
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ Dataset should be a list")
            return False
        
        if len(data) == 0:
            print("❌ Dataset is empty")
            return False
        
        # Check first item structure
        first_item = data[0]
        required_fields = ['text', 'entities', 'annotations', 'label']
        
        for field in required_fields:
            if field not in first_item:
                print(f"❌ Missing field '{field}' in dataset")
                return False
        
        # Validate entities structure
        entities = first_item['entities']
        if not isinstance(entities, list):
            print("❌ Entities should be a list")
            return False
        
        if len(entities) > 0:
            entity = entities[0]
            entity_fields = ['start', 'end', 'label']
            for field in entity_fields:
                if field not in entity:
                    print(f"❌ Missing field '{field}' in entity")
                    return False
        
        # Validate annotations structure
        annotations = first_item['annotations']
        if not isinstance(annotations, list):
            print("❌ Annotations should be a list")
            return False
        
        if len(annotations) > 0:
            annotation = annotations[0]
            annotation_fields = ['field_type', 'value', 'start_pos', 'end_pos']
            for field in annotation_fields:
                if field not in annotation:
                    print(f"❌ Missing field '{field}' in annotation")
                    return False
        
        print(f"✅ Dataset format valid ({len(data)} examples)")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False
    except Exception as e:
        print(f"❌ Dataset validation error: {e}")
        return False


def test_training_configs():
    """Test training configuration examples."""
    print("\n🧪 Testing training configurations...")
    
    config_path = Path(__file__).parent / "data" / "training" / "training_config_examples.json"
    
    if not config_path.exists():
        print("❌ Training config examples not found")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        
        required_configs = ['ner_training_config', 'classification_training_config', 'field_extraction_training_config']
        
        for config_name in required_configs:
            if config_name not in configs:
                print(f"❌ Missing config: {config_name}")
                return False
            
            config = configs[config_name]
            required_fields = ['model_name', 'model_type', 'training_data_path', 'epochs', 'batch_size']
            
            for field in required_fields:
                if field not in config:
                    print(f"❌ Missing field '{field}' in {config_name}")
                    return False
        
        print(f"✅ Training configurations valid ({len(configs)} configs)")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False
    except Exception as e:
        print(f"❌ Config validation error: {e}")
        return False


def test_python_syntax():
    """Test that Python files have valid syntax."""
    print("\n🧪 Testing Python syntax...")
    
    base_path = Path(__file__).parent
    python_files = [
        "main.py",
        "config/settings.py",
        "services/training/model_trainer.py",
        "services/training/data_loader.py",
        "services/document_processor.py",
        "utils/validation.py",
        "scripts/train_model.py",
        "scripts/prepare_dataset.py"
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        full_path = base_path / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                compile(source, str(full_path), 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
            except Exception as e:
                # Other errors (like import errors) are expected without dependencies
                pass
    
    if syntax_errors:
        print(f"❌ Syntax errors found:")
        for error in syntax_errors:
            print(f"   {error}")
        return False
    else:
        print(f"✅ Python syntax valid ({len(python_files)} files checked)")
        return True


def test_docker_config():
    """Test Docker configuration."""
    print("\n🧪 Testing Docker configuration...")
    
    base_path = Path(__file__).parent
    
    # Check Dockerfile
    dockerfile_path = base_path / "Dockerfile"
    if not dockerfile_path.exists():
        print("❌ Dockerfile not found")
        return False
    
    try:
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
        
        required_commands = ['FROM', 'WORKDIR', 'COPY', 'RUN', 'EXPOSE', 'CMD']
        for command in required_commands:
            if command not in dockerfile_content:
                print(f"❌ Missing Docker command: {command}")
                return False
    except Exception as e:
        print(f"❌ Dockerfile validation error: {e}")
        return False
    
    # Check docker-compose.yml
    compose_path = base_path / "docker-compose.yml"
    if not compose_path.exists():
        print("❌ docker-compose.yml not found")
        return False
    
    print("✅ Docker configuration valid")
    return True


def test_requirements():
    """Test requirements.txt."""
    print("\n🧪 Testing requirements...")
    
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if not requirements_path.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        with open(requirements_path, 'r') as f:
            requirements = f.read()
        
        essential_packages = [
            'tensorflow',
            'torch',
            'transformers',
            'spacy',
            'fastapi',
            'PyPDF2',
            'pytesseract',
            'opencv-python',
            'scikit-learn',
            'mlflow'
        ]
        
        missing_packages = []
        for package in essential_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing essential packages: {missing_packages}")
            return False
        
        print("✅ Requirements file valid")
        return True
        
    except Exception as e:
        print(f"❌ Requirements validation error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 AI Training Pipeline Structure Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Example Dataset", test_example_dataset),
        ("Training Configurations", test_training_configs),
        ("Python Syntax", test_python_syntax),
        ("Docker Configuration", test_docker_config),
        ("Requirements", test_requirements),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    # Summary
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
    print(f"{'='*50}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The AI training pipeline is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start services: docker-compose up --build")
        print("3. Train your model: python scripts/train_model.py --config <config> --data <dataset> --model-type <type>")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues before proceeding.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)