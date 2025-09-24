import React from 'react';

const Hero = () => {
    const title = "AI-Powered X-Ray Analysis";
    return (
        <section id="hero" className="hero">
            <h1 className="hero-title">
                {title.split("").map((letter, index) =>
                    <span key={index} className="letter" style={{ animationDelay: `${index * 0.05}s` }}>
                        {letter === " " ? "\u00A0" : letter}
                    </span>
                )}
            </h1>
            <p className="hero-tagline">Instant, Accurate, and Transparent Thoracic Pathology Detection.</p>
            <a href="#upload" className="cta-button pulse">Upload X-Ray</a>
        </section>
    );
};
export default Hero;