const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const sharp = require('sharp');
const Claim = require('../models/Claim');

const router = express.Router();

// Ensure upload directory exists
const uploadDir = 'uploads';
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const userDir = path.join(uploadDir, req.user._id.toString());
    if (!fs.existsSync(userDir)) {
      fs.mkdirSync(userDir, { recursive: true });
    }
    cb(null, userDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

// File filter
const fileFilter = (req, file, cb) => {
  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
  
  if (allowedTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error('Invalid file type. Only PDF, JPEG, JPG, and PNG files are allowed.'), false);
  }
};

// Configure multer
const upload = multer({
  storage: storage,
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB default
  },
  fileFilter: fileFilter
});

// @route   POST /api/upload/document
// @desc    Upload document for claim
// @access  Private
router.post('/document', upload.single('document'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No file uploaded'
      });
    }
    
    const { claimId, documentType } = req.body;
    
    if (!claimId || !documentType) {
      return res.status(400).json({
        success: false,
        message: 'Claim ID and document type are required'
      });
    }
    
    // Find the claim
    const claim = await Claim.findOne({ claimId });
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Claim not found'
      });
    }
    
    // Check if user has permission to upload to this claim
    const canUpload = claim.patient.toString() === req.user._id.toString() ||
                     claim.hospital.toString() === req.user._id.toString() ||
                     req.user.role === 'admin';
    
    if (!canUpload) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to upload documents for this claim'
      });
    }
    
    // Process image files (compress if needed)
    let processedPath = req.file.path;
    if (req.file.mimetype.startsWith('image/')) {
      try {
        const compressedPath = req.file.path.replace(path.extname(req.file.path), '_compressed' + path.extname(req.file.path));
        await sharp(req.file.path)
          .resize(2000, 2000, { fit: 'inside', withoutEnlargement: true })
          .jpeg({ quality: 85 })
          .toFile(compressedPath);
        
        // Replace original with compressed version if it's smaller
        const originalStats = fs.statSync(req.file.path);
        const compressedStats = fs.statSync(compressedPath);
        
        if (compressedStats.size < originalStats.size) {
          fs.unlinkSync(req.file.path);
          fs.renameSync(compressedPath, req.file.path);
        } else {
          fs.unlinkSync(compressedPath);
        }
      } catch (compressionError) {
        console.log('Image compression failed, using original:', compressionError.message);
      }
    }
    
    // Create document object
    const documentData = {
      type: documentType,
      filename: req.file.filename,
      originalName: req.file.originalname,
      path: req.file.path,
      size: req.file.size,
      mimeType: req.file.mimetype,
      uploadedBy: req.user._id
    };
    
    // Add document to claim
    await claim.addDocument(documentData);
    
    // Emit real-time update
    const io = req.app.get('io');
    io.to(claim.insurer.toString()).emit('document-uploaded', {
      claimId: claim.claimId,
      documentType,
      uploadedBy: req.user.fullName,
      uploadedAt: new Date()
    });
    
    res.status(201).json({
      success: true,
      message: 'Document uploaded successfully',
      data: {
        document: documentData,
        claimId: claim.claimId
      }
    });
    
  } catch (error) {
    console.error('Upload error:', error);
    
    // Clean up uploaded file on error
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        message: 'File too large. Maximum size is 10MB.'
      });
    }
    
    res.status(500).json({
      success: false,
      message: error.message || 'Server error during file upload'
    });
  }
});

// @route   POST /api/upload/multiple
// @desc    Upload multiple documents
// @access  Private
router.post('/multiple', upload.array('documents', 10), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No files uploaded'
      });
    }
    
    const { claimId } = req.body;
    const documentTypes = JSON.parse(req.body.documentTypes || '[]');
    
    if (!claimId) {
      return res.status(400).json({
        success: false,
        message: 'Claim ID is required'
      });
    }
    
    // Find the claim
    const claim = await Claim.findOne({ claimId });
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Claim not found'
      });
    }
    
    // Check permissions
    const canUpload = claim.patient.toString() === req.user._id.toString() ||
                     claim.hospital.toString() === req.user._id.toString() ||
                     req.user.role === 'admin';
    
    if (!canUpload) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to upload documents for this claim'
      });
    }
    
    const uploadedDocuments = [];
    
    // Process each file
    for (let i = 0; i < req.files.length; i++) {
      const file = req.files[i];
      const documentType = documentTypes[i] || 'other';
      
      // Process image compression if needed
      if (file.mimetype.startsWith('image/')) {
        try {
          const compressedPath = file.path.replace(path.extname(file.path), '_compressed' + path.extname(file.path));
          await sharp(file.path)
            .resize(2000, 2000, { fit: 'inside', withoutEnlargement: true })
            .jpeg({ quality: 85 })
            .toFile(compressedPath);
          
          const originalStats = fs.statSync(file.path);
          const compressedStats = fs.statSync(compressedPath);
          
          if (compressedStats.size < originalStats.size) {
            fs.unlinkSync(file.path);
            fs.renameSync(compressedPath, file.path);
            file.size = compressedStats.size;
          } else {
            fs.unlinkSync(compressedPath);
          }
        } catch (compressionError) {
          console.log('Image compression failed for file', file.originalname);
        }
      }
      
      const documentData = {
        type: documentType,
        filename: file.filename,
        originalName: file.originalname,
        path: file.path,
        size: file.size,
        mimeType: file.mimetype,
        uploadedBy: req.user._id
      };
      
      uploadedDocuments.push(documentData);
      await claim.addDocument(documentData);
    }
    
    // Emit real-time update
    const io = req.app.get('io');
    io.to(claim.insurer.toString()).emit('multiple-documents-uploaded', {
      claimId: claim.claimId,
      documentCount: uploadedDocuments.length,
      uploadedBy: req.user.fullName,
      uploadedAt: new Date()
    });
    
    res.status(201).json({
      success: true,
      message: `${uploadedDocuments.length} documents uploaded successfully`,
      data: {
        documents: uploadedDocuments,
        claimId: claim.claimId
      }
    });
    
  } catch (error) {
    console.error('Multiple upload error:', error);
    
    // Clean up uploaded files on error
    if (req.files) {
      req.files.forEach(file => {
        if (fs.existsSync(file.path)) {
          fs.unlinkSync(file.path);
        }
      });
    }
    
    res.status(500).json({
      success: false,
      message: error.message || 'Server error during file upload'
    });
  }
});

// @route   GET /api/upload/document/:filename
// @desc    Get uploaded document
// @access  Private
router.get('/document/:filename', async (req, res) => {
  try {
    const filename = req.params.filename;
    const filePath = path.join(uploadDir, req.user._id.toString(), filename);
    
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({
        success: false,
        message: 'File not found'
      });
    }
    
    // Set appropriate headers
    const ext = path.extname(filename).toLowerCase();
    let contentType = 'application/octet-stream';
    
    switch (ext) {
      case '.pdf':
        contentType = 'application/pdf';
        break;
      case '.jpg':
      case '.jpeg':
        contentType = 'image/jpeg';
        break;
      case '.png':
        contentType = 'image/png';
        break;
    }
    
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `inline; filename="${filename}"`);
    
    // Stream the file
    const fileStream = fs.createReadStream(filePath);
    fileStream.pipe(res);
    
  } catch (error) {
    console.error('File retrieval error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error retrieving file'
    });
  }
});

// @route   DELETE /api/upload/document/:documentId
// @desc    Delete uploaded document
// @access  Private
router.delete('/document/:documentId', async (req, res) => {
  try {
    const documentId = req.params.documentId;
    
    // Find claim with this document
    const claim = await Claim.findOne({
      'documents._id': documentId
    });
    
    if (!claim) {
      return res.status(404).json({
        success: false,
        message: 'Document not found'
      });
    }
    
    // Check permissions
    const canDelete = claim.patient.toString() === req.user._id.toString() ||
                     claim.hospital.toString() === req.user._id.toString() ||
                     req.user.role === 'admin';
    
    if (!canDelete) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to delete this document'
      });
    }
    
    // Find the document
    const document = claim.documents.id(documentId);
    
    if (!document) {
      return res.status(404).json({
        success: false,
        message: 'Document not found'
      });
    }
    
    // Delete file from filesystem
    if (fs.existsSync(document.path)) {
      fs.unlinkSync(document.path);
    }
    
    // Remove document from claim
    claim.documents.pull(documentId);
    await claim.save();
    
    res.json({
      success: true,
      message: 'Document deleted successfully'
    });
    
  } catch (error) {
    console.error('Delete document error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error deleting document'
    });
  }
});

module.exports = router;