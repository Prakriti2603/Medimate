import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './ConsentManagement.css';

const ConsentManagement = () => {
  const [consents, setConsents] = useState([
    {
      id: 1,
      entity: 'XYZ Hospital',
      type: 'Hospital',
      hasAccess: true,
      grantedDate: '2025-09-10',
      txnHash: '0xA1234567890ABCDEF'
    },
    {
      id: 2,
      entity: 'ABC Insurance',
      type: 'Insurer',
      hasAccess: true,
      grantedDate: '2025-09-12',
      txnHash: '0xB9876543210FEDCBA'
    }
  ]);

  const handleToggleAccess = (id) => {
    setConsents(prev => prev.map(consent => 
      consent.id === id 
        ? { ...consent, hasAccess: !consent.hasAccess }
        : consent
    ));
  };

  return (
    <div className="consent-management">
      <header className="consent-header">
        <Link to="/patient/dashboard" className="back-btn">← Back</Link>
        <h1>Manage Data Sharing</h1>
      </header>

      <div className="consent-content">
        <div className="consent-list">
          {consents.map((consent) => (
            <div key={consent.id} className="consent-item">
              <div className="consent-info">
                <h3>{consent.entity}</h3>
                <span className="entity-type">{consent.type}</span>
                {consent.hasAccess && (
                  <span className="granted-date">
                    Access granted on: {new Date(consent.grantedDate).toLocaleDateString()}
                  </span>
                )}
              </div>
              
              <div className="consent-actions">
                {consent.hasAccess ? (
                  <button 
                    className="revoke-btn"
                    onClick={() => handleToggleAccess(consent.id)}
                  >
                    Revoke Access
                  </button>
                ) : (
                  <button 
                    className="grant-btn"
                    onClick={() => handleToggleAccess(consent.id)}
                  >
                    Grant Access
                  </button>
                )}
              </div>
              
              {consent.hasAccess && (
                <div className="blockchain-info">
                  <div className="txn-hash">
                    <span className="label">Blockchain Txn Hash:</span>
                    <span className="hash">{consent.txnHash}</span>
                    <span className="verified">Verified ✅</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="consent-explanation">
          <h3>About Data Sharing Consent</h3>
          <ul>
            <li>Your consent is recorded on the blockchain for transparency and immutability</li>
            <li>You can grant or revoke access at any time</li>
            <li>All access changes are logged with cryptographic proof</li>
            <li>Only authorized entities can view your medical data</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ConsentManagement;