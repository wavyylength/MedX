import React, { useState } from 'react';

const Login = ({ onLoginSuccess }) => {
  const [isLoginView, setIsLoginView] = useState(true);

  // State for form inputs
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleFormSubmit = (e) => {
    e.preventDefault();
    setError('');

    // Simple Form Validation
    if (!email || !password || (!isLoginView && !username)) {
      setError('Please fill in all required fields.');
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
        setError('Please enter a valid email address.');
        return;
    }

    // --- Simulate Authentication ---
    // In a real app, you would make an API call to your backend here.
    console.log('Authentication successful for:', email);
    onLoginSuccess(); // This function tells the parent App component to grant access.
  };

  return (
    <div className="login-container">
      <div className={`login-card ${isLoginView ? '' : 'signup-view'}`}>
        <div className="login-logo">
          CXR-Vision<span>AI</span>
        </div>

        <div className="form-toggle">
          <button 
            className={isLoginView ? 'active' : ''} 
            onClick={() => setIsLoginView(true)}
          >
            Login
          </button>
          <button 
            className={!isLoginView ? 'active' : ''} 
            onClick={() => setIsLoginView(false)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleFormSubmit} className="login-form">
          <h2>{isLoginView ? 'Welcome Back' : 'Create Account'}</h2>
          
          {!isLoginView && (
            <div className="input-group">
              <i className="fas fa-user"></i>
              <input 
                type="text" 
                placeholder="Username" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required 
              />
            </div>
          )}

          <div className="input-group">
            <i className="fas fa-envelope"></i>
            <input 
              type="email" 
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)} 
              required 
            />
          </div>

          <div className="input-group">
            <i className="fas fa-lock"></i>
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          {error && <p className="error-message">{error}</p>}

          <button type="submit" className="cta-button form-submit-btn">
            {isLoginView ? 'Login' : 'Sign Up'}
          </button>

          <p className="form-footer-text">
            {isLoginView ? "Don't have an account?" : "Already have an account?"}
            <span onClick={() => setIsLoginView(!isLoginView)}>
              {isLoginView ? ' Sign Up' : ' Login'}
            </span>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;