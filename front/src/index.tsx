import React from 'react';
import ReactDOM from 'react-dom/client';
// Removido: import { BrowserRouter as Router } from 'react-router-dom'; // <-- Router importado aqui
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    {/* Removido: <Router> */}
      <App />
    {/* Removido: </Router> */}
  </React.StrictMode>
);