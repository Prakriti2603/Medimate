import React from 'react';

function Hero() {
    return (
        <section className="hero-section">
            <div className="hero-content">
                <h1 className="hero-headline">
                    Your Health Records, Secured.
                    <br />
                    Your Insurance Claims, Automated.
                </h1>
                <p className="hero-subheadline">
                    MediMate uses Blockchain and AI to give you control over your medical data and simplify insurance claims forever.
                </p>
                <div className="hero-cta">
                    <button className="btn-primary-solid">Get Started for Free</button>
                    <button className="btn-secondary-outline">Watch Demo</button>
                </div>
            </div>
        </section>
    );
}

export default Hero;