const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Basic middleware
app.use(cors({
  origin: "http://localhost:3000",
  credentials: true
}));
app.use(express.json());

// Test route
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    message: 'Test server is running'
  });
});

// Simple auth routes for testing
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  // Simple test login
  if (email === 'test@example.com' && password === 'password') {
    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: {
          _id: '123',
          fullName: 'Test User',
          email: 'test@example.com',
          role: 'patient'
        },
        token: 'test-token-123'
      }
    });
  } else {
    res.status(401).json({
      success: false,
      message: 'Invalid credentials'
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Test Server running on port ${PORT}`);
});