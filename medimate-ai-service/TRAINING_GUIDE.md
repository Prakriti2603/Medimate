# Medical AI Model Training Guide

This guide explains how to train AI models on your medical dataset for automatic form filling and medical information extraction.

## Overview

The MediMate AI service supports training three types of models:

1. **Named Entity Recognition (NER)** - Extract medical entities like patient names, medications, diagnoses
2. **Document Classification** - Classify medical documents by type or specialty
3. **Field Extraction** - Extract specific form fields from medical text

## Quick Start

### 1. Prepare Your Dataset

Your medical dataset should be in JSON format. Here are the required formats:

#### For NER Training:
```json
[
  {
    "text": "Patient John Doe, age 45, diagnosed with hypertension.",
    "entities": [
      {"start": 8, "end": 16, "label": "PATIENT_NAME"},
      {"start": 22, "end": 24, "label": "AGE"},
      {"start": 40, "end": 52, "label": "DIAGNOSIS"}
    ]
  }
]
```

#### For Classification Training:
```json
[
  {
    "text": "Patient presents with chest pain and shortness of breath.",
    "label": "CARDIOLOGY"
  }
]
```

#### For Field Extraction Training:
```json
[
  {
    "text": "Patient: John Doe, Age: 45, Insurance: INS123456",
    "annotations": [
      {"field_type": "patient_name", "value": "John Doe", "start_pos": 9, "end_pos": 17},
      {"field_type": "age", "value": "45", "start_pos": 24, "end_pos": 26},
      {"field_type": "insurance_id", "value": "INS123456", "start_pos": 39, "end_pos": 48}
    ]
  }
]
```

### 2. Convert Your Data (if needed)

If your data is in CSV format, use the preparation script:

```bash
# Convert CSV to training format
python scripts/prepare_dataset.py --action convert --input your_data.csv --output training_data.json --type field_extraction

# Validate your dataset
python scripts/prepare_dataset.py --action validate --input training_data.json --type field_extraction
```

### 3. Create Training Configuration

Create a JSON configuration file (e.g., `my_training_config.json`):

```json
{
  "model_name": "my_medical_ai_v1",
  "model_type": "field_extraction",
  "training_data_path": "./data/training/my_dataset.json",
  "base_model": "bert-base-uncased",
  "epochs": 10,
  "batch_size": 16,
  "learning_rate": 3e-5,
  "validation_split": 0.2,
  "field_types": [
    "patient_name",
    "age",
    "diagnosis",
    "medication",
    "dosage",
    "insurance_id"
  ]
}
```

### 4. Train Your Model

```bash
# Train the model
python scripts/train_model.py --config my_training_config.json --data ./data/training/my_dataset.json --model-type field_extraction

# Validate data before training
python scripts/train_model.py --config my_training_config.json --data ./data/training/my_dataset.json --model-type field_extraction --validate-data

# Dry run (validate without training)
python scripts/train_model.py --config my_training_config.json --data ./data/training/my_dataset.json --model-type field_extraction --dry-run
```

## Dataset Requirements

### Minimum Dataset Size
- **NER**: 500+ examples with diverse entity types
- **Classification**: 100+ examples per class
- **Field Extraction**: 300+ examples with varied field combinations

### Data Quality Guidelines

1. **Text Quality**
   - Clean, readable medical text
   - Consistent formatting
   - Representative of real medical documents

