import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

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

// AI Module Components
import AIFormProcessor from './pages/AIFormProcessor';

// Module Selector
import ModuleSelector from './components/ModuleSelector';

// Protected Route Component
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/modules" element={<ProtectedRoute><ModuleSelector /></ProtectedRoute>} />
          
          {/* Patient Module Routes */}
          <Route path="/patient/dashboard" element={<ProtectedRoute allowedRoles={['patient']}><PatientDashboard /></ProtectedRoute>} />
          <Route path="/patient/upload-documents" element={<ProtectedRoute allowedRoles={['patient']}><UploadDocuments /></ProtectedRoute>} />
          <Route path="/patient/consent" element={<ProtectedRoute allowedRoles={['patient']}><ConsentManagement /></ProtectedRoute>} />
          <Route path="/patient/track-claims" element={<ProtectedRoute allowedRoles={['patient']}><ClaimTracking /></ProtectedRoute>} />
          
          {/* Insurer Module Routes */}
          <Route path="/insurer/dashboard" element={<ProtectedRoute allowedRoles={['insurer']}><InsurerDashboard /></ProtectedRoute>} />
          <Route path="/insurer/claim-review/:claimId" element={<ProtectedRoute allowedRoles={['insurer']}><ClaimReview /></ProtectedRoute>} />
          
          {/* Hospital Module Routes */}
          <Route path="/hospital/dashboard" element={<ProtectedRoute allowedRoles={['hospital']}><HospitalDashboard /></ProtectedRoute>} />
          <Route path="/hospital/upload" element={<ProtectedRoute allowedRoles={['hospital']}><HospitalUpload /></ProtectedRoute>} />
          
          {/* Admin Module Routes */}
          <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['admin']}><AdminDashboard /></ProtectedRoute>} />
          
          {/* AI Module Routes */}
          <Route path="/ai/form-processor" element={<ProtectedRoute><AIFormProcessor /></ProtectedRoute>} />
        </Routes>
        
        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;