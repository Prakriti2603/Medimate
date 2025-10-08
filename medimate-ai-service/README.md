# MediMate AI Service

AI-powered medical document processing and form auto-fill service for the MediMate healthcare platform.

## Features

- **Document Processing**: Extract medical information from PDFs, images, and handwritten documents
- **AI Form Auto-Fill**: Intelligently populate medical forms using extracted data
- **Medical NLP**: Advanced natural language processing for medical terminology
- **Model Training**: Train and deploy custom AI models for specific healthcare workflows
- **Real-time Processing**: Asynchronous document processing with progress tracking
- **HIPAA Compliance**: Secure, encrypted processing of sensitive medical data

## Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional)
- GPU support (optional, for faster processing)

### Installation

1. **Clone and navigate to the AI service directory:**
   ```bash
   cd medimate-ai-service
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download required models:**
   ```bash
   python -m spacy download en_core_web_sm
   python -m spacy download en_core_sci_sm
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the service:**
   ```bash
   python main.py
   ```

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

This will start:
- AI Service (port 8001)
- Redis (port 6379)
- MongoDB (port 27017)
- MLflow (port 5000)

## API Documentation

Once the service is running, visit:
- **API Documentation**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## Configuration

Key environment variables in `.env`:

```bash
# Service Configuration
AI_SERVICE_HOST=localhost
AI_SERVICE_PORT=8001
USE_GPU=true

# Model Configuration
MODEL_BASE_PATH=./models
TRAINING_DATA_PATH=./data/training
CONFIDENCE_THRESHOLD=0.85

# Database Configuration
REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017/medimate_ai

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
```

## Usage Examples

### Document Upload and Processing

```python
import requests

# Upload document
with open('medical_document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/v1/documents/upload',
        files={'file': f}
    )
    document_id = response.json()['document_id']

# Extract fields
extraction_response = requests.post(
    'http://localhost:8001/api/v1/documents/extract',
    json={'document_id': document_id}
)
extracted_data = extraction_response.json()
```

### Model Training

```python
# Start model training
training_request = {
    'model_name': 'custom_medical_ner',
    'training_data_path': './data/training/medical_ner_dataset.json',
    'model_type': 'ner',
    'hyperparameters': {
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 20
    }
}

response = requests.post(
    'http://localhost:8001/api/v1/models/train',
    json=training_request
)
training_id = response.json()['training_id']
```

## Development

### Project Structure

```
medimate-ai-service/
├── api/                    # API routes and endpoints
│   └── routes/
├── config/                 # Configuration management
├── core/                   # Core functionality
├── models/                 # AI model implementations
├── services/              # Business logic services
├── utils/                 # Utility functions
├── data/                  # Training and test data
├── logs/                  # Application logs
├── cache/                 # Caching directory
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── Dockerfile           # Container configuration
```

### Adding New Models

1. Create model class in `models/` directory
2. Implement training pipeline in `services/training/`
3. Add API endpoints in `api/routes/`
4. Update configuration as needed

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## Deployment

### Production Deployment

1. **Build production image:**
   ```bash
   docker build -t medimate-ai-service:latest .
   ```

2. **Deploy with environment-specific configuration:**
   ```bash
   docker run -d \
     --name medimate-ai \
     -p 8001:8001 \
     -e AI_SERVICE_HOST=0.0.0.0 \
     -e USE_GPU=true \
     -v /path/to/models:/app/models \
     medimate-ai-service:latest
   ```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

## Security

- All medical data is encrypted in transit and at rest
- HIPAA-compliant data handling and audit trails
- Secure model training with data anonymization
- API authentication and authorization

## Monitoring

- Health checks at `/health`, `/ready`, `/live`
- MLflow for experiment tracking
- Prometheus metrics (optional)
- Structured logging with rotation

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review logs in `logs/ai_service.log`
3. Monitor health endpoints for service status
4. Check MLflow UI for model performance metrics

## License

MIT License - see LICENSE file for details.