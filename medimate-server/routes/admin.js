const express = require('express');
const User = require('../models/User');
const Claim = require('../models/Claim');
const Consent = require('../models/Consent');
const { authorize } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/admin/dashboard
// @desc    Get admin dashboard data
// @access  Private (Admin only)
router.get('/dashboard', authorize('admin'), async (req, res) => {
  try {
    // System statistics
    const systemStats = {
      totalPatients: await User.countDocuments({ role: 'patient' }),
      totalHospitals: await User.countDocuments({ role: 'hospital' }),
      totalInsurers: await User.countDocuments({ role: 'insurer' }),
      activeClaims: await Claim.countDocuments({ status: { $in: ['submitted', 'under_review'] } }),
      approvedClaims: await Claim.countDocuments({ status: 'approved' }),
      rejectedClaims: await Claim.countDocuments({ status: 'rejected' })
    };
    
    // AI performance metrics
    const aiMetrics = await Claim.aggregate([
      { $match: { 'aiExtraction.confidence': { $exists: true } } },
      {
        $group: {
          _id: null,
          avgConfidence: { $avg: '$aiExtraction.confidence' },
          totalProcessed: { $sum: 1 },
          highConfidence: {
            $sum: { $cond: [{ $gte: ['$aiExtraction.confidence', 90] }, 1, 0] }
          }
        }
      }
    ]);
    
    const aiPerformance = {
      accuracy: aiMetrics[0]?.avgConfidence || 0,
      totalProcessed: aiMetrics[0]?.totalProcessed || 0,
      highConfidenceRate: aiMetrics[0] ? 
        (aiMetrics[0].highConfidence / aiMetrics[0].totalProcessed * 100) : 0
    };
    
    // Recent blockchain transactions (mock data)
    const blockchainLogs = await Consent.find({
      'blockchain.transactionHash': { $exists: true }
    })
    .populate('patient', 'fullName')
    .populate('entity', 'hospitalData.hospitalName insurerData.companyName')
    .sort({ createdAt: -1 })
    .limit(10);
    
    // Recent system activity
    const recentActivity = await Claim.find({})
    .populate('patient', 'fullName')
    .populate('timeline.updatedBy', 'fullName role')
    .sort({ 'timeline.timestamp': -1 })
    .limit(10)
    .then(claims => {
      const activities = [];
      claims.forEach(claim => {
        claim.timeline.forEach(entry => {
          activities.push({
            action: `Claim ${entry.status}`,
            user: entry.updatedBy?.fullName || 'System',
            userRole: entry.updatedBy?.role || 'system',
            timestamp: entry.timestamp,
            claimId: claim.claimId
          });
        });
      });
      return activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 10);
    });
    
    res.json({
      success: true,
      data: {
        systemStats,
        aiPerformance,
        blockchainLogs,
        recentActivity
      }
    });
    
  } catch (error) {
    console.error('Admin dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching dashboard data'
    });
  }
});

// @route   GET /api/admin/users
// @desc    Get all users with pagination
// @access  Private (Admin only)
router.get('/users', authorize('admin'), async (req, res) => {
  try {
    const { role, search, page = 1, limit = 20 } = req.query;
    
    // Build query
    const query = {};
    if (role) query.role = role;
    
    if (search) {
      query.$or = [
        { fullName: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } }
      ];
    }
    
    const users = await User.find(query)
      .select('-password')
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit);
    
    const total = await User.countDocuments(query);
    
    res.json({
      success: true,
      data: {
        users,
        pagination: {
          current: parseInt(page),
          pages: Math.ceil(total / limit),
          total
        }
      }
    });
    
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching users'
    });
  }
});

// @route   GET /api/admin/claims
// @desc    Get all claims with advanced filtering
// @access  Private (Admin only)
router.get('/claims', authorize('admin'), async (req, res) => {
  try {
    const { status, hospital, insurer, dateFrom, dateTo, page = 1, limit = 20 } = req.query;
    
    // Build query
    const query = {};
    if (status) query.status = status;
    if (hospital) query.hospital = hospital;
    if (insurer) query.insurer = insurer;
    
    if (dateFrom || dateTo) {
      query.createdAt = {};
      if (dateFrom) query.createdAt.$gte = new Date(dateFrom);
      if (dateTo) query.createdAt.$lte = new Date(dateTo);
    }
    
    const claims = await Claim.find(query)
      .populate('patient', 'fullName email')
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
          current: parseInt(page),
          pages: Math.ceil(total / limit),
          total
        }
      }
    });
    
  } catch (error) {
    console.error('Get admin claims error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching claims'
    });
  }
});

// @route   GET /api/admin/analytics
// @desc    Get system analytics
// @access  Private (Admin only)
router.get('/analytics', authorize('admin'), async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    // Calculate date range
    const now = new Date();
    let startDate;
    
    switch (period) {
      case '7d':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '90d':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      default:
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }
    
    // Claims analytics
    const claimsAnalytics = await Claim.aggregate([
      { $match: { createdAt: { $gte: startDate } } },
      {
        $group: {
          _id: {
            date: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
            status: '$status'
          },
          count: { $sum: 1 },
          totalAmount: { $sum: '$financialInfo.claimedAmount' }
        }
      },
      { $sort: { '_id.date': 1 } }
    ]);
    
    // User registration analytics
    const userAnalytics = await User.aggregate([
      { $match: { createdAt: { $gte: startDate } } },
      {
        $group: {
          _id: {
            date: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
            role: '$role'
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.date': 1 } }
    ]);
    
    // Processing time analytics
    const processingTimeAnalytics = await Claim.aggregate([
      { $match: { status: 'approved', createdAt: { $gte: startDate } } },
      {
        $project: {
          processingTime: {
            $subtract: [
              { $arrayElemAt: ['$timeline.timestamp', -1] },
              { $arrayElemAt: ['$timeline.timestamp', 0] }
            ]
          }
        }
      },
      {
        $group: {
          _id: null,
          avgProcessingTime: { $avg: '$processingTime' },
          minProcessingTime: { $min: '$processingTime' },
          maxProcessingTime: { $max: '$processingTime' }
        }
      }
    ]);
    
    res.json({
      success: true,
      data: {
        period,
        claimsAnalytics,
        userAnalytics,
        processingTimeAnalytics: processingTimeAnalytics[0] || {}
      }
    });
    
  } catch (error) {
    console.error('Analytics error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error fetching analytics'
    });
  }
});

// @route   PUT /api/admin/users/:userId/status
// @desc    Update user status (activate/deactivate)
// @access  Private (Admin only)
router.put('/users/:userId/status', authorize('admin'), async (req, res) => {
  try {
    const { isActive } = req.body;
    
    const user = await User.findByIdAndUpdate(
      req.params.userId,
      { isActive },
      { new: true }
    ).select('-password');
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    res.json({
      success: true,
      message: `User ${isActive ? 'activated' : 'deactivated'} successfully`,
      data: { user }
    });
    
  } catch (error) {
    console.error('Update user status error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error updating user status'
    });
  }
});

// @route   DELETE /api/admin/claims/:claimId
// @desc    Delete claim (admin only)
// @access  Private (Admin only)
router.delete('/claims/:claimId', authorize('admin'), async (req, res) => {
  try {
    const claim = await Claim.findOneAndDelete({ claimId: req.params.claimId });
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Claim not found'
      });
    }
    
    res.json({
      success: true,
      message: 'Claim deleted successfully'
    });
    
  } catch (error) {
    console.error('Delete claim error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error deleting claim'
    });
  }
});

module.exports = router;