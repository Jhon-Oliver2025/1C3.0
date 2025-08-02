import { Routes, Route } from 'react-router-dom';
import './App.css';

// Componente simples para teste
function HomePage() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>1Crypten Frontend</h1>
      <p>Aplicação funcionando!</p>
    </div>
  );
}

import React from 'react';

function App() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f0f0f0'
    }}>
      <div style={{
        textAlign: 'center',
        padding: '40px',
        backgroundColor: 'white',
        borderRadius: '10px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ color: '#333', marginBottom: '20px' }}>🚀 1Crypten</h1>
        <p style={{ color: '#666', fontSize: '18px' }}>Frontend funcionando perfeitamente!</p>
        <p style={{ color: '#999', fontSize: '14px', marginTop: '20px' }}>Build realizado com sucesso ✅</p>
      </div>
    </div>
  );
}

export default App;

<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="*" element={<HomePage />} />
</Routes>
}

export default App;