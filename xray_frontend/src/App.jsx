import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Upload from './components/Upload';
import Footer from './components/Footer';

function App() {
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
}

export default App;