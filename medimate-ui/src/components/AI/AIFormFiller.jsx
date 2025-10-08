import React, { useState, useEffect } from 'react';
import './AIFormFiller.css';

const AIFormFiller = ({ documentId, extractionResult, onFormComplete }) => {
  const [selectedFormType, setSelectedFormType] = useState('');
  const [availableForms, setAvailableForms] = useState([]);
  const [formTemplate, setFormTemplate] = useState(null);
  const [filledForm, setFilledForm] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAvailableForms();
  }, []);

  const loadAvailableForms = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/documents/forms/templates');
      if (response.ok) {
        const data = await response.json();
        setAvailableForms(data.available_forms || []);
      }
    } catch (err) {
      console.error('Failed to load form templates:', err);
    }
  };

  const handleFormTypeChange = async (formType) => {
    setSelectedFormType(formType);
    setError(null);
    
    if (!formType || !documentId) return;

    setLoading(true);
    
    try {
      // Auto-fill the selected form
      const response = await fetch('http://localhost:8001/api/v1/documents/auto-fill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          form_type: formType
        }),
      });

      if (!response.ok) {
        throw new Error('Form auto-fill failed');
      }

      const result = await response.json();
      setFilledForm(result);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (fieldName, newValue) => {
    if (!filledForm) return;

    setFilledForm(prev => ({
      ...prev,
      filled_form: {
        ...prev.filled_form,
        [fieldName]: {
          ...prev.filled_form[fieldName],
          value: newValue,
          auto_filled: false // Mark as manually edited
        }
      }
    }));
  };

  const handleSubmitForm = () => {
    if (onFormComplete && filledForm) {
      onFormComplete({
        formType: selectedFormType,
        formData: filledForm.filled_form,
        completionRate: filledForm.completion_rate,
        validationResults: filledForm.validation_results
      });
    }
  };

  const getFieldIcon = (field) => {
    if (field.auto_filled && field.confidence > 0.8) return '✅';
    if (field.auto_filled && field.confidence > 0.6) return '⚠️';
    if (field.auto_filled) return '❓';
    return '✏️';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.8) return '#28a745';
    if (confidence > 0.6) return '#ffc107';
    return '#dc3545';
  };

  return (
    <div className="ai-form-filler">
      <div className="form-header">
        <h3>🤖 AI Form Auto-Fill</h3>
        <p>Select a form type to automatically populate with extracted information</p>
      </div>

      {/* Form Type Selection */}
      <div className="form-selection">
        <label htmlFor="form-type">Select Form Type:</label>
        <select
          id="form-type"
          value={selectedFormType}
          onChange={(e) => handleFormTypeChange(e.target.value)}
          disabled={loading}
        >
          <option value="">Choose a form...</option>
          {availableForms.map(formType => (
            <option key={formType} value={formType}>
              {formType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>AI is filling out the form...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <div>
            <h4>Auto-fill Error</h4>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Filled Form Display */}
      {filledForm && !loading && (
        <div className="filled-form">
          <div className="form-stats">
            <div className="stat">
              <span className="stat-label">Completion Rate:</span>
              <span className="stat-value">{Math.round(filledForm.completion_rate * 100)}%</span>
            </div>
            <div className="stat">
              <span className="stat-label">Fields Filled:</span>
              <span className="stat-value">{filledForm.fields_filled}/{filledForm.total_fields}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Confidence:</span>
              <span 
                className="stat-value"
                style={{ color: getConfidenceColor(filledForm.confidence_score) }}
              >
                {Math.round(filledForm.confidence_score * 100)}%
              </span>
            </div>
          </div>

          <div className="form-fields">
            <h4>Form Fields</h4>
            {Object.entries(filledForm.filled_form).map(([fieldName, fieldData]) => (
              <div key={fieldName} className="form-field">
                <div className="field-header">
                  <label>
                    {getFieldIcon(fieldData)}
                    {fieldName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    {fieldData.required && <span className="required">*</span>}
                  </label>
                  {fieldData.auto_filled && (
                    <div className="confidence-badge">
                      <span 
                        className="confidence-score"
                        style={{ backgroundColor: getConfidenceColor(fieldData.confidence) }}
                      >
                        {Math.round(fieldData.confidence * 100)}%
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="field-input">
                  {fieldData.type === 'textarea' ? (
                    <textarea
                      value={fieldData.value || ''}
                      onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                      placeholder={`Enter ${fieldName.replace('_', ' ')}`}
                      rows={3}
                    />
                  ) : (
                    <input
                      type={fieldData.type === 'date' ? 'date' : fieldData.type === 'number' ? 'number' : 'text'}
                      value={fieldData.value || ''}
                      onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                      placeholder={`Enter ${fieldName.replace('_', ' ')}`}
                    />
                  )}
                </div>

                {fieldData.auto_filled && (
                  <div className="field-info">
                    <small>
                      {fieldData.confidence > 0.8 ? '✅ High confidence AI extraction' :
                       fieldData.confidence > 0.6 ? '⚠️ Medium confidence - please verify' :
                       '❓ Low confidence - please review carefully'}
                    </small>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Validation Results */}
          {filledForm.validation_results && !filledForm.validation_results.is_valid && (
            <div className="validation-issues">
              <h4>⚠️ Validation Issues</h4>
              {filledForm.validation_results.missing_required?.length > 0 && (
                <div className="missing-fields">
                  <p><strong>Missing Required Fields:</strong></p>
                  <ul>
                    {filledForm.validation_results.missing_required.map(field => (
                      <li key={field}>{field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</li>
                    ))}
                  </ul>
                </div>
              )}
              {filledForm.validation_results.field_warnings?.length > 0 && (
                <div className="field-warnings">
                  <p><strong>Field Warnings:</strong></p>
                  <ul>
                    {filledForm.validation_results.field_warnings.map((warning, index) => (
                      <li key={index}>
                        {warning.field}: {warning.message} (Confidence: {Math.round(warning.confidence * 100)}%)
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="form-actions">
            <button
              onClick={handleSubmitForm}
              className="submit-button"
              disabled={filledForm.validation_results && !filledForm.validation_results.is_valid}
            >
              Complete Form
            </button>
            <button
              onClick={() => setFilledForm(null)}
              className="cancel-button"
            >
              Start Over
            </button>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="legend">
        <h5>Legend:</h5>
        <div className="legend-items">
          <div className="legend-item">
            <span>✅</span> High confidence AI extraction
          </div>
          <div className="legend-item">
            <span>⚠️</span> Medium confidence - verify
          </div>
          <div className="legend-item">
            <span>❓</span> Low confidence - review carefully
          </div>
          <div className="legend-item">
            <span>✏️</span> Manually entered
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIFormFiller;