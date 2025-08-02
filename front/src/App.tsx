import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Importar componentes de páginas
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import DashboardPage from './pages/DashboardPage';
import BtcSentimentPage from './pages/BtcSentimentPage';
import MinhaContaPage from './pages/MinhaContaPage';
import ConfiguracoesPage from './pages/ConfiguracoesPage';
import SuportePage from './pages/SuportePage';
import SairPage from './pages/SairPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import MainLayout from './components/MainLayout/MainLayout';

/**
 * Componente para verificar autenticação
 * Redireciona para login se não autenticado
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = !!localStorage.getItem('authToken');
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

/**
 * Componente principal da aplicação
 * Gerencia todo o roteamento da aplicação
 */
function App() {
  return (
    <Routes>
      {/* Rota pública - Landing Page */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Rotas de autenticação */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      
      {/* Rotas públicas de informação */}
      <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
      <Route path="/terms-of-service" element={<TermsOfServicePage />} />
      
      {/* Rotas protegidas com layout */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <MainLayout>
            <DashboardPage />
          </MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/btc-sentiment" element={
        <ProtectedRoute>
          <MainLayout>
            <BtcSentimentPage />
          </MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/minha-conta" element={
        <ProtectedRoute>
          <MainLayout>
            <MinhaContaPage />
          </MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/configuracoes" element={
        <ProtectedRoute>
          <MainLayout>
            <ConfiguracoesPage />
          </MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/suporte" element={
        <ProtectedRoute>
          <MainLayout>
            <SuportePage />
          </MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/sair" element={
        <ProtectedRoute>
          <SairPage />
        </ProtectedRoute>
      } />
      
      {/* Rota catch-all - redireciona para landing page */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;