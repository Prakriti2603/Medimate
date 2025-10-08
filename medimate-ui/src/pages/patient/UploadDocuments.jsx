import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './UploadDocuments.css';

const UploadDocuments = () => {
  const [uploadedFiles, setUploadedFiles] = useState({});
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadErrors, setUploadErrors] = useState({});

  // File size limits (in bytes)
  const FILE_SIZE_LIMITS = {
    maxSize: 10 * 1024 * 1024, // 10MB maximum
    recommendedSize: 5 * 1024 * 1024, // 5MB recommended
    minSize: 1024 // 1KB minimum
  };

  const documentTypes = [
    { key: 'insurance', label: 'Insurance Policy/E-card', required: true },
    { key: 'idProof', label: 'ID Proof (Aadhaar, PAN, etc.)', required: true },
    { key: 'admission', label: 'Admission Note', required: true },
    { key: 'discharge', label: 'Discharge Summary', required: true },
    { key: 'hospitalBill', label: 'Hospital Bill + Breakup', required: true },
    { key: 'pharmacy', label: 'Pharmacy Bills', required: false },
    { key: 'labReports', label: 'Lab Reports', required: false },
    { key: 'prescriptions', label: 'Prescriptions', required: false }
  ];

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file) => {
    const errors = [];
    
    // Check file size
    if (file.size > FILE_SIZE_LIMITS.maxSize) {
      errors.push(`File size (${formatFileSize(file.size)}) exceeds maximum limit of ${formatFileSize(FILE_SIZE_LIMITS.maxSize)}`);
    }
    
    if (file.size < FILE_SIZE_LIMITS.minSize) {
      errors.push(`File size (${formatFileSize(file.size)}) is too small. Minimum size is ${formatFileSize(FILE_SIZE_LIMITS.minSize)}`);
    }
    
    // Check file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      errors.push('Invalid file type. Please upload PDF, JPG, JPEG, or PNG files only.');
    }
    
    // Warning for large files
    const warnings = [];
    if (file.size > FILE_SIZE_LIMITS.recommendedSize) {
      warnings.push(`Large file detected (${formatFileSize(file.size)}). Consider compressing for faster upload.`);
    }
    
    return { errors, warnings };
  };

  const handleFileUpload = (docType, event) => {
    const file = event.target.files[0];
    
    // Clear previous errors
    setUploadErrors(prev => ({
      ...prev,
      [docType]: null
    }));
    
    if (file) {
      const validation = validateFile(file);
      
      if (validation.errors.length > 0) {
        // File validation failed
        setUploadErrors(prev => ({
          ...prev,
          [docType]: {
            type: 'error',
            messages: validation.errors
          }
        }));
        // Clear the file input
        event.target.value = '';
        return;
      }
      
      // File is valid, show warnings if any
      if (validation.warnings.length > 0) {
        setUploadErrors(prev => ({
          ...prev,
          [docType]: {
            type: 'warning',
            messages: validation.warnings
          }
        }));
      }
      
      // Add file to uploaded files
      setUploadedFiles(prev => ({
        ...prev,
        [docType]: file
      }));
      
      // Update progress
      const newProgress = Object.keys({...uploadedFiles, [docType]: file}).length;
      setUploadProgress(newProgress);
    }
  };

  const handleSubmit = () => {
    // Handle form submission
    console.log('Submitting documents:', uploadedFiles);
    alert('Documents submitted successfully!');
  };

  const totalDocs = documentTypes.length;
  const progressPercentage = (uploadProgress / totalDocs) * 100;

  return (
    <div className="upload-documents">
      <header className="upload-header">
        <Link to="/patient/dashboard" className="back-btn">← Back</Link>
        <h1>Upload Your Documents</h1>
      </header>

      <div className="upload-content">
        <div className="document-list">
          {documentTypes.map((doc) => (
            <div key={doc.key} className="document-item">
              <label className="document-label">
                {doc.label} {doc.required && <span className="required">*</span>}
              </label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id={doc.key}
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(doc.key, e)}
                  className="file-input"
                />
                <label htmlFor={doc.key} className="file-input-label">
                  {uploadedFiles[doc.key] ? 
                    `✓ ${uploadedFiles[doc.key].name} (${formatFileSize(uploadedFiles[doc.key].size)})` : 
                    'Choose File'
                  }
                </label>
                
                {/* File size info */}
                <div className="file-size-info">
                  <small>Max: {formatFileSize(FILE_SIZE_LIMITS.maxSize)} | Recommended: {formatFileSize(FILE_SIZE_LIMITS.recommendedSize)}</small>
                </div>
                
                {/* Error/Warning messages */}
                {uploadErrors[doc.key] && (
                  <div className={`upload-message ${uploadErrors[doc.key].type}`}>
                    {uploadErrors[doc.key].messages.map((message, index) => (
                      <div key={index} className="message-item">
                        {uploadErrors[doc.key].type === 'error' ? '❌' : '⚠️'} {message}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="progress-section">
          <div className="progress-bar-container">
            <div className="progress-label">
              Progress: {uploadProgress}/{totalDocs} documents uploaded
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
          
          {/* File size summary */}
          {Object.keys(uploadedFiles).length > 0 && (
            <div className="file-summary">
              <h4>Upload Summary</h4>
              <div className="summary-stats">
                <div className="stat-item">
                  <span className="stat-label">Total Files:</span>
                  <span className="stat-value">{Object.keys(uploadedFiles).length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Size:</span>
                  <span className="stat-value">
                    {formatFileSize(
                      Object.values(uploadedFiles).reduce((total, file) => total + file.size, 0)
                    )}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Largest File:</span>
                  <span className="stat-value">
                    {formatFileSize(
                      Math.max(...Object.values(uploadedFiles).map(file => file.size))
                    )}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <button 
          className="submit-btn"
          onClick={handleSubmit}
          disabled={uploadProgress === 0}
        >
          Submit Documents
        </button>
      </div>
    </div>
  );
};

export default UploadDocuments;