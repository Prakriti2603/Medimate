import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './AIDocumentUpload.css';

const AIDocumentUpload = ({ onUploadComplete, onProcessingUpdate }) => {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);
    setProgress(0);

    try {
      // Upload file to AI service
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('http://localhost:8001/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }

      const uploadResult = await uploadResponse.json();
      const documentId = uploadResult.document_id;

      setUploading(false);
      setProcessing(true);
      setProgress(25);

      // Start AI processing
      if (onProcessingUpdate) {
        onProcessingUpdate({ status: 'processing', progress: 25 });
      }

      // Extract information from document
      const extractResponse = await fetch('http://localhost:8001/api/v1/documents/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          extraction_options: {}
        }),
      });

      if (!extractResponse.ok) {
        throw new Error('Extraction failed');
      }

      const extractResult = await extractResponse.json();
      setProgress(75);

      // Get comprehensive analysis
      const analysisResponse = await fetch('http://localhost:8001/api/v1/documents/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId
        }),
      });

      if (!analysisResponse.ok) {
        throw new Error('Analysis failed');
      }

      const analysisResult = await analysisResponse.json();
      setProgress(100);

      // Get form suggestions
      const suggestionsResponse = await fetch(`http://localhost:8001/api/v1/documents/suggestions/${documentId}`);
      const suggestions = suggestionsResponse.ok ? await suggestionsResponse.json() : null;

      setProcessing(false);

      if (onUploadComplete) {
        onUploadComplete({
          documentId,
          filename: file.name,
          extractionResult: extractResult,
          analysisResult: analysisResult,
          suggestions: suggestions
        });
      }

    } catch (err) {
      setError(err.message);
      setUploading(false);
      setProcessing(false);
      setProgress(0);
    }
  }, [onUploadComplete, onProcessingUpdate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff']
    },
    maxFiles: 1,
    disabled: uploading || processing
  });

  return (
    <div className="ai-document-upload">
      <div
        {...getRootProps()}
        className={`upload-dropzone ${isDragActive ? 'drag-active' : ''} ${
          uploading || processing ? 'disabled' : ''
        }`}
      >
        <input {...getInputProps()} />
        
        {!uploading && !processing && (
          <div className="upload-content">
            <div className="upload-icon">📄</div>
            <h3>AI-Powered Document Processing</h3>
            <p>
              {isDragActive
                ? 'Drop your medical document here...'
                : 'Drag & drop a medical document, or click to select'}
            </p>
            <p className="supported-formats">
              Supports: PDF, PNG, JPG, TIFF
            </p>
          </div>
        )}

        {uploading && (
          <div className="upload-status">
            <div className="spinner"></div>
            <h3>Uploading Document...</h3>
            <p>Please wait while we upload your file</p>
          </div>
        )}

        {processing && (
          <div className="processing-status">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <h3>AI Processing in Progress...</h3>
            <p>
              {progress < 30 && 'Extracting text from document...'}
              {progress >= 30 && progress < 60 && 'Analyzing medical content...'}
              {progress >= 60 && progress < 90 && 'Extracting medical entities...'}
              {progress >= 90 && 'Finalizing results...'}
            </p>
            <div className="progress-text">{progress}% Complete</div>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <div className="error-icon">⚠️</div>
          <div>
            <h4>Processing Error</h4>
            <p>{error}</p>
            <button 
              onClick={() => setError(null)}
              className="retry-button"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIDocumentUpload;