const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const { createServer } = require('http');
const { Server } = require('socket.io');
require('dotenv').config();

// Import routes
const authRoutes = require('./routes/auth');
const patientRoutes = require('./routes/patient');
const insurerRoutes = require('./routes/insurer');
const hospitalRoutes = require('./routes/hospital');
const adminRoutes = require('./routes/admin');
const uploadRoutes = require('./routes/upload');

// Import middleware
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST", "PUT", "DELETE"]
  }
});

const PORT = process.env.PORT || 5000;

// Security middleware
app.use(helmet());
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: (process.env.RATE_LIMIT_WINDOW || 15) * 60 * 1000,
  max: process.env.RATE_LIMIT_MAX || 100,
  message: 'Too many requests from this IP, please try again later.'
});
app.use(limiter);

// CORS configuration
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:3000",
  credentials: true
}));

// Body parsing middleware
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Logging
if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}

// Static files (for uploaded documents)
app.use('/uploads', express.static('uploads'));

// Database connection
const mongoURI = process.env.MONGODB_URI || 'mongodb+srv://prakritiranka05:MediMate2022@medimate.fhnzm9r.mongodb.net/?retryWrites=true&w=majority&appName=Medimate';
mongoose.connect(mongoURI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('✅ Connected to MongoDB'))
.catch(err => console.error('❌ MongoDB connection error:', err));

// Socket.IO for real-time updates
io.on('connection', (socket) => {
  console.log('👤 User connected:', socket.id);
  
  // Join user to their specific room
  socket.on('join-room', (userId) => {
    socket.join(userId);
    console.log(`User ${userId} joined room`);
  });
  
  // Handle claim status updates
  socket.on('claim-update', (data) => {
    io.to(data.userId).emit('claim-status-changed', data);
  });
  
  // Handle document upload notifications
  socket.on('document-uploaded', (data) => {
    io.to(data.insurerId).emit('new-document', data);
  });
  
  // Handle consent changes
  socket.on('consent-changed', (data) => {
    io.to(data.hospitalId).emit('consent-updated', data);
  });
  
  socket.on('disconnect', () => {
    console.log('👤 User disconnected:', socket.id);
  });
});

// Make io available to routes
app.set('io', io);

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/patient', authMiddleware, patientRoutes);
app.use('/api/insurer', authMiddleware, insurerRoutes);
app.use('/api/hospital', authMiddleware, hospitalRoutes);
app.use('/api/admin', authMiddleware, adminRoutes);
app.use('/api/upload', authMiddleware, uploadRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: '🏥 MediMate Server is running!',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      patient: '/api/patient',
      insurer: '/api/insurer',
      hospital: '/api/hospital',
      admin: '/api/admin',
      upload: '/api/upload',
      health: '/api/health'
    }
  });
});

// Error handling middleware
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    message: `Cannot ${req.method} ${req.originalUrl}`
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 MediMate Server running on port ${PORT}`);
  console.log(`📱 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
  console.log(`🔗 API Base URL: http://localhost:${PORT}/api`);
});