import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';

// Componente da página inicial
function HomePage() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>🚀 1Crypten</h1>
      <p>Frontend funcionando perfeitamente!</p>
      <p style={{ color: '#999', fontSize: '14px', marginTop: '20px' }}>Build realizado com sucesso ✅</p>
    </div>
  );
}

// Componente principal da aplicação
function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="*" element={<HomePage />} />
    </Routes>
  );
}

export default App;