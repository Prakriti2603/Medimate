import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [systemStats] = useState({
    totalPatients: 200,
    totalHospitals: 15,
    totalInsurers: 8,
    activeClaims: 50,
    approvedClaims: 120,
    rejectedClaims: 10,
    aiAccuracy: 91
  });

  const [blockchainLogs] = useState([
    { id: 1, type: 'Consent Granted', hash: '0xA123456789ABCDEF', status: 'verified', timestamp: '2025-09-14 10:30' },
    { id: 2, type: 'Claim Filed', hash: '0xB456789012FEDCBA', status: 'verified', timestamp: '2025-09-14 09:15' },
    { id: 3, type: 'Record Uploaded', hash: '0xC789012345ABCDEF', status: 'verified', timestamp: '2025-09-14 08:45' },
    { id: 4, type: 'Consent Revoked', hash: '0xD012345678FEDCBA', status: 'verified', timestamp: '2025-09-13 16:20' },
    { id: 5, type: 'Claim Approved', hash: '0xE345678901ABCDEF', status: 'verified', timestamp: '2025-09-13 14:10' }
  ]);

  const [recentActivity] = useState([
    { id: 1, action: 'New patient registered', user: 'John Doe', timestamp: '2 minutes ago' },
    { id: 2, action: 'Claim approved', user: 'ABC Insurance', timestamp: '15 minutes ago' },
    { id: 3, action: 'Records uploaded', user: 'XYZ Hospital', timestamp: '1 hour ago' },
    { id: 4, action: 'Consent granted', user: 'Jane Smith', timestamp: '2 hours ago' }
  ]);

  const getTransactionTypeColor = (type) => {
    switch (type) {
      case 'Consent Granted': return '#27ae60';
      case 'Claim Filed': return '#3498db';
      case 'Record Uploaded': return '#16a085';
      case 'Consent Revoked': return '#e74c3c';
      case 'Claim Approved': return '#f39c12';
      default: return '#666';
    }
  };

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <div className="logo">MediMate Admin Dashboard</div>
        <div className="admin-info">System Administrator</div>
      </header>

      <div className="dashboard-content">
        <div className="overview-section">
          <h2>System Overview</h2>
          <div className="overview-grid">
            <div className="overview-card entities">
              <h3>Platform Entities</h3>
              <div className="entity-stats">
                <div className="entity-item">
                  <span className="entity-number">{systemStats.totalPatients}</span>
                  <span className="entity-label">Total Patients</span>
                </div>
                <div className="entity-item">
                  <span className="entity-number">{systemStats.totalHospitals}</span>
                  <span className="entity-label">Hospitals</span>
                </div>
                <div className="entity-item">
                  <span className="entity-number">{systemStats.totalInsurers}</span>
                  <span className="entity-label">Insurers</span>
                </div>
              </div>
            </div>

            <div className="overview-card claims">
              <h3>Claims Statistics</h3>
              <div className="claims-stats">
                <div className="claim-item active">
                  <span className="claim-number">{systemStats.activeClaims}</span>
                  <span className="claim-label">Active Claims</span>
                </div>
                <div className="claim-item approved">
                  <span className="claim-number">{systemStats.approvedClaims}</span>
                  <span className="claim-label">Approved</span>
                </div>
                <div className="claim-item rejected">
                  <span className="claim-number">{systemStats.rejectedClaims}</span>
                  <span className="claim-label">Rejected</span>
                </div>
              </div>
            </div>

            <div className="overview-card ai-performance">
              <h3>AI Model Performance</h3>
              <div className="ai-stats">
                <div className="accuracy-circle">
                  <div className="accuracy-number">{systemStats.aiAccuracy}%</div>
                  <div className="accuracy-label">Accuracy</div>
                </div>
                <div className="performance-details">
                  <div className="detail-item">
                    <span className="detail-label">Last 50 claims</span>
                    <span className="detail-value">46 correct</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Processing time</span>
                    <span className="detail-value">2.3s avg</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="blockchain-section">
          <h3>Blockchain Transaction Logs</h3>
          <div className="blockchain-logs">
            <div className="logs-header">
              <div className="header-cell">Transaction Type</div>
              <div className="header-cell">Hash</div>
              <div className="header-cell">Status</div>
              <div className="header-cell">Timestamp</div>
            </div>
            
            {blockchainLogs.map((log) => (
              <div key={log.id} className="log-row">
                <div className="log-cell">
                  <span 
                    className="transaction-type"
                    style={{ color: getTransactionTypeColor(log.type) }}
                  >
                    {log.type}
                  </span>
                </div>
                <div className="log-cell">
                  <span className="transaction-hash">{log.hash}</span>
                </div>
                <div className="log-cell">
                  <span className="status-verified">✅ Verified</span>
                </div>
                <div className="log-cell">
                  <span className="timestamp">{log.timestamp}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="activity-section">
          <h3>Recent System Activity</h3>
          <div className="activity-list">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="activity-item">
                <div className="activity-icon">📋</div>
                <div className="activity-details">
                  <div className="activity-action">{activity.action}</div>
                  <div className="activity-meta">
                    <span className="activity-user">{activity.user}</span>
                    <span className="activity-time">{activity.timestamp}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="admin-actions">
          <h3>System Management</h3>
          <div className="action-buttons">
            <button className="admin-btn primary">Generate Reports</button>
            <button className="admin-btn secondary">Manage Users</button>
            <button className="admin-btn secondary">System Settings</button>
            <button className="admin-btn warning">Backup Data</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;