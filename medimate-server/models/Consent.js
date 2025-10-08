const mongoose = require('mongoose');

const consentSchema = new mongoose.Schema({
  patient: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  entity: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  entityType: {
    type: String,
    enum: ['hospital', 'insurer'],
    required: true
  },
  
  // Consent Details
  consentType: {
    type: String,
    enum: ['data_sharing', 'treatment', 'billing', 'research'],
    default: 'data_sharing'
  },
  status: {
    type: String,
    enum: ['granted', 'revoked', 'expired'],
    default: 'granted'
  },
  
  // Permissions
  permissions: {
    viewMedicalRecords: { type: Boolean, default: false },
    shareWithThirdParty: { type: Boolean, default: false },
    useForResearch: { type: Boolean, default: false },
    marketingCommunication: { type: Boolean, default: false }
  },
  
  // Validity
  grantedAt: {
    type: Date,
    default: Date.now
  },
  expiresAt: {
    type: Date,
    required: true,
    default: function() {
      // Default expiry: 1 year from now
      return new Date(Date.now() + 365 * 24 * 60 * 60 * 1000);
    }
  },
  revokedAt: Date,
  
  // Blockchain Integration
  blockchain: {
    transactionHash: String,
    blockNumber: Number,
    networkId: String,
    gasUsed: Number,
    confirmed: { type: Boolean, default: false }
  },
  
  // Audit Trail
  auditTrail: [{
    action: {
      type: String,
      enum: ['granted', 'modified', 'revoked', 'expired', 'renewed']
    },
    timestamp: { type: Date, default: Date.now },
    ipAddress: String,
    userAgent: String,
    reason: String
  }],
  
  // Legal and Compliance
  legalBasis: {
    type: String,
    enum: ['consent', 'contract', 'legal_obligation', 'vital_interests', 
           'public_task', 'legitimate_interests'],
    default: 'consent'
  },
  consentVersion: {
    type: String,
    default: '1.0'
  },
  
  // Metadata
  metadata: {
    consentMethod: {
      type: String,
      enum: ['web', 'mobile', 'paper', 'verbal'],
      default: 'web'
    },
    language: { type: String, default: 'en' },
    jurisdiction: { type: String, default: 'IN' }
  }
  
}, {
  timestamps: true
});

// Indexes
consentSchema.index({ patient: 1, entity: 1, entityType: 1 });
consentSchema.index({ status: 1, expiresAt: 1 });
consentSchema.index({ 'blockchain.transactionHash': 1 });

// Virtual for checking if consent is active
consentSchema.virtual('isActive').get(function() {
  return this.status === 'granted' && this.expiresAt > new Date();
});

// Method to revoke consent
consentSchema.methods.revoke = function(reason = '') {
  this.status = 'revoked';
  this.revokedAt = new Date();
  this.auditTrail.push({
    action: 'revoked',
    timestamp: new Date(),
    reason: reason
  });
  return this.save();
};

// Method to renew consent
consentSchema.methods.renew = function(newExpiryDate) {
  this.status = 'granted';
  this.expiresAt = newExpiryDate;
  this.revokedAt = undefined;
  this.auditTrail.push({
    action: 'renewed',
    timestamp: new Date()
  });
  return this.save();
};

// Static method to check consent between entities
consentSchema.statics.checkConsent = async function(patientId, entityId, entityType) {
  const consent = await this.findOne({
    patient: patientId,
    entity: entityId,
    entityType: entityType,
    status: 'granted',
    expiresAt: { $gt: new Date() }
  });
  
  return !!consent;
};

module.exports = mongoose.model('Consent', consentSchema);