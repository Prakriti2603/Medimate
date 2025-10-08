import React, { useState } from 'react';
import AIDocumentUpload from '../components/AI/AIDocumentUpload';
import AIFormFiller from '../components/AI/AIFormFiller';
import './AIFormProcessor.css';

const AIFormProcessor = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [documentData, setDocumentData] = useState(null);
  const [processingResults, setProcessingResults] = useState(null);
  const [completedForm, setCompletedForm] = useState(null);

  const handleUploadComplete = (results) => {
    setDocumentData(results);
    setProcessingResults(results);
    setCurrentStep(2);
  };

  const handleFormComplete = (formData) => {
    setCompletedForm(formData);
    setCurrentStep(3);
  };

  const handleStartOver = () => {
    setCurrentStep(1);
    setDocumentData(null);
    setProcessingResults(null);
    setCompletedForm(null);
  };

  const renderStepIndicator = () => (
    <div className="step-indicator">
      <div className={`step ${currentStep >= 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
        <div className="step-number">1</div>
        <div className="step-label">Upload Document</div>
      </div>
      <div className="step-connector"></div>
      <div className={`step ${currentStep >= 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
        <div className="step-number">2</div>
        <div className="step-label">AI Form Fill</div>
      </div>
      <div className="step-connector"></div>
      <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
        <div className="step-number">3</div>
        <div className="step-label">Review & Submit</div>
      </div>
    </div>
  );

  const renderExtractionSummary = () => {
    if (!processingResults) return null;

    const { extractionResult, analysisResult } = processingResults;
    
    return (
      <div className="extraction-summary">
        <h3>📊 Document Analysis Summary</h3>
        
        <div className="summary-grid">
          <div className="summary-card">
            <div className="card-header">
              <h4>📄 Document Info</h4>
            </div>
            <div className="card-content">
              <div className="info-item">
                <span className="label">Type:</span>
                <span className="value">
                  {analysisResult?.analysis?.classification?.document_type?.replace('_', ' ') || 'Unknown'}
                </span>
              </div>
              <div className="info-item">
                <span className="label">Specialty:</span>
                <span className="value">
                  {analysisResult?.analysis?.classification?.specialty || 'General'}
                </span>
              </div>
              <div className="info-item">
                <span className="label">Confidence:</span>
                <span className="value confidence">
                  {Math.round((analysisResult?.analysis?.classification?.confidence || 0) * 100)}%
                </span>
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-header">
              <h4>🏷️ Entities Found</h4>
            </div>
            <div className="card-content">
              <div className="info-item">
                <span className="label">Total Entities:</span>
                <span className="value">{extractionResult?.extracted_fields?.length || 0}</span>
              </div>
              <div className="info-item">
                <span className="label">High Confidence:</span>
                <span className="value">
                  {extractionResult?.extracted_fields?.filter(f => f.confidence > 0.8).length || 0}
                </span>
              </div>
              <div className="info-item">
                <span className="label">Processing Time:</span>
                <span className="value">{extractionResult?.processing_time?.toFixed(2) || 0}s</span>
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-header">
              <h4>💡 AI Insights</h4>
            </div>
            <div className="card-content">
              {analysisResult?.analysis?.nlp_analysis?.insights?.clinical_notes?.slice(0, 3).map((note, index) => (
                <div key={index} className="insight-item">
                  <span className="insight-icon">•</span>
                  <span className="insight-text">{note}</span>
                </div>
              )) || <span className="no-insights">No insights available</span>}
            </div>
          </div>
        </div>

        {extractionResult?.extracted_fields?.length > 0 && (
          <div className="extracted-entities">
            <h4>🔍 Key Extracted Information</h4>
            <div className="entities-grid">
              {extractionResult.extracted_fields.slice(0, 6).map((field, index) => (
                <div key={index} className="entity-item">
                  <div className="entity-label">{field.field_name.replace('_', ' ')}</div>
                  <div className="entity-value">{field.value}</div>
                  <div className="entity-confidence">
                    <div 
                      className="confidence-bar"
                      style={{ 
                        width: `${field.confidence * 100}%`,
                        backgroundColor: field.confidence > 0.8 ? '#28a745' : 
                                       field.confidence > 0.6 ? '#ffc107' : '#dc3545'
                      }}
                    ></div>
                    <span className="confidence-text">{Math.round(field.confidence * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderCompletionSummary = () => {
    if (!completedForm) return null;

    return (
      <div className="completion-summary">
        <div className="success-header">
          <div className="success-icon">🎉</div>
          <h2>Form Completed Successfully!</h2>
          <p>Your medical form has been automatically filled and is ready for submission.</p>
        </div>

        <div className="completion-stats">
          <div className="stat-card">
            <div className="stat-number">{Math.round(completedForm.completionRate * 100)}%</div>
            <div className="stat-label">Completion Rate</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{Object.keys(completedForm.formData).length}</div>
            <div className="stat-label">Total Fields</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">
              {Object.values(completedForm.formData).filter(f => f.value).length}
            </div>
            <div className="stat-label">Fields Filled</div>
          </div>
        </div>

        <div className="form-preview">
          <h3>📋 Form Preview</h3>
          <div className="form-type-badge">
            {completedForm.formType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </div>
          
          <div className="preview-fields">
            {Object.entries(completedForm.formData)
              .filter(([_, fieldData]) => fieldData.value)
              .slice(0, 5)
              .map(([fieldName, fieldData]) => (
                <div key={fieldName} className="preview-field">
                  <span className="field-name">
                    {fieldName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                  </span>
                  <span className="field-value">{fieldData.value}</span>
                  {fieldData.auto_filled && (
                    <span className="ai-badge">AI</span>
                  )}
                </div>
              ))}
          </div>
        </div>

        <div className="completion-actions">
          <button className="primary-button" onClick={() => alert('Form submitted successfully!')}>
            Submit Form
          </button>
          <button className="secondary-button" onClick={() => setCurrentStep(2)}>
            Edit Form
          </button>
          <button className="tertiary-button" onClick={handleStartOver}>
            Process New Document
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="ai-form-processor">
      <div className="page-header">
        <h1>🤖 AI Medical Form Processor</h1>
        <p>Upload medical documents and let AI automatically fill out forms</p>
      </div>

      {renderStepIndicator()}

      <div className="page-content">
        {currentStep === 1 && (
          <div className="step-content">
            <AIDocumentUpload 
              onUploadComplete={handleUploadComplete}
              onProcessingUpdate={(update) => console.log('Processing update:', update)}
            />
          </div>
        )}

        {currentStep === 2 && (
          <div className="step-content">
            {renderExtractionSummary()}
            <AIFormFiller
              documentId={documentData?.documentId}
              extractionResult={processingResults?.extractionResult}
              onFormComplete={handleFormComplete}
            />
          </div>
        )}

        {currentStep === 3 && (
          <div className="step-content">
            {renderCompletionSummary()}
          </div>
        )}
      </div>

      {currentStep > 1 && (
        <div className="page-actions">
          <button 
            className="back-button"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
          >
            ← Back
          </button>
          <button 
            className="start-over-button"
            onClick={handleStartOver}
          >
            Start Over
          </button>
        </div>
      )}
    </div>
  );
};

export default AIFormProcessor;