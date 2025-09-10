import { Link } from 'react-router-dom';
import './PatientDashboard.css';

const PatientDashboard = () => {
    const patientName = "John Doe"; // This would come from auth context
    const claimStatus = "In Processing";

    return (
        <div className="patient-dashboard">
            <header className="dashboard-header">
                <div className="logo">MediMate</div>
                <div className="welcome">Welcome, {patientName}</div>
            </header>

            <div className="dashboard-content">
                <div className="claim-status-section">
                    <h3>Claim Status: {claimStatus}</h3>
                    <div className="timeline-view">
                        <div className="timeline-step completed">
                            <div className="step-circle"></div>
                            <span>Submitted</span>
                        </div>
                        <div className="timeline-step active">
                            <div className="step-circle"></div>
                            <span>In Processing</span>
                        </div>
                        <div className="timeline-step">
                            <div className="step-circle"></div>
                            <span>Approved</span>
                        </div>
                    </div>
                </div>

                <div className="action-buttons">
                    <Link to="/patient/upload-documents" className="action-btn">
                        Upload Documents
                    </Link>
                    <Link to="/patient/consent" className="action-btn">
                        Give Consent
                    </Link>
                    <Link to="/patient/track-claims" className="action-btn">
                        Track Claims
                    </Link>
                    <Link to="/patient/profile" className="action-btn">
                        Profile Settings
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default PatientDashboard;