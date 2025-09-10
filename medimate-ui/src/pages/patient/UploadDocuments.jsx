import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './UploadDocuments.css';

const UploadDocuments = () => {
  const [uploadedFiles, setUploadedFiles] = useState({});
  const [uploadProgress, setUploadProgress] = useState(0);

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

  const handleFileUpload = (docType, event) => {
    const file = event.target.files[0];
    if (file) {
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
                    `✓ ${uploadedFiles[doc.key].name}` : 
                    'Choose File'
                  }
                </label>
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