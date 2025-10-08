import React from 'react';
import { Link } from 'react-router-dom';
import './ModuleSelector.css';

const ModuleSelector = () => {
  return (
    <div className="module-selector">
      <div className="selector-content">
        <h2>Select Your Module</h2>
        <p>Choose the appropriate module based on your role</p>

        <div className="module-cards">
          <Link to="/patient/dashboard" className="module-card patient">
            <div className="module-icon">👤</div>
            <h3>Patient Portal</h3>
            <p>Upload documents, manage consent, and track your claims</p>
            <div className="module-features">
              <span>• Document Upload</span>
              <span>• Consent Management</span>
              <span>• Claim Tracking</span>
            </div>
          </Link>

          <Link to="/insurer/dashboard" className="module-card insurer">
            <div className="module-icon">🏢</div>
            <h3>Insurer Portal</h3>
            <p>Review claims, manage approvals, and process insurance requests</p>
            <div className="module-features">
              <span>• Claim Review</span>
              <span>• AI-Powered Extraction</span>
              <span>• Claims Dashboard</span>
            </div>
          </Link>

          <Link to="/hospital/dashboard" className="module-card hospital">
            <div className="module-icon">🏥</div>
            <h3>Hospital Portal</h3>
            <p>Upload patient records and manage medical documentation</p>
            <div className="module-features">
              <span>• Record Upload</span>
              <span>• Patient Management</span>
              <span>• Consent Tracking</span>
            </div>
          </Link>

          <Link to="/admin/dashboard" className="module-card admin">
            <div className="module-icon">⚙️</div>
            <h3>Admin Dashboard</h3>
            <p>Monitor system performance and manage platform operations</p>
            <div className="module-features">
              <span>• System Analytics</span>
              <span>• Blockchain Logs</span>
              <span>• AI Performance</span>
            </div>
          </Link>

          <Link to="/ai/form-processor" className="module-card ai">
            <div className="module-icon">🤖</div>
            <h3>AI Form Processor</h3>
            <p>AI-powered medical document processing and automatic form filling</p>
            <div className="module-features">
              <span>• Document Upload</span>
              <span>• AI Text Extraction</span>
              <span>• Auto Form Fill</span>
            </div>
          </Link>
        </div>

        <div className="demo-note">
          <p><strong>Demo Mode:</strong> This is a demonstration of the MediMate platform. In production, users would be automatically routed based on their authenticated role.</p>
        </div>
      </div>
    </div>
  );
};

export default ModuleSelector;