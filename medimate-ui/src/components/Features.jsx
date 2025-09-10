import React from 'react';

// You can replace emojis with actual icons (e.g., from an icon library)
const featuresData = [
    {
        icon: '⛓️',
        title: 'Blockchain Security',
        description: 'Your health records are stored in a tamper-proof, decentralized vault, ensuring data integrity and privacy.',
    },
    {
        icon: '🤖',
        title: 'AI-Powered Automation',
        description: 'Our AI engine reads your medical documents and auto-fills complex insurance claim forms in seconds, eliminating errors.',
    },
    {
        icon: '🙌',
        title: 'Complete Patient Control',
        description: 'You own your data. Grant or revoke access to doctors and insurers with a single click using our consent manager.',
    },
];

function Features() {
    return (
        <section id="features" className="features-section">
            <div className="features-container">
                <h2>A Smarter Way to Manage Healthcare</h2>
                <p className="features-intro">MediMate is designed to solve the biggest problems in health data management and insurance processing.</p>
                <div className="features-grid">
                    {featuresData.map((feature, index) => (
                        <div key={index} className="feature-card">
                            <div className="feature-icon">{feature.icon}</div>
                            <h3 className="feature-title">{feature.title}</h3>
                            <p className="feature-description">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

export default Features;