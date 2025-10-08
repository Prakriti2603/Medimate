const mongoose = require('mongoose');

const claimSchema = new mongoose.Schema({
  claimId: {
    type: String,
    required: true,
    unique: true,
    default: function() {
      return 'CLM' + new Date().getFullYear() + '-' + 
             String(Math.floor(Math.random() * 10000)).padStart(3, '0');
    }
  },
  patient: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  hospital: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  insurer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  
  // Medical Information
  medicalInfo: {
    admissionDate: {
      type: Date,
      required: true
    },
    dischargeDate: {
      type: Date,
      required: true
    },
    diagnosis: {
      primary: { type: String, required: true },
      secondary: [String],
      icdCodes: [String]
    },
    treatment: {
      description: String,
      procedures: [String],
      medications: [String]
    },
    doctorInfo: {
      name: String,
      specialization: String,
      licenseNumber: String
    }
  },
  
  // Financial Information
  financialInfo: {
    totalAmount: {
      type: Number,
      required: true,
      min: 0
    },
    breakdown: {
      roomCharges: { type: Number, default: 0 },
      doctorFees: { type: Number, default: 0 },
      medicineCharges: { type: Number, default: 0 },
      labCharges: { type: Number, default: 0 },
      otherCharges: { type: Number, default: 0 }
    },
    claimedAmount: {
      type: Number,
      required: true,
      min: 0
    },
    approvedAmount: {
      type: Number,
      default: 0
    }
  },
  
  // Documents
  documents: [{
    type: {
      type: String,
      enum: ['insurance', 'idProof', 'admission', 'discharge', 'hospitalBill', 
             'pharmacy', 'labReports', 'prescriptions'],
      required: true
    },
    filename: { type: String, required: true },
    originalName: { type: String, required: true },
    path: { type: String, required: true },
    size: { type: Number, required: true },
    mimeType: { type: String, required: true },
    uploadedAt: { type: Date, default: Date.now },
    uploadedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    }
  }],
  
  // AI Extraction Results
  aiExtraction: {
    confidence: { type: Number, min: 0, max: 100 },
    extractedData: {
      policyNumber: String,
      patientName: String,
      admissionDate: Date,
      dischargeDate: Date,
      diagnosis: String,
      totalBill: Number
    },
    processedAt: Date,
    version: String
  },
  
  // Status and Timeline
  status: {
    type: String,
    enum: ['draft', 'submitted', 'under_review', 'approved', 'rejected', 'paid'],
    default: 'draft'
  },
  timeline: [{
    status: {
      type: String,
      enum: ['submitted', 'under_review', 'approved', 'rejected', 'paid']
    },
    timestamp: { type: Date, default: Date.now },
    updatedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    comments: String,
    attachments: [String]
  }],
  
  // Review Information
  reviewInfo: {
    reviewer: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    reviewDate: Date,
    comments: String,
    internalNotes: String,
    flagged: { type: Boolean, default: false },
    flagReason: String
  },
  
  // Consent and Blockchain
  consent: {
    patientConsent: { type: Boolean, default: false },
    consentDate: Date,
    blockchainHash: String,
    consentVersion: String
  },
  
  // Metadata
  priority: {
    type: String,
    enum: ['low', 'medium', 'high', 'urgent'],
    default: 'medium'
  },
  tags: [String],
  isArchived: { type: Boolean, default: false }
  
}, {
  timestamps: true
});

// Indexes for better performance
claimSchema.index({ claimId: 1 });
claimSchema.index({ patient: 1, status: 1 });
claimSchema.index({ insurer: 1, status: 1 });
claimSchema.index({ hospital: 1, status: 1 });
claimSchema.index({ 'timeline.timestamp': -1 });

// Virtual for claim age
claimSchema.virtual('ageInDays').get(function() {
  return Math.floor((Date.now() - this.createdAt) / (1000 * 60 * 60 * 24));
});

// Method to update status with timeline
claimSchema.methods.updateStatus = function(newStatus, updatedBy, comments = '') {
  this.status = newStatus;
  this.timeline.push({
    status: newStatus,
    timestamp: new Date(),
    updatedBy: updatedBy,
    comments: comments
  });
  return this.save();
};

// Method to add document
claimSchema.methods.addDocument = function(documentData) {
  this.documents.push(documentData);
  return this.save();
};

module.exports = mongoose.model('Claim', claimSchema);