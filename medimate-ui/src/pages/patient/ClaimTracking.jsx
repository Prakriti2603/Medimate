import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './ClaimTracking.css';

const ClaimTracking = () => {
  const [claims] = useState([
    {
      id: 'CLM2025-001',
      status: 'In Review',
      submittedDate: '2025-09-12',
      verifiedDate: '2025-09-14',
      amount: '₹65,000',
      hospital: 'XYZ Hospital',
      diagnosis: 'Pneumonia',
      timeline: [
        { date: '12/09', status: 'Submitted', completed: true },
        { date: '14/09', status: 'Verified by Insurer', completed: true },
        { date: 'Pending', status: 'Final Approval', completed: false }
      ]
    },
    {
      id: 'CLM2025-002',
      status: 'Approved',
      submittedDate: '2025-08-20',
      verifiedDate: '2025-08-22',
      approvedDate: '2025-08-25',
      amount: '₹25,000',
      hospital: 'ABC Medical Center',
      diagnosis: 'Appendectomy',
      timeline: [
        { date: '20/08', status: 'Submitted', completed: true },
        { date: '22/08', status: 'Verified by Insurer', completed: true },
        { date: '25/08', status: 'Final Approval', completed: true }
      ]
    }
  ]);

  const [selectedClaim, setSelectedClaim] = useState(claims[0]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Submitted': return '#2196f3';
      case 'In Review': return '#ff9800';
      case 'Approved': return '#4caf50';
      case 'Rejected': return '#f44336';
      default: return '#666';
    }
  };

  return (
    <div className="claim-tracking">
      <header className="tracking-header">
        <Link to="/patient/dashboard" className="back-btn">← Back</Link>
        <h1>Track Claims</h1>
      </header>

      <div className="tracking-content">
        <div className="claims-sidebar">
          <h3>Your Claims</h3>
          {claims.map((claim) => (
            <div 
              key={claim.id}
              className={`claim-card ${selectedClaim.id === claim.id ? 'active' : ''}`}
              onClick={() => setSelectedClaim(claim)}
            >
              <div className="claim-id">{claim.id}</div>
              <div className="claim-amount">{claim.amount}</div>
              <div 
                className="claim-status"
                style={{ color: getStatusColor(claim.status) }}
              >
                {claim.status}
              </div>
            </div>
          ))}
        </div>

        <div className="claim-details">
          <div className="claim-header">
            <h2>Claim ID: {selectedClaim.id}</h2>
            <div 
              className="status-badge"
              style={{ backgroundColor: getStatusColor(selectedClaim.status) }}
            >
              {selectedClaim.status}
            </div>
          </div>

          <div className="claim-info">
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Amount:</span>
                <span className="value">{selectedClaim.amount}</span>
              </div>
              <div className="info-item">
                <span className="label">Hospital:</span>
                <span className="value">{selectedClaim.hospital}</span>
              </div>
              <div className="info-item">
                <span className="label">Diagnosis:</span>
                <span className="value">{selectedClaim.diagnosis}</span>
              </div>
              <div className="info-item">
                <span className="label">Submitted:</span>
                <span className="value">{new Date(selectedClaim.submittedDate).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          <div className="timeline-section">
            <h3>Timeline</h3>
            <div className="timeline">
              {selectedClaim.timeline.map((step, index) => (
                <div key={index} className={`timeline-item ${step.completed ? 'completed' : 'pending'}`}>
                  <div className="timeline-marker"></div>
                  <div className="timeline-content">
                    <div className="timeline-date">{step.date}</div>
                    <div className="timeline-status">{step.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {selectedClaim.status === 'In Review' && (
            <div className="next-steps">
              <h4>Next Steps</h4>
              <p>Your claim is currently being reviewed by the insurance team. You will be notified once the review is complete.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ClaimTracking;