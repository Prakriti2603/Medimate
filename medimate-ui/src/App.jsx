import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';

// Patient Module Components
import PatientDashboard from './pages/patient/PatientDashboard';
import UploadDocuments from './pages/patient/UploadDocuments';
import ConsentManagement from './pages/patient/ConsentManagement';
import ClaimTracking from './pages/patient/ClaimTracking';

// Insurer Module Components
import InsurerDashboard from './pages/insurer/InsurerDashboard';
import ClaimReview from './pages/insurer/ClaimReview';

// Hospital Module Components
import HospitalDashboard from './pages/hospital/HospitalDashboard';
import HospitalUpload from './pages/hospital/HospitalUpload';

// Admin Module Components
import AdminDashboard from './pages/admin/AdminDashboard';

// Module Selector
import ModuleSelector from './components/ModuleSelector';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/modules" element={<ModuleSelector />} />
        
        {/* Patient Module Routes */}
        <Route path="/patient/dashboard" element={<PatientDashboard />} />
        <Route path="/patient/upload-documents" element={<UploadDocuments />} />
        <Route path="/patient/consent" element={<ConsentManagement />} />
        <Route path="/patient/track-claims" element={<ClaimTracking />} />
        
        {/* Insurer Module Routes */}
        <Route path="/insurer/dashboard" element={<InsurerDashboard />} />
        <Route path="/insurer/claim-review/:claimId" element={<ClaimReview />} />
        
        {/* Hospital Module Routes */}
        <Route path="/hospital/dashboard" element={<HospitalDashboard />} />
        <Route path="/hospital/upload" element={<HospitalUpload />} />
        
        {/* Admin Module Routes */}
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;