2. **Annotation Quality**
   - Accurate entity boundaries
   - Consistent labeling scheme
   - Complete annotations (don't skip entities)

3. **Data Diversity**
   - Multiple medical specialties
   - Various document types
   - Different writing styles

## Training Configuration Options

### Basic Parameters
```json
{
  "model_name": "your_model_name",
  "model_type": "ner|classification|field_extraction",
  "training_data_path": "path/to/your/data.json",
  "base_model": "bert-base-uncased",
  "epochs": 10,
  "batch_size": 16,
  "learning_rate": 3e-5,
  "validation_split": 0.2
}
```

### Advanced Parameters
```json
{
  "early_stopping": true,
  "early_stopping_patience": 3,
  "save_best_model": true,
  "evaluation_strategy": "epoch",
  "logging_steps": 100,
  "warmup_ratio": 0.1,
  "weight_decay": 0.01,
  "max_length": 512,
  "gradient_accumulation_steps": 2
}
```

### Model Optimization
```json
{
  "model_optimization": {
    "use_mixed_precision": true,
    "gradient_checkpointing": true,
    "dataloader_num_workers": 4
  }
}
```

## Using Your Dataset

### Step 1: Analyze Your Data

First, understand your dataset structure:

```python
import json
import pandas as pd

# Load your data
with open('your_dataset.json', 'r') as f:
    data = json.load(f)

print(f"Total examples: {len(data)}")
print(f"Sample record: {data[0]}")

# If you have CSV data
df = pd.read_csv('your_data.csv')
print(df.head())
print(df.columns.tolist())
```

### Step 2: Prepare Training Data

Convert your data to the required format:

```python
# Example: Convert your custom format to training format
training_data = []

for record in your_data:
    # Extract text content
    text = record['medical_text']  # Adjust field name
    
    # For field extraction
    annotations = []
    for field_name, field_value in record['extracted_fields'].items():
        # Find position in text
        start_pos = text.find(field_value)
        if start_pos != -1:
            annotations.append({
                'field_type': field_name,
                'value': field_value,
                'start_pos': start_pos,
                'end_pos': start_pos + len(field_value)
            })
    
    training_data.append({
        'text': text,
        'annotations': annotations
    })

# Save training data
with open('prepared_training_data.json', 'w') as f:
    json.dump(training_data, f, indent=2)
```

### Step 3: Configure Training

Create a configuration file tailored to your data:

```json
{
  "model_name": "custom_medical_extractor",
  "model_type": "field_extraction",
  "training_data_path": "./data/training/prepared_training_data.json",
  "base_model": "distilbert-base-uncased",
  "epochs": 15,
  "batch_size": 32,
  "learning_rate": 5e-5,
  "validation_split": 0.15,
  "field_types": [
    "patient_name",
    "date_of_birth",
    "insurance_number",
    "primary_diagnosis",
    "medications",
    "allergies",
    "vital_signs",
    "lab_results"
  ],
  "hyperparameters": {
    "max_length": 768,
    "warmup_ratio": 0.1,
    "weight_decay": 0.01
  }
}
```

## Training Process

### 1. Data Loading and Validation
- Dataset is loaded and validated
- Statistics are calculated
- Data quality issues are reported

### 2. Model Initialization
- Base model is loaded (BERT, DistilBERT, etc.)
- Model architecture is configured for your task
- Training parameters are set

### 3. Training Loop
- Model trains on your data
- Validation is performed each epoch
- Best model is saved based on validation metrics
- Training progress is logged to MLflow

### 4. Model Evaluation
- Final model performance is evaluated
- Metrics are calculated and reported
- Model is saved for deployment

## Monitoring Training

### MLflow Integration

Training metrics are automatically logged to MLflow:

```bash
# Start MLflow UI (if not using Docker)
mlflow ui --host 0.0.0.0 --port 5000

# View at http://localhost:5000
```

### Key Metrics to Monitor

- **Accuracy**: Overall prediction accuracy
- **Precision**: Correct positive predictions / Total positive predictions
- **Recall**: Correct positive predictions / Total actual positives
- **F1-Score**: Harmonic mean of precision and recall
- **Loss**: Training and validation loss curves

## Model Deployment

After training, your model is automatically saved and can be deployed:

```python
# Load trained model
from services.training.model_trainer import ModelTrainer

trainer = ModelTrainer()
# Model loading and inference code here
```

## Troubleshooting

### Common Issues

1. **Out of Memory**
   - Reduce batch_size
   - Use gradient_accumulation_steps
   - Enable gradient_checkpointing

2. **Poor Performance**
   - Increase dataset size
   - Improve data quality
   - Adjust learning rate
   - Try different base models

3. **Overfitting**
   - Increase validation_split
   - Add regularization (weight_decay)
   - Use early stopping
   - Reduce model complexity

4. **Slow Training**
   - Enable mixed precision training
   - Use GPU acceleration
   - Increase batch_size (if memory allows)
   - Use dataloader_num_workers

### Performance Optimization

```json
{
  "model_optimization": {
    "use_mixed_precision": true,
    "gradient_checkpointing": true,
    "dataloader_num_workers": 4,
    "pin_memory": true
  },
  "training_optimization": {
    "gradient_accumulation_steps": 4,
    "max_grad_norm": 1.0,
    "warmup_steps": 1000
  }
}
```

## Best Practices

1. **Data Preparation**
   - Clean and normalize your text data
   - Ensure consistent annotation format
   - Balance your dataset across classes/entities
   - Use representative validation data

2. **Model Selection**
   - Start with DistilBERT for faster training
   - Use BERT-base for better accuracy
   - Consider domain-specific models (BioBERT, ClinicalBERT)

3. **Training Strategy**
   - Start with small epochs and adjust
   - Monitor validation metrics closely
   - Use early stopping to prevent overfitting
   - Save checkpoints regularly

4. **Evaluation**
   - Test on held-out data
   - Evaluate on real-world examples
   - Check for bias and fairness
   - Validate medical accuracy with experts

## Example: Complete Training Workflow

```bash
# 1. Prepare sample dataset
python scripts/prepare_dataset.py --action sample --output sample_data.json --type field_extraction --samples 500

# 2. Validate dataset
python scripts/prepare_dataset.py --action validate --input sample_data.json --type field_extraction

# 3. Train model
python scripts/train_model.py --config data/training/training_config_examples.json --data sample_data.json --model-type field_extraction --validate-data

# 4. Check results in MLflow UI
# Visit http://localhost:5000
```

This completes the training setup! Your model will be ready to integrate with the MediMate platform for automatic medical form filling.