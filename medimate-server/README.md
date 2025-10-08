# MediMate Backend Server

Real-time healthcare insurance platform backend with AI-powered document processing and blockchain integration.

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- MongoDB (local or cloud)
- npm or yarn

### Installation

1. **Navigate to server directory**
   ```bash
   cd medimate-server
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the server**
   ```bash
   # Development mode with auto-reload
   npm run dev
   
   # Production mode
   npm start
   ```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update profile
- `POST /api/auth/logout` - Logout

### Patient Routes
- `GET /api/patient/dashboard` - Patient dashboard data
- `GET /api/patient/claims` - Get patient claims
- `POST /api/patient/claims` - Create new claim
- `GET /api/patient/consents` - Get patient consents
- `POST /api/patient/consents` - Grant consent

### Insurer Routes
- `GET /api/insurer/dashboard` - Insurer dashboard
- `GET /api/insurer/claims` - Get claims for review
- `PUT /api/insurer/claims/:id/review` - Approve/reject claim
- `POST /api/insurer/claims/:id/ai-extract` - AI document extraction

### Hospital Routes
- `GET /api/hospital/dashboard` - Hospital dashboard
- `GET /api/hospital/patients` - Get patients with consent
- `POST /api/hospital/claims` - Create claim for patient
- `GET /api/hospital/consents` - Get patient consents

### Admin Routes
- `GET /api/admin/dashboard` - System overview
- `GET /api/admin/users` - Manage users
- `GET /api/admin/claims` - All claims management
- `GET /api/admin/analytics` - System analytics

### File Upload
- `POST /api/upload/document` - Upload single document
- `POST /api/upload/multiple` - Upload multiple documents
- `GET /api/upload/document/:filename` - Get uploaded file
- `DELETE /api/upload/document/:id` - Delete document

## 🔐 Authentication

All protected routes require JWT token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## 📊 Real-time Features

### Socket.IO Events

**Client → Server:**
- `join-room` - Join user-specific room
- `claim-update` - Claim status update
- `document-uploaded` - Document upload notification
- `consent-changed` - Consent status change

**Server → Client:**
- `claim-status-changed` - Real-time claim updates
- `new-document` - New document uploaded
- `consent-updated` - Consent status changed
- `new-claim-submitted` - New claim notification

## 🗄️ Database Models

### User Model
```javascript
{
  fullName: String,
  email: String (unique),
  phoneNumber: String,
  password: String (hashed),
  role: ['patient', 'insurer', 'hospital', 'admin'],
  isActive: Boolean,
  // Role-specific data
  patientData: { ... },
  hospitalData: { ... },
  insurerData: { ... }
}
```

### Claim Model
```javascript
{
  claimId: String (auto-generated),
  patient: ObjectId,
  hospital: ObjectId,
  insurer: ObjectId,
  medicalInfo: { ... },
  financialInfo: { ... },
  documents: [{ ... }],
  aiExtraction: { ... },
  status: ['draft', 'submitted', 'under_review', 'approved', 'rejected'],
  timeline: [{ ... }],
  consent: { ... }
}
```

### Consent Model
```javascript
{
  patient: ObjectId,
  entity: ObjectId,
  entityType: ['hospital', 'insurer'],
  status: ['granted', 'revoked', 'expired'],
  permissions: { ... },
  blockchain: { ... },
  auditTrail: [{ ... }]
}
```

## 📁 File Upload

### Supported Formats
- PDF documents
- JPEG/JPG images
- PNG images

### Size Limits
- Maximum: 10MB per file
- Automatic image compression
- Secure file storage

### File Structure
```
uploads/
├── [userId]/
│   ├── document-123456789.pdf
│   └── image-987654321.jpg
```

## 🔒 Security Features

- **JWT Authentication** with secure tokens
- **Password Hashing** using bcrypt
- **Rate Limiting** to prevent abuse
- **CORS Protection** for cross-origin requests
- **Helmet.js** for security headers
- **File Validation** for uploads
- **Role-based Authorization**

## 🚀 Performance Features

- **Compression** middleware for responses
- **MongoDB Indexing** for fast queries
- **Image Optimization** with Sharp
- **Pagination** for large datasets
- **Caching** strategies

## 🔧 Environment Variables

```env
# Server
PORT=5000
NODE_ENV=development

# Database
MONGODB_URI=mongodb://localhost:27017/medimate

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRE=7d

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_PATH=./uploads

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100

# CORS
FRONTEND_URL=http://localhost:3000
```

## 📈 Monitoring & Logging

- **Morgan** for HTTP request logging
- **Error Handling** middleware
- **Health Check** endpoint at `/api/health`
- **Performance Metrics** tracking

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production
```bash
npm start
```

### Docker (Optional)
```bash
docker build -t medimate-server .
docker run -p 5000:5000 medimate-server
```

## 📞 Support

For issues and questions:
- Check the logs in console
- Verify environment variables
- Ensure MongoDB connection
- Check file permissions for uploads

## 🔄 API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": [ ... ]
}
```

---

**MediMate Backend** - Powering the future of healthcare insurance! 🏥💙