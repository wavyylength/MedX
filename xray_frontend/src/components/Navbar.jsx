import React, { useState, useEffect } from 'react';

const Navbar = () => {
    const [scrolled, setScrolled] = useState(false);
    
    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 50);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
            <a href="#hero" className="logo">CXR-Vision<span>AI</span></a>
            <ul className="nav-links">
                <li><a href="#upload">X-Ray Analyzer</a></li>
                <li><a href="#report-generator">Report Generator</a></li>
                {/* The "History" link has been removed */}
                <li><a href="#footer">About</a></li>
            </ul>
        </nav>
    );
};
export default Navbar;