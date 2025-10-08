#!/usr/bin/env python3
"""
Training script for medical AI models.
Use this script to train models on your medical dataset.
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from services.training.model_trainer import ModelTrainer
from services.training.data_loader import MedicalDataLoader
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Train medical AI models')
    parser.add_argument('--config', required=True, help='Path to training configuration JSON file')
    parser.add_argument('--data', required=True, help='Path to training dataset')
    parser.add_argument('--model-type', choices=['ner', 'classification', 'field_extraction'], 
                       required=True, help='Type of model to train')
    parser.add_argument('--validate-data', action='store_true', help='Validate dataset before training')
    parser.add_argument('--dry-run', action='store_true', help='Validate configuration without training')
    
    args = parser.parse_args()
    
    try:
        # Load training configuration
        logger.info(f"Loading training configuration from: {args.config}")
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Override data path from command line
        config['training_data_path'] = args.data
        config['model_type'] = args.model_type
        
        logger.info(f"Training configuration loaded: {config.get('model_name', 'unnamed_model')}")
        
        # Initialize data loader and trainer
        data_loader = MedicalDataLoader()
        trainer = ModelTrainer()
        
        # Load and validate dataset
        logger.info(f"Loading dataset from: {args.data}")
        dataset = await data_loader.load_dataset(args.data, args.model_type)
        
        logger.info(f"Dataset loaded: {dataset['metadata']['total_examples']} examples")
        logger.info(f"Labels found: {dataset['metadata']['labels']}")
        
        if args.validate_data:
            logger.info("Validating dataset...")
            validation_results = await data_loader.validate_dataset(dataset)
            
            if not validation_results['is_valid']:
                logger.error("Dataset validation failed:")
                for error in validation_results['errors']:
                    logger.error(f"  - {error}")
                return
            
            if validation_results['warnings']:
                logger.warning("Dataset validation warnings:")
                for warning in validation_results['warnings']:
                    logger.warning(f"  - {warning}")
            
            logger.info("Dataset validation passed!")
        
        if args.dry_run:
            logger.info("Dry run completed successfully. Configuration and data are valid.")
            return
        
        # Start training
        logger.info("Starting model training...")
        training_result = await trainer.train_model(config)
        
        logger.info("Training completed successfully!")
        logger.info(f"Model saved to: {training_result['model_path']}")
        logger.info(f"Training metrics: {training_result['metrics']}")
        
        # Print summary
        print("\n" + "="*50)
        print("TRAINING SUMMARY")
        print("="*50)
        print(f"Model Name: {config.get('model_name', 'unnamed_model')}")
        print(f"Model Type: {args.model_type}")
        print(f"Dataset: {args.data}")
        print(f"Examples: {dataset['metadata']['total_examples']}")
        print(f"Model Path: {training_result['model_path']}")
        print("\nMetrics:")
        for metric, value in training_result['metrics'].items():
            print(f"  {metric}: {value:.4f}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())