const express = require('express');
const Claim = require('../models/Claim');
const { authorize } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/insurer/dashboard
// @desc    Get insurer dashboard data
// @access  Private (Insurer only)
router.get('/dashboard', authorize('insurer'), async (req, res) => {
  try {
    const insurerId = req.user._id;
    
    // Get claims statistics
    const stats = {
      pending: await Claim.countDocuments({ insurer: insurerId, status: 'submitted' }),
      inReview: await Claim.countDocuments({ insurer: insurerId, status: 'under_review' }),
      approved: await Claim.countDocuments({ insurer: insurerId, status: 'approved' }),
      rejected: await Claim.countDocuments({ insurer: insurerId, status: 'rejected' })
    };
    
    // Get recent claims
    const recentClaims = await Claim.find({ insurer: insurerId })
      .populate('patient', 'fullName')
      .populate('hospital', 'hospitalData.hospitalName')
      .sort({ createdAt: -1 })
      .limit(10);
    
    res.json({
      success: true,
      data: {
        stats,
        recentClaims
      }
    });
    
  } catch (error) {
    console.error('Insurer dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching dashboard data'
    });
  }
});

// @route   GET /api/insurer/claims
// @desc    Get all claims for insurer
// @access  Private (Insurer only)
router.get('/claims', authorize('insurer'), async (req, res) => {
  try {
    const { status, search, page = 1, limit = 10 } = req.query;
    const insurerId = req.user._id;
    
    // Build query
    const query = { insurer: insurerId };
    if (status) query.status = status;
    
    // Add search functionality
    if (search) {
      query.$or = [
        { claimId: { $regex: search, $options: 'i' } },
        { 'medicalInfo.diagnosis.primary': { $regex: search, $options: 'i' } }
      ];
    }
    
    const claims = await Claim.find(query)
      .populate('patient', 'fullName email phoneNumber')
      .populate('hospital', 'hospitalData.hospitalName')
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
    console.error('Get insurer claims error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching claims'
    });
  }
});

// @route   GET /api/insurer/claims/:claimId
// @desc    Get specific claim for review
// @access  Private (Insurer only)
router.get('/claims/:claimId', authorize('insurer'), async (req, res) => {
  try {
    const claim = await Claim.findOne({
      claimId: req.params.claimId,
      insurer: req.user._id
    })
    .populate('patient', 'fullName email phoneNumber patientData')
    .populate('hospital', 'hospitalData')
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

// @route   PUT /api/insurer/claims/:claimId/review
// @desc    Update claim status (approve/reject)
// @access  Private (Insurer only)
router.put('/claims/:claimId/review', authorize('insurer'), async (req, res) => {
  try {
    const { status, comments, approvedAmount } = req.body;
    
    if (!['approved', 'rejected', 'under_review'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid status'
      });
    }
    
    const claim = await Claim.findOne({
      claimId: req.params.claimId,
      insurer: req.user._id
    });
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Claim not found'
      });
    }
    
    // Update claim status
    await claim.updateStatus(status, req.user._id, comments);
    
    // Update review information
    claim.reviewInfo = {
      reviewer: req.user._id,
      reviewDate: new Date(),
      comments: comments || '',
      internalNotes: req.body.internalNotes || ''
    };
    
    // Update approved amount if provided
    if (status === 'approved' && approvedAmount) {
      claim.financialInfo.approvedAmount = approvedAmount;
    }
    
    await claim.save();
    
    // Populate for response
    await claim.populate('patient', 'fullName email');
    await claim.populate('hospital', 'hospitalData.hospitalName');
    
    // Emit real-time update to patient
    const io = req.app.get('io');
    io.to(claim.patient._id.toString()).emit('claim-status-updated', {
      claimId: claim.claimId,
      status: status,
      comments: comments,
      updatedAt: new Date()
    });
    
    res.json({
      success: true,
      message: `Claim ${status} successfully`,
      data: { claim }
    });
    
  } catch (error) {
    console.error('Review claim error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error reviewing claim'
    });
  }
});

// @route   POST /api/insurer/claims/:claimId/ai-extract
// @desc    Trigger AI extraction for claim documents
// @access  Private (Insurer only)
router.post('/claims/:claimId/ai-extract', authorize('insurer'), async (req, res) => {
  try {
    const claim = await Claim.findOne({
      claimId: req.params.claimId,
      insurer: req.user._id
    });
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Claim not found'
      });
    }
    
    // Simulate AI extraction (in real implementation, this would call AI service)
    const mockAiExtraction = {
      confidence: Math.floor(Math.random() * 20) + 80, // 80-99%
      extractedData: {
        policyNumber: 'POL' + Math.floor(Math.random() * 1000000),
        patientName: claim.patient?.fullName || 'Unknown',
        admissionDate: claim.medicalInfo?.admissionDate,
        dischargeDate: claim.medicalInfo?.dischargeDate,
        diagnosis: claim.medicalInfo?.diagnosis?.primary || 'Not specified',
        totalBill: claim.financialInfo?.totalAmount || 0
      },
      processedAt: new Date(),
      version: '1.0.0'
    };
    
    // Update claim with AI extraction results
    claim.aiExtraction = mockAiExtraction;
    await claim.save();
    
    res.json({
      success: true,
      message: 'AI extraction completed',
      data: { 
        aiExtraction: mockAiExtraction,
        claimId: claim.claimId
      }
    });
    
  } catch (error) {
    console.error('AI extraction error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error during AI extraction'
    });
  }
});

module.exports = router;