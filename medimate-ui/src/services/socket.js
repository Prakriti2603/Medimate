import { io } from 'socket.io-client';
import { toast } from 'react-toastify';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = new Map();
  }

  connect(userId) {
    if (this.socket) {
      this.disconnect();
    }

    const serverUrl = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';
    
    this.socket = io(serverUrl, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true,
    });

    this.socket.on('connect', () => {
      console.log('✅ Connected to MediMate server');
      this.isConnected = true;
      
      // Join user-specific room
      if (userId) {
        this.socket.emit('join-room', userId);
      }
      
      toast.success('Connected to MediMate server', {
        position: 'bottom-right',
        autoClose: 3000,
      });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('❌ Disconnected from server:', reason);
      this.isConnected = false;
      
      toast.warning('Connection lost. Attempting to reconnect...', {
        position: 'bottom-right',
        autoClose: 5000,
      });
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      toast.error('Failed to connect to server', {
        position: 'bottom-right',
        autoClose: 5000,
      });
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('🔄 Reconnected after', attemptNumber, 'attempts');
      toast.success('Reconnected to server', {
        position: 'bottom-right',
        autoClose: 3000,
      });
    });

    // Set up real-time event listeners
    this.setupEventListeners();

    return this.socket;
  }

  setupEventListeners() {
    if (!this.socket) return;

    // Claim status updates
    this.socket.on('claim-status-changed', (data) => {
      console.log('📋 Claim status updated:', data);
      toast.info(`Claim ${data.claimId} status: ${data.status}`, {
        position: 'top-right',
        autoClose: 5000,
      });
      
      // Trigger custom listeners
      this.emit('claimStatusChanged', data);
    });

    // Document upload notifications
    this.socket.on('new-document', (data) => {
      console.log('📄 New document uploaded:', data);
      toast.info(`New document uploaded for claim ${data.claimId}`, {
        position: 'top-right',
        autoClose: 5000,
      });
      
      this.emit('documentUploaded', data);
    });

    // Consent updates
    this.socket.on('consent-updated', (data) => {
      console.log('🔐 Consent updated:', data);
      toast.info(`Consent updated for patient ${data.patientName}`, {
        position: 'top-right',
        autoClose: 5000,
      });
      
      this.emit('consentUpdated', data);
    });

    // New claim notifications
    this.socket.on('new-claim-submitted', (data) => {
      console.log('🆕 New claim submitted:', data);
      toast.info(`New claim ${data.claimId} submitted`, {
        position: 'top-right',
        autoClose: 5000,
      });
      
      this.emit('newClaimSubmitted', data);
    });

    // Multiple documents uploaded
    this.socket.on('multiple-documents-uploaded', (data) => {
      console.log('📁 Multiple documents uploaded:', data);
      toast.success(`${data.documentCount} documents uploaded successfully`, {
        position: 'top-right',
        autoClose: 5000,
      });
      
      this.emit('multipleDocumentsUploaded', data);
    });

    // Consent granted/revoked
    this.socket.on('consent-granted', (data) => {
      console.log('✅ Consent granted:', data);
      toast.success(`Consent granted by ${data.patientName}`, {
        position: 'top-right',
        autoClose: 5000,
      });
      
      this.emit('consentGranted', data);
    });

    this.socket.on('consent-revoked', (data) => {
      console.log('❌ Consent revoked:', data);
      toast.warning(`Consent revoked by ${data.patientName}`, {
        position: 'top-right',
        autoClose: 5000,
      });
      
      this.emit('consentRevoked', data);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      this.listeners.clear();
    }
  }

  // Custom event system for components
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in socket event callback:', error);
        }
      });
    }
  }

  // Send events to server
  sendClaimUpdate(data) {
    if (this.socket && this.isConnected) {
      this.socket.emit('claim-update', data);
    }
  }

  sendDocumentUploaded(data) {
    if (this.socket && this.isConnected) {
      this.socket.emit('document-uploaded', data);
    }
  }

  sendConsentChanged(data) {
    if (this.socket && this.isConnected) {
      this.socket.emit('consent-changed', data);
    }
  }

  // Utility methods
  isSocketConnected() {
    return this.isConnected && this.socket?.connected;
  }

  getSocket() {
    return this.socket;
  }
}

// Create singleton instance
const socketService = new SocketService();

export default socketService;