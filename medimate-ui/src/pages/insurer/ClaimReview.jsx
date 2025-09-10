import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './ClaimReview.css';

const ClaimReview = () => {
  const [claimData] = useState({
    claimId: 'CLM2025-001',
    extractedFields: {
      policyNo: 'POL123456',
      patientName: 'John Doe',
      admissionDate: '2025-09-12',
      dischargeDate: '2025-09-16',
      diagnosis: 'Pneumonia (ICD: J18.9)',
      totalBill: '₹65,000'
    },
    confidence: 92,
    documents: [
      { name: 'Hospital Bill.pdf', type: 'bill' },
      { name: 'Discharge Summary.pdf', type: 'discharge' },
      { name: 'Lab Reports.pdf', type: 'lab' }
    ]
  });

  const [selectedDocument, setSelectedDocument] = useState(claimData.documents[0]);
  const [comments, setComments] = useState('');

  const handleDecision = (action) => {
    console.log(`Claim ${action}:`, { claimId: claimData.claimId, comments });
    
    let message = '';
    switch(action) {
      case 'approve':
        message = 'Claim approved successfully!';
        break;
      case 'reject':
        message = 'Claim rejected. Patient will be notified.';
        break;
      case 'request-info':
        message = 'Additional information requested from patient.';
        break;
      default:
        message = 'Action completed.';
    }
    alert(message);
  };

  return (
    <div className="claim-review">
      <header className="review-header">
        <Link to="/insurer/dashboard" className="back-btn">← Back</Link>
        <h1>Claim Review - Claim ID: {claimData.claimId}</h1>
      </header>

      <div className="review-content">
        <div className="extracted-fields">
          <h3>Auto-Filled Fields (AI Extracted)</h3>
          <div className="fields-grid">
            <div className="field-item">
              <span className="field-label">Policy No.:</span>
              <span className="field-value">{claimData.extractedFields.policyNo}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Patient Name:</span>
              <span className="field-value">{claimData.extractedFields.patientName}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Admission Date:</span>
              <span className="field-value">{claimData.extractedFields.admissionDate}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Discharge Date:</span>
              <span className="field-value">{claimData.extractedFields.dischargeDate}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Diagnosis:</span>
              <span className="field-value">{claimData.extractedFields.diagnosis}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Total Bill:</span>
              <span className="field-value total-amount">{claimData.extractedFields.totalBill}</span>
            </div>
          </div>
          
          <div className="confidence-indicator">
            <span>Extracted Field Confidence: </span>
            <span className={`confidence-score ${claimData.confidence >= 90 ? 'high' : claimData.confidence >= 70 ? 'medium' : 'low'}`}>
              {claimData.confidence}%
            </span>
          </div>
        </div>

        <div className="document-section">
          <div className="document-tabs">
            <h3>Original Documents</h3>
            <div className="tabs">
              {claimData.documents.map((doc, index) => (
                <button
                  key={index}
                  className={`tab ${selectedDocument.name === doc.name ? 'active' : ''}`}
                  onClick={() => setSelectedDocument(doc)}
                >
                  {doc.name}
                </button>
              ))}
            </div>
          </div>
          
          <div className="document-viewer">
            <div className="pdf-placeholder">
              <div className="pdf-icon">📄</div>
              <p>PDF Preview: {selectedDocument.name}</p>
              <p className="pdf-note">Document viewer would display the actual PDF content here</p>
            </div>
          </div>
        </div>

        <div className="comments-section">
          <h3>Review Comments</h3>
          <textarea
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            placeholder="Add your review comments here..."
            className="comments-textarea"
          />
        </div>

        <div className="action-buttons">
          <button 
            className="approve-btn"
            onClick={() => handleDecision('approve')}
          >
            Approve
          </button>
          <button 
            className="reject-btn"
            onClick={() => handleDecision('reject')}
          >
            Reject
          </button>
          <button 
            className="request-info-btn"
            onClick={() => handleDecision('request-info')}
          >
            Request Info
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClaimReview;