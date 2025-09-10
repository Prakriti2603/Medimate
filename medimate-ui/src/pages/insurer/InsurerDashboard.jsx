import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './InsurerDashboard.css';

const InsurerDashboard = () => {
  const [claims] = useState([
    { id: 'CLM2025-001', patientName: 'John Doe', amount: '₹65,000', status: 'Pending', submittedDate: '2025-09-12' },
    { id: 'CLM2025-002', patientName: 'Jane Smith', amount: '₹45,000', status: 'In Review', submittedDate: '2025-09-10' },
    { id: 'CLM2025-003', patientName: 'Mike Johnson', amount: '₹25,000', status: 'Approved', submittedDate: '2025-09-08' },
    { id: 'CLM2025-004', patientName: 'Sarah Wilson', amount: '₹85,000', status: 'Rejected', submittedDate: '2025-09-05' },
    { id: 'CLM2025-005', patientName: 'David Brown', amount: '₹35,000', status: 'Pending', submittedDate: '2025-09-14' }
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  const claimStats = {
    pending: claims.filter(c => c.status === 'Pending').length,
    inReview: claims.filter(c => c.status === 'In Review').length,
    approved: claims.filter(c => c.status === 'Approved').length,
    rejected: claims.filter(c => c.status === 'Rejected').length
  };

  const filteredClaims = claims.filter(claim => {
    const matchesSearch = claim.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         claim.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || claim.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'Pending': return '#ff9800';
      case 'In Review': return '#2196f3';
      case 'Approved': return '#4caf50';
      case 'Rejected': return '#f44336';
      default: return '#666';
    }
  };

  return (
    <div className="insurer-dashboard">
      <header className="dashboard-header">
        <div className="logo">MediMate Insurer Portal</div>
        <div className="user-info">Welcome, Insurance Admin</div>
      </header>

      <div className="dashboard-content">
        <div className="stats-overview">
          <h2>Claims Overview</h2>
          <div className="stats-grid">
            <div className="stat-card pending">
              <div className="stat-number">{claimStats.pending}</div>
              <div className="stat-label">Pending</div>
            </div>
            <div className="stat-card in-review">
              <div className="stat-number">{claimStats.inReview}</div>
              <div className="stat-label">In Review</div>
            </div>
            <div className="stat-card approved">
              <div className="stat-number">{claimStats.approved}</div>
              <div className="stat-label">Approved</div>
            </div>
            <div className="stat-card rejected">
              <div className="stat-number">{claimStats.rejected}</div>
              <div className="stat-label">Rejected</div>
            </div>
          </div>
        </div>

        <div className="claims-section">
          <div className="section-header">
            <h3>Claims Management</h3>
            <div className="filters">
              <input
                type="text"
                placeholder="Search claims..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="status-filter"
              >
                <option value="All">Filter by Status</option>
                <option value="Pending">Pending</option>
                <option value="In Review">In Review</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>
          </div>

          <div className="claims-table">
            <div className="table-header">
              <div className="header-cell">Claim ID</div>
              <div className="header-cell">Patient Name</div>
              <div className="header-cell">Amount</div>
              <div className="header-cell">Status</div>
              <div className="header-cell">Submitted</div>
              <div className="header-cell">Actions</div>
            </div>
            
            {filteredClaims.map((claim) => (
              <div key={claim.id} className="table-row">
                <div className="table-cell claim-id">{claim.id}</div>
                <div className="table-cell">{claim.patientName}</div>
                <div className="table-cell amount">{claim.amount}</div>
                <div className="table-cell">
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(claim.status) }}
                  >
                    {claim.status}
                  </span>
                </div>
                <div className="table-cell">{new Date(claim.submittedDate).toLocaleDateString()}</div>
                <div className="table-cell">
                  <Link 
                    to={`/insurer/claim-review/${claim.id}`}
                    className="review-btn"
                  >
                    Review
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {filteredClaims.length === 0 && (
            <div className="no-results">
              No claims found matching your criteria.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InsurerDashboard;