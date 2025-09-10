import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './HospitalDashboard.css';

const HospitalDashboard = () => {
  const [patients] = useState([
    { id: 'P001', name: 'John Doe', admissionDate: '2025-09-12', status: 'Active', consentStatus: 'Approved' },
    { id: 'P002', name: 'Jane Smith', admissionDate: '2025-09-10', status: 'Discharged', consentStatus: 'Approved' },
    { id: 'P003', name: 'Mike Johnson', admissionDate: '2025-09-08', status: 'Active', consentStatus: 'Pending' },
    { id: 'P004', name: 'Sarah Wilson', admissionDate: '2025-09-05', status: 'Discharged', consentStatus: 'Approved' }
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  const stats = {
    totalPatients: patients.length,
    activePatients: patients.filter(p => p.status === 'Active').length,
    recordsUploaded: patients.filter(p => p.consentStatus === 'Approved').length,
    pendingConsent: patients.filter(p => p.consentStatus === 'Pending').length
  };

  const filteredPatients = patients.filter(patient => {
    const matchesSearch = patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || patient.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return '#16a085';
      case 'Discharged': return '#3498db';
      default: return '#666';
    }
  };

  const getConsentColor = (consent) => {
    switch (consent) {
      case 'Approved': return '#27ae60';
      case 'Pending': return '#f39c12';
      case 'Denied': return '#e74c3c';
      default: return '#666';
    }
  };

  return (
    <div className="hospital-dashboard">
      <header className="dashboard-header">
        <div className="logo">MediMate Hospital Portal</div>
        <div className="hospital-info">XYZ Hospital - Dr. Admin</div>
      </header>

      <div className="dashboard-content">
        <div className="stats-overview">
          <h2>Hospital Overview</h2>
          <div className="stats-grid">
            <div className="stat-card total">
              <div className="stat-number">{stats.totalPatients}</div>
              <div className="stat-label">Total Patients</div>
            </div>
            <div className="stat-card active">
              <div className="stat-number">{stats.activePatients}</div>
              <div className="stat-label">Active Patients</div>
            </div>
            <div className="stat-card uploaded">
              <div className="stat-number">{stats.recordsUploaded}</div>
              <div className="stat-label">Records Uploaded</div>
            </div>
            <div className="stat-card pending">
              <div className="stat-number">{stats.pendingConsent}</div>
              <div className="stat-label">Pending Consent</div>
            </div>
          </div>
        </div>

        <div className="patients-section">
          <div className="section-header">
            <h3>Patient Management</h3>
            <div className="actions">
              <Link to="/hospital/upload" className="upload-btn">
                Upload Records
              </Link>
            </div>
          </div>

          <div className="filters">
            <input
              type="text"
              placeholder="Search patients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="status-filter"
            >
              <option value="All">All Status</option>
              <option value="Active">Active</option>
              <option value="Discharged">Discharged</option>
            </select>
          </div>

          <div className="patients-table">
            <div className="table-header">
              <div className="header-cell">Patient ID</div>
              <div className="header-cell">Patient Name</div>
              <div className="header-cell">Admission Date</div>
              <div className="header-cell">Status</div>
              <div className="header-cell">Consent Status</div>
              <div className="header-cell">Actions</div>
            </div>
            
            {filteredPatients.map((patient) => (
              <div key={patient.id} className="table-row">
                <div className="table-cell patient-id">{patient.id}</div>
                <div className="table-cell">{patient.name}</div>
                <div className="table-cell">{new Date(patient.admissionDate).toLocaleDateString()}</div>
                <div className="table-cell">
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(patient.status) }}
                  >
                    {patient.status}
                  </span>
                </div>
                <div className="table-cell">
                  <span 
                    className="consent-badge"
                    style={{ backgroundColor: getConsentColor(patient.consentStatus) }}
                  >
                    {patient.consentStatus}
                  </span>
                </div>
                <div className="table-cell">
                  <Link 
                    to="/hospital/upload"
                    className={`action-btn ${patient.consentStatus !== 'Approved' ? 'disabled' : ''}`}
                  >
                    Upload Records
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {filteredPatients.length === 0 && (
            <div className="no-results">
              No patients found matching your criteria.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HospitalDashboard;