import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../AuthForm.css';

function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState({}); // New state for errors

    // --- New Validation Function ---
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
        // Return true if there are no errors, false otherwise
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        // Validate the form before submitting
        if (validateForm()) {
            console.log('Logging in with:', { email, password });
            alert('Form is valid! Login functionality to be connected to backend.');
            // Clear fields after successful validation (optional)
            setEmail('');
            setPassword('');
            setErrors({});
        } else {
            console.log('Form validation failed');
        }
    };

    return (
        <div className="auth-container">
            <form className="auth-form" onSubmit={handleSubmit} noValidate> {/* noValidate disables default browser validation */}
                <h2>Welcome Back!</h2>
                <p>Log in to access your MediMate account.</p>

                <div className="input-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    {/* Display error message if it exists */}
                    {errors.email && <p className="error-text">{errors.email}</p>}
                </div>

                <div className="input-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    {/* Display error message if it exists */}
                    {errors.password && <p className="error-text">{errors.password}</p>}
                </div>

                <button type="submit" className="btn-auth">Login</button>
                <p className="auth-switch">
                    Don't have an account? <Link to="/signup">Sign Up</Link>
                </p>
            </form>
        </div>
    );
}

export default LoginPage;