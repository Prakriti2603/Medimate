from setuptools import setup, find_packages

setup(
    name="medimate-ai-service",
    version="1.0.0",
    description="AI-powered medical form auto-fill service for MediMate",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "tensorflow>=2.13.0",
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "spacy>=3.6.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "PyPDF2>=3.0.0",
        "pytesseract>=0.3.10",
        "opencv-python>=4.8.0",
        "scikit-learn>=1.3.0",
        "mlflow>=2.5.0",
        "redis>=4.6.0",
        "cryptography>=41.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)