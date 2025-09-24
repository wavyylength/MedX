import React, { useState } from 'react';
import './App.css';

// Import all your components, including the new Login component
import Login from './components/Login.jsx';
import Navbar from './components/Navbar.jsx';
import Hero from './components/Hero.jsx';
import Upload from './components/Upload.jsx';
import Footer from './components/Footer.jsx';

// A new component to hold the main dashboard content for better organization
const Dashboard = () => {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Upload />
      </main>
      <Footer />
    </>
  );
};


function App() {
  // State to manage if the user is authenticated. It starts as 'false'.
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // This function will be passed to the Login component and called on a successful login
  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    
  };

  return (
    <div className="App">
      {isAuthenticated ? (
        // If the user IS authenticated, show the main dashboard
        <Dashboard />
      ) : (
        // If the user IS NOT authenticated, show the Login page
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;