import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
    return (
        <nav className="landing-nav">
            <div className="nav-logo">
                <Link to="/">MediMate 🩺</Link> {/* Use Link for the logo too */}
            </div>
            <div className="nav-actions">
                <Link to="/login">
                    <button className="btn-login">Login</button>
                </Link>
                <Link to="/signup">
                    <button className="btn-signup">Sign Up</button>
                </Link>
            </div>
        </nav>
    );
}

// Small CSS change for logo link
// In LandingPage.css, update .nav-logo a to also apply to Link
// .nav-logo a, .nav-logo > Link { ... } - but React handles this fine.

export default Navbar;