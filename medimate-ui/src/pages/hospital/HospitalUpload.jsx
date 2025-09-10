import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './HospitalUpload.css';

const HospitalUpload = () => {
  const [uploadedFiles, setUploadedFiles] = useState({});
  const [patientConsent, setPatientConsent] = useState(true); // Demo: patient has given consent
  const [selectedPatient, setSelectedPatient] = useState('John Doe - ID: P001');

  const documentTypes = [
    { key: 'admission', label: 'Admission Note', required: true },
    { key: 'discharge', label: 'Discharge Summary', required: true },
    { key: 'hospitalBills', label: 'Hospital Bills (Main + Breakup)', required: true },
    { key: 'receipts', label: 'Receipts', required: false },
    { key: 'pharmacy', label: 'Pharmacy Bills', required: false },
    { key: 'labReports', label: 'Lab Reports', required: false }
  ];

  const handleFileUpload = (docType, event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFiles(prev => ({
        ...prev,
        [docType]: file
      }));
    }
  };

  const handleSubmit = () => {
    console.log('Submitting hospital records:', uploadedFiles);
    alert('Hospital records uploaded successfully! Patient and insurer will be notified.');
  };

  const uploadedCount = Object.keys(uploadedFiles).length;
  const totalDocs = documentTypes.length;

  return (
    <div className="hospital-upload">
      <header className="upload-header">
        <Link to="/hospital/dashboard" className="back-btn">← Back</Link>
        <h1>Upload Hospital Records for Patient</h1>
      </header>

      <div className="upload-content">
        <div className="patient-info">
          <h3>Patient Information</h3>
          <div className="patient-details">
            <div className="patient-name">
              <span className="label">Selected Patient:</span>
              <select 
                value={selectedPatient}
                onChange={(e) => setSelectedPatient(e.target.value)}
                className="patient-select"
              >
                <option value="John Doe - ID: P001">John Doe - ID: P001</option>
                <option value="Jane Smith - ID: P002">Jane Smith - ID: P002</option>
                <option value="Mike Johnson - ID: P003">Mike Johnson - ID: P003</option>
              </select>
            </div>
            <div className="consent-status">
              <span className="label">Consent Status:</span>
              <span className={`consent-badge ${patientConsent ? 'approved' : 'pending'}`}>
                {patientConsent ? '✅ Patient Approved' : '⏳ Pending Approval'}
              </span>
            </div>
          </div>
        </div>

        <div className="document-upload-section">
          <h3>Upload Medical Records</h3>
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
                    disabled={!patientConsent}
                  />
                  <label htmlFor={doc.key} className={`file-input-label ${!patientConsent ? 'disabled' : ''}`}>
                    {uploadedFiles[doc.key] ? 
                      `✓ ${uploadedFiles[doc.key].name}` : 
                      'Choose File'
                    }
                  </label>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="upload-summary">
          <div className="progress-info">
            <span>Progress: {uploadedCount}/{totalDocs} documents uploaded</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(uploadedCount / totalDocs) * 100}%` }}
            ></div>
          </div>
        </div>

        <button 
          className="submit-btn"
          onClick={handleSubmit}
          disabled={!patientConsent || uploadedCount === 0}
        >
          Submit Hospital Records
        </button>

        {!patientConsent && (
          <div className="consent-warning">
            <p>⚠️ Patient consent is required before uploading medical records.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HospitalUpload;