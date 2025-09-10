import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../AuthForm.css';

function SignupPage() {
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errors, setErrors] = useState({});
    const [successMessage, setSuccessMessage] = useState(''); // For success feedback

    const validateForm = () => {
        // ... (validation logic remains the same)
        const newErrors = {};
        if (!fullName) newErrors.fullName = 'Full name is required';
        if (!email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = 'Email address is invalid';
        }
        if (!phoneNumber) {
            newErrors.phoneNumber = 'Phone number is required';
        } else if (!/^\d{10}$/.test(phoneNumber)) {
            newErrors.phoneNumber = 'Phone number must be 10 digits';
        }
        if (!password) {
            newErrors.password = 'Password is required';
        } else {
            const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;
            if (!passwordRegex.test(password)) {
                newErrors.password = 'Password must be 8+ characters and include an uppercase letter, a lowercase letter, a number, and a symbol.';
            }
        }
        if (password !== confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // Demo version - no backend API call
    const handleSubmit = (event) => {
        event.preventDefault();
        setSuccessMessage('');
        if (validateForm()) {
            console.log('Demo signup successful:', { fullName, email, phoneNumber });
            setSuccessMessage('Account created successfully! This is a demo version.');

            // Clear form fields
            setFullName('');
            setEmail('');
            setPhoneNumber('');
            setPassword('');
            setConfirmPassword('');
            setErrors({});
        } else {
            console.log('Form validation failed');
        }
    };

    return (
        <div className="auth-container">
            <form className="auth-form" onSubmit={handleSubmit} noValidate>
                <h2>Create Your Account</h2>
                {/* Display general form errors or success messages */}
                {errors.form && <p className="error-text">{errors.form}</p>}
                {successMessage && <p className="success-text">{successMessage}</p>}

                {/* ... (all input fields remain the same) ... */}
                <div className="input-group">
                    <label htmlFor="fullName">Full Name</label>
                    <input type="text" id="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
                    {errors.fullName && <p className="error-text">{errors.fullName}</p>}
                </div>
                <div className="input-group">
                    <label htmlFor="email">Email</label>
                    <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                    {errors.email && <p className="error-text">{errors.email}</p>}
                </div>
                <div className="input-group">
                    <label htmlFor="phoneNumber">Phone Number</label>
                    <input type="tel" id="phoneNumber" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} required />
                    {errors.phoneNumber && <p className="error-text">{errors.phoneNumber}</p>}
                </div>
                <div className="input-group">
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                    {errors.password && <p className="error-text">{errors.password}</p>}
                </div>
                <div className="input-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input type="password" id="confirmPassword" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
                    {errors.confirmPassword && <p className="error-text">{errors.confirmPassword}</p>}
                </div>
                <button type="submit" className="btn-auth">Create Account</button>
                <p className="auth-switch">
                    Already have an account? <Link to="/login">Log In</Link>
                </p>
            </form>
        </div>
    );
}

export default SignupPage;