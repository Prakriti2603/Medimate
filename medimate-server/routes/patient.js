const express = require('express');
const Claim = require('../models/Claim');
const Consent = require('../models/Consent');
const User = require('../models/User');
const { authorize } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/patient/dashboard
// @desc    Get patient dashboard data
// @access  Private (Patient only)
router.get('/dashboard', authorize('patient'), async (req, res) => {
  try {
    const patientId = req.user._id;
    
    // Get claims summary
    const claims = await Claim.find({ patient: patientId })
      .populate('hospital', 'hospitalData.hospitalName')
      .populate('insurer', 'insurerData.companyName')
      .sort({ createdAt: -1 })
      .limit(5);
    
    // Get consent status
    const consents = await Consent.find({ patient: patientId })
      .populate('entity', 'hospitalData.hospitalName insurerData.companyName role')
      .sort({ createdAt: -1 });
    
    // Calculate statistics
    const stats = {
      totalClaims: await Claim.countDocuments({ patient: patientId }),
      pendingClaims: await Claim.countDocuments({ 
        patient: patientId, 
        status: { $in: ['submitted', 'under_review'] } 
      }),
      approvedClaims: await Claim.countDocuments({ 
        patient: patientId, 
        status: 'approved' 
      }),
      totalClaimedAmount: await Claim.aggregate([
        { $match: { patient: patientId } },
        { $group: { _id: null, total: { $sum: '$financialInfo.claimedAmount' } } }
      ]).then(result => result[0]?.total || 0)
    };
    
    res.json({
      success: true,
      data: {
        stats,
        recentClaims: claims,
        consents
      }
    });
    
  } catch (error) {
    console.error('Patient dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching dashboard data'
    });
  }
});

// @route   GET /api/patient/claims
// @desc    Get all patient claims
// @access  Private (Patient only)
router.get('/claims', authorize('patient'), async (req, res) => {
  try {
    const patientId = req.user._id;
    const { status, page = 1, limit = 10 } = req.query;
    
    // Build query
    const query = { patient: patientId };
    if (status) query.status = status;
    
    // Get claims with pagination
    const claims = await Claim.find(query)
      .populate('hospital', 'hospitalData.hospitalName')
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
          current: page,
          pages: Math.ceil(total / limit),
          total
        }
      }
    });
    
  } catch (error) {
    console.error('Get claims error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching claims'
    });
  }
});

// @route   GET /api/patient/claims/:claimId
// @desc    Get specific claim details
// @access  Private (Patient only)
router.get('/claims/:claimId', authorize('patient'), async (req, res) => {
  try {
    const claim = await Claim.findOne({
      claimId: req.params.claimId,
      patient: req.user._id
    })
    .populate('hospital', 'hospitalData.hospitalName hospitalData.address')
    .populate('insurer', 'insurerData.companyName insurerData.address')
    .populate('timeline.updatedBy', 'fullName role');
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Claim not found'
      });
    }
    
    res.json({
      success: true,
      data: { claim }
    });
    
  } catch (error) {
    console.error('Get claim error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching claim'
    });
  }
});

// @route   POST /api/patient/claims
// @desc    Create new claim
// @access  Private (Patient only)
router.post('/claims', authorize('patient'), async (req, res) => {
  try {
    const patientId = req.user._id;
    const {
      hospital,
      insurer,
      medicalInfo,
      financialInfo
    } = req.body;
    
    // Verify hospital and insurer exist
    const hospitalUser = await User.findById(hospital);
    const insurerUser = await User.findById(insurer);
    
    if (!hospitalUser || hospitalUser.role !== 'hospital') {
      return res.status(400).json({
        success: false,
        message: 'Invalid hospital'
      });
    }
    
    if (!insurerUser || insurerUser.role !== 'insurer') {
      return res.status(400).json({
        success: false,
        message: 'Invalid insurer'
      });
    }
    
    // Create claim
    const claim = new Claim({
      patient: patientId,
      hospital,
      insurer,
      medicalInfo,
      financialInfo,
      status: 'draft'
    });
    
    await claim.save();
    
    // Populate for response
    await claim.populate('hospital', 'hospitalData.hospitalName');
    await claim.populate('insurer', 'insurerData.companyName');
    
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

// @route   GET /api/patient/consents
// @desc    Get patient consents
// @access  Private (Patient only)
router.get('/consents', authorize('patient'), async (req, res) => {
  try {
    const consents = await Consent.find({ patient: req.user._id })
      .populate('entity', 'hospitalData.hospitalName insurerData.companyName role')
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

// @route   POST /api/patient/consents
// @desc    Grant consent to entity
// @access  Private (Patient only)
router.post('/consents', authorize('patient'), async (req, res) => {
  try {
    const { entityId, entityType, permissions, expiresAt } = req.body;
    
    // Check if consent already exists
    const existingConsent = await Consent.findOne({
      patient: req.user._id,
      entity: entityId,
      entityType
    });
    
    if (existingConsent && existingConsent.status === 'granted') {
      return res.status(400).json({
        success: false,
        message: 'Consent already granted to this entity'
      });
    }
    
    // Create or update consent
    const consentData = {
      patient: req.user._id,
      entity: entityId,
      entityType,
      permissions: permissions || {},
      expiresAt: expiresAt || new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
      status: 'granted',
      blockchain: {
        transactionHash: 'demo_' + Date.now(), // In real implementation, this would be actual blockchain hash
        confirmed: true
      }
    };
    
    let consent;
    if (existingConsent) {
      consent = await Consent.findByIdAndUpdate(existingConsent._id, consentData, { new: true });
    } else {
      consent = new Consent(consentData);
      await consent.save();
    }
    
    await consent.populate('entity', 'hospitalData.hospitalName insurerData.companyName role');
    
    // Emit real-time update
    const io = req.app.get('io');
    io.to(entityId.toString()).emit('consent-granted', {
      patientId: req.user._id,
      patientName: req.user.fullName,
      consentId: consent._id
    });
    
    res.status(201).json({
      success: true,
      message: 'Consent granted successfully',
      data: { consent }
    });
    
  } catch (error) {
    console.error('Grant consent error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error granting consent'
    });
  }
});

// @route   PUT /api/patient/consents/:consentId/revoke
// @desc    Revoke consent
// @access  Private (Patient only)
router.put('/consents/:consentId/revoke', authorize('patient'), async (req, res) => {
  try {
    const { reason } = req.body;
    
    const consent = await Consent.findOne({
      _id: req.params.consentId,
      patient: req.user._id
    });
    
    if (!consent) {
      return res.status(404).json({
        success: false,
        message: 'Consent not found'
      });
    }
    
    await consent.revoke(reason);
    await consent.populate('entity', 'hospitalData.hospitalName insurerData.companyName role');
    
    // Emit real-time update
    const io = req.app.get('io');
    io.to(consent.entity._id.toString()).emit('consent-revoked', {
      patientId: req.user._id,
      patientName: req.user.fullName,
      consentId: consent._id
    });
    
    res.json({
      success: true,
      message: 'Consent revoked successfully',
      data: { consent }
    });
    
  } catch (error) {
    console.error('Revoke consent error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error revoking consent'
    });
  }
});

module.exports = router;