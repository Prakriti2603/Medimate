import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Features from '../components/Features';
import Footer from '../components/Footer';
import '../LandingPage.css'; // We'll create this new CSS file

function LandingPage() {
    return (
        <div className="landing-page">
            <Navbar />
            <Hero />
            <Features />
            <Footer />
        </div>
    );
}

export default LandingPage;