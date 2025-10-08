import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('medimate_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('medimate_token');
      localStorage.removeItem('medimate_user');
      window.location.href = '/login';
    }
    
    return Promise.reject({
      message: error.response?.data?.message || error.message || 'An error occurred',
      status: error.response?.status,
      data: error.response?.data
    });
  }
);

// Authentication API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (userData) => api.put('/auth/profile', userData),
  logout: () => api.post('/auth/logout'),
};

// Patient API
export const patientAPI = {
  getDashboard: () => api.get('/patient/dashboard'),
  getClaims: (params) => api.get('/patient/claims', { params }),
  getClaim: (claimId) => api.get(`/patient/claims/${claimId}`),
  createClaim: (claimData) => api.post('/patient/claims', claimData),
  getConsents: () => api.get('/patient/consents'),
  grantConsent: (consentData) => api.post('/patient/consents', consentData),
  revokeConsent: (consentId, reason) => api.put(`/patient/consents/${consentId}/revoke`, { reason }),
};

// Insurer API
export const insurerAPI = {
  getDashboard: () => api.get('/insurer/dashboard'),
  getClaims: (params) => api.get('/insurer/claims', { params }),
  getClaim: (claimId) => api.get(`/insurer/claims/${claimId}`),
  reviewClaim: (claimId, reviewData) => api.put(`/insurer/claims/${claimId}/review`, reviewData),
  extractAI: (claimId) => api.post(`/insurer/claims/${claimId}/ai-extract`),
};

// Hospital API
export const hospitalAPI = {
  getDashboard: () => api.get('/hospital/dashboard'),
  getPatients: (params) => api.get('/hospital/patients', { params }),
  getClaims: (params) => api.get('/hospital/claims', { params }),
  createClaim: (claimData) => api.post('/hospital/claims', claimData),
  updateClaim: (claimId, claimData) => api.put(`/hospital/claims/${claimId}`, claimData),
  getConsents: () => api.get('/hospital/consents'),
};

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: (params) => api.get('/admin/users', { params }),
  getClaims: (params) => api.get('/admin/claims', { params }),
  getAnalytics: (params) => api.get('/admin/analytics', { params }),
  updateUserStatus: (userId, status) => api.put(`/admin/users/${userId}/status`, status),
  deleteClaim: (claimId) => api.delete(`/admin/claims/${claimId}`),
};

// File Upload API
export const uploadAPI = {
  uploadDocument: (formData, onProgress) => {
    return api.post('/upload/document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    });
  },
  uploadMultiple: (formData, onProgress) => {
    return api.post('/upload/multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    });
  },
  getDocument: (filename) => api.get(`/upload/document/${filename}`, {
    responseType: 'blob',
  }),
  deleteDocument: (documentId) => api.delete(`/upload/document/${documentId}`),
};

// Health Check
export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;