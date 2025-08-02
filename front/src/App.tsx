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

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="*" element={<HomePage />} />
    </Routes>
  );
}

export default App;