const express = require('express');
const Claim = require('../models/Claim');
const Consent = require('../models/Consent');
const User = require('../models/User');
const { authorize } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/hospital/dashboard
// @desc    Get hospital dashboard data
// @access  Private (Hospital only)
router.get('/dashboard', authorize('hospital'), async (req, res) => {
  try {
    const hospitalId = req.user._id;
    
    // Get patients with consent
    const consents = await Consent.find({ 
      entity: hospitalId, 
      entityType: 'hospital',
      status: 'granted'
    }).populate('patient', 'fullName email');
    
    // Get claims statistics
    const stats = {
      totalPatients: consents.length,
      activePatients: await Claim.countDocuments({ 
        hospital: hospitalId, 
        status: { $in: ['submitted', 'under_review'] }
      }),
      recordsUploaded: await Claim.countDocuments({ hospital: hospitalId }),
      pendingConsent: await Consent.countDocuments({ 
        entity: hospitalId, 
        entityType: 'hospital',
        status: 'granted'
      })
    };
    
    // Get recent claims
    const recentClaims = await Claim.find({ hospital: hospitalId })
      .populate('patient', 'fullName')
      .populate('insurer', 'insurerData.companyName')
      .sort({ createdAt: -1 })
      .limit(5);
    
    res.json({
      success: true,
      data: {
        stats,
        recentClaims,
        patients: consents.map(c => ({
          ...c.patient.toObject(),
          consentStatus: c.status,
          consentDate: c.grantedAt
        }))
      }
    });
    
  } catch (error) {
    console.error('Hospital dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching dashboard data'
    });
  }
});

// @route   GET /api/hospital/patients
// @desc    Get patients with consent
// @access  Private (Hospital only)
router.get('/patients', authorize('hospital'), async (req, res) => {
  try {
    const { search, status = 'granted' } = req.query;
    const hospitalId = req.user._id;
    
    // Build query
    const query = { 
      entity: hospitalId, 
      entityType: 'hospital',
      status: status
    };
    
    let consents = await Consent.find(query)
      .populate('patient', 'fullName email phoneNumber patientData')
      .sort({ createdAt: -1 });
    
    // Apply search filter
    if (search) {
      consents = consents.filter(consent => 
        consent.patient.fullName.toLowerCase().includes(search.toLowerCase()) ||
        consent.patient.email.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    const patients = consents.map(consent => ({
      id: consent.patient._id,
      fullName: consent.patient.fullName,
      email: consent.patient.email,
      phoneNumber: consent.patient.phoneNumber,
      consentStatus: consent.status,
      consentDate: consent.grantedAt,
      patientData: consent.patient.patientData
    }));
    
    res.json({
      success: true,
      data: { patients }
    });
    
  } catch (error) {
    console.error('Get patients error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching patients'
    });
  }
});

// @route   GET /api/hospital/claims
// @desc    Get hospital claims
// @access  Private (Hospital only)
router.get('/claims', authorize('hospital'), async (req, res) => {
  try {
    const { status, page = 1, limit = 10 } = req.query;
    const hospitalId = req.user._id;
    
    // Build query
    const query = { hospital: hospitalId };
    if (status) query.status = status;
    
    const claims = await Claim.find(query)
      .populate('patient', 'fullName email')
      .populate('insurer', 'insurerData.companyName')
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit);
    
    const total = await Claim.countDocuments(query);
    
    res.json({
      success: true,
      data: {
        claims,
        pagination: {
          current: parseInt(page),
          pages: Math.ceil(total / limit),
          total
        }
      }
    });
    
  } catch (error) {
    console.error('Get hospital claims error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching claims'
    });
  }
});

// @route   POST /api/hospital/claims
// @desc    Create claim for patient
// @access  Private (Hospital only)
router.post('/claims', authorize('hospital'), async (req, res) => {
  try {
    const hospitalId = req.user._id;
    const {
      patientId,
      insurerId,
      medicalInfo,
      financialInfo
    } = req.body;
    
    // Verify patient consent
    const hasConsent = await Consent.checkConsent(patientId, hospitalId, 'hospital');
    
    if (!hasConsent) {
      return res.status(403).json({
        success: false,
        message: 'Patient consent required before creating claim'
      });
    }
    
    // Verify insurer exists
    const insurer = await User.findById(insurerId);
    if (!insurer || insurer.role !== 'insurer') {
      return res.status(400).json({
        success: false,
        message: 'Invalid insurer'
      });
    }
    
    // Create claim
    const claim = new Claim({
      patient: patientId,
      hospital: hospitalId,
      insurer: insurerId,
      medicalInfo,
      financialInfo,
      status: 'submitted'
    });
    
    await claim.save();
    
    // Add initial timeline entry
    await claim.updateStatus('submitted', hospitalId, 'Claim submitted by hospital');
    
    // Populate for response
    await claim.populate('patient', 'fullName email');
    await claim.populate('insurer', 'insurerData.companyName');
    
    // Emit real-time update
    const io = req.app.get('io');
    io.to(insurerId.toString()).emit('new-claim-submitted', {
      claimId: claim.claimId,
      patientName: claim.patient.fullName,
      hospitalName: req.user.hospitalData?.hospitalName,
      submittedAt: new Date()
    });
    
    res.status(201).json({
      success: true,
      message: 'Claim created successfully',
      data: { claim }
    });
    
  } catch (error) {
    console.error('Create claim error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error creating claim'
    });
  }
});

// @route   PUT /api/hospital/claims/:claimId
// @desc    Update claim information
// @access  Private (Hospital only)
router.put('/claims/:claimId', authorize('hospital'), async (req, res) => {
  try {
    const claim = await Claim.findOne({
      claimId: req.params.claimId,
      hospital: req.user._id
    });
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Claim not found'
      });
    }
    
    // Only allow updates if claim is in draft or submitted status
    if (!['draft', 'submitted'].includes(claim.status)) {
      return res.status(400).json({
        success: false,
        message: 'Cannot update claim in current status'
      });
    }
    
    const allowedUpdates = ['medicalInfo', 'financialInfo'];
    const updates = {};
    
    Object.keys(req.body).forEach(key => {
      if (allowedUpdates.includes(key)) {
        updates[key] = req.body[key];
      }
    });
    
    Object.assign(claim, updates);
    await claim.save();
    
    res.json({
      success: true,
      message: 'Claim updated successfully',
      data: { claim }
    });
    
  } catch (error) {
    console.error('Update claim error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error updating claim'
    });
  }
});

// @route   GET /api/hospital/consents
// @desc    Get patient consents for hospital
// @access  Private (Hospital only)
router.get('/consents', authorize('hospital'), async (req, res) => {
  try {
    const consents = await Consent.find({ 
      entity: req.user._id, 
      entityType: 'hospital' 
    })
    .populate('patient', 'fullName email phoneNumber')
    .sort({ createdAt: -1 });
    
    res.json({
      success: true,
      data: { consents }
    });
    
  } catch (error) {
    console.error('Get consents error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching consents'
    });
  }
});

module.exports = router;