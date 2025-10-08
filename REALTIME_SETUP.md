# 🚀 MediMate Real-Time Setup Guide

Complete guide to set up the full-stack MediMate platform with real-time features.

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **MongoDB** (local or cloud)
- **Git** for version control

## 🔧 Step 1: Backend Setup

### 1. Navigate to server directory
```bash
cd "MediMate 1st/medimate-server"
```

### 2. Install backend dependencies
```bash
npm install
```

### 3. Start the backend server
```bash
# Development mode with auto-reload
npm run dev

# OR Production mode
npm start
```

**Expected Output:**
```
✅ Connected to MongoDB
🚀 MediMate Server running on port 5000
📱 Frontend URL: http://localhost:3000
🔗 API Base URL: http://localhost:5000/api
```

## 🎨 Step 2: Frontend Setup

### 1. Open a new terminal and navigate to UI directory
```bash
cd "MediMate 1st/medimate-ui"
```

### 2. Install Socket.IO client for real-time features
```bash
npm install socket.io-client axios
```

### 3. Start the frontend application
```bash
npm start
```

## 🌐 Step 3: Access the Application

### Frontend URLs:
- **Main App**: http://localhost:3000
- **Module Selector**: http://localhost:3000/modules
- **Patient Portal**: http://localhost:3000/patient/dashboard
- **Insurer Portal**: http://localhost:3000/insurer/dashboard
- **Hospital Portal**: http://localhost:3000/hospital/dashboard
- **Admin Dashboard**: http://localhost:3000/admin/dashboard

### Backend URLs:
- **API Base**: http://localhost:5000/api
- **Health Check**: http://localhost:5000/api/health
- **Documentation**: http://localhost:5000

## 🔐 Step 4: Create Test Users

### Using API endpoints or MongoDB directly:

**Patient User:**
```json
{
  "fullName": "John Doe",
  "email": "patient@medimate.com",
  "phoneNumber": "1234567890",
  "password": "password123",
  "role": "patient"
}
```

**Insurer User:**
```json
{
  "fullName": "ABC Insurance Admin",
  "email": "insurer@medimate.com",
  "phoneNumber": "1234567891",
  "password": "password123",
  "role": "insurer"
}
```

**Hospital User:**
```json
{
  "fullName": "XYZ Hospital Admin",
  "email": "hospital@medimate.com",
  "phoneNumber": "1234567892",
  "password": "password123",
  "role": "hospital"
}
```

**Admin User:**
```json
{
  "fullName": "System Administrator",
  "email": "admin@medimate.com",
  "phoneNumber": "1234567893",
  "password": "password123",
  "role": "admin"
}
```

## ✨ Real-Time Features Available

### 🔄 Live Updates
- **Claim Status Changes** - Patients see real-time updates
- **Document Uploads** - Insurers notified instantly
- **Consent Changes** - Hospitals get immediate notifications
- **New Claims** - Real-time claim submissions

### 📡 Socket.IO Integration
- **Automatic reconnection** on network issues
- **Room-based messaging** for user-specific updates
- **Event-driven architecture** for scalability

### 🎯 Interactive Features
- **File Upload** with progress tracking
- **Real-time validation** and error handling
- **Live dashboards** with auto-refresh
- **Instant notifications** across modules

## 🧪 Step 5: Test Real-Time Features

### Test Scenario 1: Patient Upload → Insurer Notification
1. **Login as Patient** → Upload documents
2. **Login as Insurer** → See real-time notification
3. **Review claim** → Patient gets status update

### Test Scenario 2: Consent Management
1. **Login as Patient** → Grant consent to hospital
2. **Login as Hospital** → See patient in available list
3. **Upload records** → Real-time processing

### Test Scenario 3: Claim Processing
1. **Hospital** creates claim for patient
2. **Insurer** receives real-time notification
3. **AI extraction** processes documents
4. **Approval/Rejection** updates patient instantly

## 📊 Step 6: Monitor System

### Backend Monitoring:
- **Console logs** for real-time events
- **MongoDB** for data persistence
- **File uploads** in `/uploads` directory

### Frontend Monitoring:
- **Browser DevTools** for Socket.IO events
- **Network tab** for API calls
- **Console** for real-time updates

## 🔧 Troubleshooting

### Common Issues:

**1. MongoDB Connection Error**
```bash
# Check if MongoDB is running
# Update MONGODB_URI in .env file
```

**2. Port Already in Use**
```bash
# Kill process on port 5000
npx kill-port 5000

# Or change PORT in .env
```

**3. Socket.IO Connection Issues**
```bash
# Check CORS settings
# Verify frontend URL in backend config
```

**4. File Upload Errors**
```bash
# Check file permissions
# Verify upload directory exists
# Check file size limits
```

## 🚀 Production Deployment

### Environment Variables for Production:
```env
NODE_ENV=production
MONGODB_URI=your-production-mongodb-uri
JWT_SECRET=your-super-secure-secret
FRONTEND_URL=https://your-domain.com
```

### Build Commands:
```bash
# Backend
npm start

# Frontend
npm run build
```

## 📈 Performance Optimization

### Backend:
- **Database indexing** for faster queries
- **Image compression** for uploads
- **Rate limiting** for API protection
- **Caching** for frequent requests

### Frontend:
- **Code splitting** for faster loading
- **Image optimization** for better performance
- **Service workers** for offline capability

## 🔒 Security Features

- **JWT Authentication** with secure tokens
- **Password hashing** with bcrypt
- **File validation** and size limits
- **CORS protection** for API security
- **Rate limiting** to prevent abuse

## 📞 Support & Documentation

### API Documentation:
- **Postman Collection** available
- **Swagger/OpenAPI** integration ready
- **Real-time events** documented

### Getting Help:
1. Check console logs for errors
2. Verify environment variables
3. Test API endpoints individually
4. Monitor Socket.IO connections

---

## 🎉 Congratulations!

Your **MediMate Real-Time Platform** is now fully operational with:

✅ **Complete Backend API** with 25+ endpoints  
✅ **Real-time Socket.IO** integration  
✅ **File Upload System** with validation  
✅ **MongoDB Database** with proper models  
✅ **JWT Authentication** and authorization  
✅ **4 Complete Modules** (Patient, Insurer, Hospital, Admin)  
✅ **Professional Documentation** and setup guides  

**Your healthcare insurance platform is ready for production!** 🏥💙