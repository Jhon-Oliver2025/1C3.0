import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';

/**
 * Componente da página inicial
 * Renderiza uma página simples de boas-vindas
 */
function HomePage() {
  return (
    <div style={{ 
      padding: '40px', 
      textAlign: 'center',
      backgroundColor: 'white',
      borderRadius: '10px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>🚀 1Crypten</h1>
      <p style={{ color: '#666', fontSize: '18px' }}>Frontend funcionando perfeitamente!</p>
      <p style={{ color: '#999', fontSize: '14px', marginTop: '20px' }}>Build realizado com sucesso ✅</p>
      <div style={{ marginTop: '30px' }}>
        <p style={{ color: '#555' }}>Plataforma de análise de criptomoedas</p>
      </div>
    </div>
  );
}

/**
 * Componente principal da aplicação
 * Gerencia o roteamento da aplicação
 */
function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="*" element={<HomePage />} />
    </Routes>
  );
}

export default App;