import React, { useState } from 'react';
import './App.css';

// Import all your components (History is now removed)
import Login from './components/Login.jsx';
import Navbar from './components/Navbar.jsx';
import Hero from './components/Hero.jsx';
import Upload from './components/Upload.jsx';
import ReportGenerator from './components/ReportGenerator.jsx';
import Footer from './components/Footer.jsx';

// The Dashboard no longer needs to manage history state
const Dashboard = () => {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Upload />
        <ReportGenerator />
        {/* The <History /> component has been removed */}
      </main>
      <Footer />
    </>
  );
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <div className="App">
      {isAuthenticated ? (
        <Dashboard />
      ) : (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;