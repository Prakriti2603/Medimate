import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../AuthForm.css';

function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState({});
    const { login, isLoading } = useAuth();
    const navigate = useNavigate();

    // --- Validation Function ---
    const validateForm = () => {
        const newErrors = {};
        // Email validation
        if (!email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = 'Email address is invalid';
        }
        // Password validation
        if (!password) {
            newErrors.password = 'Password is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        
        // Validate the form before submitting
        if (!validateForm()) {
            return;
        }

        try {
            const result = await login({ email, password });
            
            if (result.success) {
                // Clear form
                setEmail('');
                setPassword('');
                setErrors({});
                
                // Navigate based on user role
                const userRole = result.user.role;
                switch (userRole) {
                    case 'patient':
                        navigate('/patient/dashboard');
                        break;
                    case 'insurer':
                        navigate('/insurer/dashboard');
                        break;
                    case 'hospital':
                        navigate('/hospital/dashboard');
                        break;
                    case 'admin':
                        navigate('/admin/dashboard');
                        break;
                    default:
                        navigate('/');
                }
            } else {
                // Error is handled by AuthContext (toast notification)
                setErrors({ general: result.error });
            }
        } catch (error) {
            console.error('Login error:', error);
            setErrors({ general: 'An unexpected error occurred. Please try again.' });
        }
    };

    return (
        <div className="auth-container">
            <form className="auth-form" onSubmit={handleSubmit} noValidate> {/* noValidate disables default browser validation */}
                <h2>Welcome Back!</h2>
                <p>Log in to access your MediMate account.</p>

                {/* General error message */}
                {errors.general && <div className="error-text" style={{ marginBottom: '1rem', textAlign: 'center' }}>{errors.general}</div>}

                <div className="input-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={isLoading}
                        required
                    />
                    {errors.email && <p className="error-text">{errors.email}</p>}
                </div>

                <div className="input-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={isLoading}
                        required
                    />
                    {errors.password && <p className="error-text">{errors.password}</p>}
                </div>

                <button type="submit" className="btn-auth" disabled={isLoading}>
                    {isLoading ? 'Logging in...' : 'Login'}
                </button>
                <p className="auth-switch">
                    Don't have an account? <Link to="/signup">Sign Up</Link>
                </p>
            </form>
        </div>
    );
}

export default LoginPage;