# MediMate - Healthcare Insurance Platform

A comprehensive healthcare insurance platform built with React that streamlines the insurance claim process through AI-powered document extraction and blockchain-based consent management.

## 🏥 Platform Overview

MediMate connects four key stakeholders in the healthcare insurance ecosystem:

- **👤 Patients** - Upload documents, manage consent, track claims
- **🏢 Insurers** - Review claims with AI assistance, approve/reject claims
- **🏥 Hospitals** - Upload patient records, manage medical documentation
- **⚙️ Admins** - Monitor system performance, view blockchain logs

## ✨ Key Features

### 🔹 Patient Module
- **Document Upload**: Support for 8 document types (Insurance Policy, ID Proof, Medical Records, etc.)
- **Consent Management**: Blockchain-based consent with grant/revoke capabilities
- **Claim Tracking**: Real-time claim status with interactive timeline
- **Dashboard**: Personalized overview with claim status and quick actions

### 🔹 Insurer Module
- **AI-Powered Extraction**: Automatic field extraction with 92% confidence
- **Claim Review**: Comprehensive claim analysis with document viewer
- **Dashboard**: Claims overview with search, filter, and statistics
- **Decision Making**: Approve, reject, or request additional information

### 🔹 Hospital Module
- **Patient Management**: Track patients with consent status
- **Record Upload**: Secure medical record upload with consent verification
- **Dashboard**: Hospital statistics and patient overview
- **Consent Integration**: Upload restrictions based on patient consent

### 🔹 Admin Module
- **System Analytics**: Platform-wide statistics (200+ patients, 15 hospitals, 8 insurers)
- **Blockchain Logs**: Transaction history with cryptographic verification
- **AI Performance**: Model accuracy tracking (91% on last 50 claims)
- **Activity Monitoring**: Real-time system activity feed

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Prakriti2603/medimate.git
   cd medimate
   ```

2. **Navigate to the UI directory**
   ```bash
   cd medimate-ui
   ```

3. **Install dependencies**
   ```bash
   npm install
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

5. **Open your browser**
   - Visit `http://localhost:3000`
   - Go to `/modules` to access the module selector

## 🎯 Navigation

### Module Access Points
- **Module Selector**: `http://localhost:3000/modules`
- **Patient Portal**: `http://localhost:3000/patient/dashboard`
- **Insurer Portal**: `http://localhost:3000/insurer/dashboard`
- **Hospital Portal**: `http://localhost:3000/hospital/dashboard`
- **Admin Dashboard**: `http://localhost:3000/admin/dashboard`

## 🏗️ Project Structure

```
medimate/
├── medimate-ui/                 # React frontend application
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   │   └── ModuleSelector/  # Module selection interface
│   │   ├── pages/
│   │   │   ├── patient/         # Patient module pages
│   │   │   ├── insurer/         # Insurer module pages
│   │   │   ├── hospital/        # Hospital module pages
│   │   │   └── admin/           # Admin module pages
│   │   └── App.jsx              # Main application component
│   ├── public/                  # Static assets
│   └── package.json             # Dependencies and scripts
├── medimate-server/             # Backend server (future implementation)
└── docs/                        # Documentation
```

## 🎨 Design System

### Color Themes
- **Patient Module**: Blue gradient (#667eea to #764ba2)
- **Insurer Module**: Dark blue gradient (#2c5aa0 to #1e3a8a)
- **Hospital Module**: Green gradient (#16a085 to #2ecc71)
- **Admin Module**: Purple-blue gradient (#8e44ad to #3498db)

### Key Design Principles
- **Responsive Design**: Mobile-first approach with flexible layouts
- **Accessibility**: Proper contrast ratios and semantic HTML
- **User Experience**: Intuitive navigation and progressive disclosure
- **Visual Hierarchy**: Clear typography and consistent spacing

## 🔧 Technology Stack

### Frontend
- **React 18.3.1** - Modern React with hooks and functional components
- **React Router DOM 6.25.1** - Client-side routing
- **CSS Grid & Flexbox** - Responsive layouts
- **CSS Custom Properties** - Consistent theming

### Future Backend Integration
- Node.js/Express server
- Database integration (MongoDB/PostgreSQL)
- Blockchain integration for consent management
- AI/ML services for document extraction

## 📱 Features by Module

### Patient Module (4 Pages)
1. **Dashboard** - Overview and quick actions
2. **Upload Documents** - Multi-file upload with progress tracking
3. **Consent Management** - Blockchain-based permissions
4. **Claim Tracking** - Status monitoring with timeline

### Insurer Module (2 Pages)
1. **Dashboard** - Claims overview with statistics
2. **Claim Review** - AI-assisted claim processing

### Hospital Module (2 Pages)
1. **Dashboard** - Patient management overview
2. **Upload Records** - Medical record submission

### Admin Module (1 Page)
1. **Dashboard** - System monitoring and analytics

## 🤝 Contributing

We welcome contributions from the team! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
5. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request**

### Development Guidelines
- Follow React best practices and hooks patterns
- Maintain consistent code formatting
- Add comments for complex logic
- Test your changes across all modules
- Ensure responsive design works on mobile devices

## 📋 Available Scripts

In the `medimate-ui` directory:

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (one-way operation)

## 🔮 Future Enhancements

- **Backend API Integration** - Connect to real backend services
- **Authentication System** - User login and role-based access
- **Real-time Notifications** - WebSocket-based updates
- **Advanced Analytics** - Detailed reporting and insights
- **Mobile App** - React Native implementation
- **Blockchain Integration** - Smart contracts for consent management
- **AI/ML Services** - Enhanced document processing
- **Multi-language Support** - Internationalization


**MediMate** - Transforming Healthcare Insurance Through Technology 🏥💙
