# Contributing to MediMate

Thank you for your interest in contributing to MediMate! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Git
- Code editor (VS Code recommended)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Prakriti2603/medimate.git
   cd medimate
   ```

2. **Install dependencies**
   ```bash
   cd medimate-ui
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## 🔄 Development Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/feature-name` - Individual feature branches
- `bugfix/bug-description` - Bug fix branches
- `hotfix/critical-fix` - Critical production fixes

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Test your changes thoroughly
   - Update documentation if needed

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### React Components
- Use functional components with hooks
- Follow PascalCase for component names
- Use descriptive prop names
- Add PropTypes for type checking (future enhancement)

### CSS Guidelines
- Use CSS modules or styled-components
- Follow BEM naming convention for classes
- Maintain responsive design principles
- Use CSS custom properties for theming

### File Structure
```
src/
├── components/          # Reusable components
├── pages/              # Page components
│   ├── patient/        # Patient module
│   ├── insurer/        # Insurer module
│   ├── hospital/       # Hospital module
│   └── admin/          # Admin module
├── styles/             # Global styles
└── utils/              # Utility functions
```

### Naming Conventions
- **Components**: PascalCase (`PatientDashboard.jsx`)
- **Files**: PascalCase for components, camelCase for utilities
- **CSS Classes**: kebab-case (`patient-dashboard`)
- **Variables**: camelCase (`patientData`)
- **Constants**: UPPER_SNAKE_CASE (`API_ENDPOINTS`)

## 🧪 Testing Guidelines

### Testing Strategy
- Unit tests for utility functions
- Component tests for React components
- Integration tests for user workflows
- E2E tests for critical paths

### Running Tests
```bash
npm test                 # Run all tests
npm test -- --watch     # Run tests in watch mode
npm test -- --coverage  # Run tests with coverage
```

## 📋 Code Review Process

### Before Submitting PR
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No console.log statements
- [ ] Responsive design tested
- [ ] Cross-browser compatibility checked

### PR Requirements
- Clear title and description
- Link to related issues
- Screenshots for UI changes
- Test coverage maintained
- No merge conflicts

## 🐛 Bug Reports

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- Browser: [e.g., Chrome 91]
- OS: [e.g., Windows 10]
- Node version: [e.g., 18.0.0]
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternative Solutions**
Other ways to solve this problem.

**Additional Context**
Screenshots, mockups, or examples.
```

## 🏗️ Module Development

### Adding New Pages
1. Create component in appropriate module folder
2. Add corresponding CSS file
3. Update routing in `App.jsx`
4. Add navigation links where appropriate
5. Update documentation

### Module Structure
Each module should follow this pattern:
```
pages/module-name/
├── ModuleDashboard.jsx
├── ModuleDashboard.css
├── FeaturePage.jsx
├── FeaturePage.css
└── index.js (if needed)
```

## 🎨 Design Guidelines

### Color Palette
- Patient: `#667eea` to `#764ba2`
- Insurer: `#2c5aa0` to `#1e3a8a`
- Hospital: `#16a085` to `#2ecc71`
- Admin: `#8e44ad` to `#3498db`

### Typography
- Headers: System fonts with fallbacks
- Body: Readable font sizes (16px minimum)
- Line height: 1.5 for body text

### Spacing
- Use consistent spacing scale (8px, 16px, 24px, 32px)
- Maintain proper whitespace
- Ensure touch-friendly button sizes (44px minimum)

## 📚 Documentation

### Code Documentation
- Add JSDoc comments for complex functions
- Include inline comments for business logic
- Update README for new features
- Maintain API documentation

### Component Documentation
```jsx
/**
 * PatientDashboard - Main dashboard for patient module
 * @param {Object} props - Component props
 * @param {string} props.patientName - Name of the patient
 * @param {Array} props.claims - List of patient claims
 */
const PatientDashboard = ({ patientName, claims }) => {
  // Component implementation
};
```

## 🚀 Deployment

### Build Process
```bash
npm run build           # Create production build
npm run build:analyze   # Analyze bundle size
```

### Environment Variables
- Use `.env` files for configuration
- Never commit sensitive data
- Document required environment variables

## 📞 Getting Help

### Communication Channels
- **GitHub Issues** - Bug reports and feature requests
- **Team Chat** - Daily communication
- **Code Reviews** - Technical discussions
- **Team Meetings** - Weekly sync-ups

### Resources
- [React Documentation](https://reactjs.org/docs)
- [React Router Documentation](https://reactrouter.com/)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Team meetings and presentations

Thank you for contributing to MediMate! 🏥💙