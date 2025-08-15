import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import './styles/mobile-essential.css';

// Importar componentes de páginas
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import StatsPage from './pages/StatsPage/StatsPage';
import BtcSentimentPage from './pages/BtcSentimentPage';
import MinhaContaPage from './pages/MinhaContaPage';
import ConfiguracoesPage from './pages/ConfiguracoesPage';
import SuportePage from './pages/Suporte/SuportePage';
import SairPage from './pages/SairPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import App1CryptenPage from './pages/App1CryptenPage/App1CryptenPage';
import VitrineAlunosPage from './pages/Vitrini/VitrineAlunosPage';
import ModuloVideoAulasPage from './pages/Vitrini/ModuloVideoAulasPage';
import AulaPage from './pages/Aula/AulaPage';
import PaymentSuccessPage from './pages/Payment/PaymentSuccessPage';
import PaymentFailurePage from './pages/Payment/PaymentFailurePage';
import CheckoutDemoPage from './pages/CheckoutDemo/CheckoutDemoPage';
import CheckoutDespertarCryptoPage from './pages/CheckoutDespertarCrypto/CheckoutDespertarCryptoPage';
import SalesPage from './pages/SalesPage/SalesPage';
import SalesAdminPage from './pages/SalesAdmin/SalesAdminPage';

import MainLayout from './components/MainLayout/MainLayout';
import UpdateNotification from './components/UpdateNotification/UpdateNotification';

/**
 * Componente para verificar autenticação
 * Redireciona para login se não autenticado
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = !!localStorage.getItem('token');
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

/**
 * Componente principal da aplicação
 * Gerencia todo o roteamento da aplicação
 */
function App() {
  return (
    <div>
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
      
      {/* Rotas das páginas Elementor */}
      <Route path="/vitrine-alunos" element={<VitrineAlunosPage />} />
      <Route path="/modulo-video-aulas" element={<ModuloVideoAulasPage />} />
      <Route path="/checkout-demo" element={<CheckoutDemoPage />} />
      <Route path="/checkout/despertar-crypto" element={<CheckoutDespertarCryptoPage />} />
      <Route path="/sales" element={<SalesPage />} />
      <Route path="/sales-admin" element={<SalesAdminPage />} />
      
      {/* Rotas das aulas do Despertar Crypto */}
      <Route path="/aula/:aulaId" element={<AulaPage />} />
      
      {/* Rotas de pagamento */}
      <Route path="/payment/success" element={<PaymentSuccessPage />} />
      <Route path="/payment/failure" element={<PaymentFailurePage />} />
      <Route path="/payment/pending" element={<PaymentSuccessPage />} />
      
      {/* Rotas protegidas com layout */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <MainLayout>
            <DashboardPage />
          </MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/estatisticas" element={
        <ProtectedRoute>
          <MainLayout>
            <StatsPage />
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
          <SuportePage />
        </ProtectedRoute>
      } />
      
      <Route path="/sair" element={
        <ProtectedRoute>
          <SairPage />
        </ProtectedRoute>
      } />
      
      <Route path="/app" element={
        <ProtectedRoute>
          <App1CryptenPage />
        </ProtectedRoute>
      } />
      

      
      {/* Rota catch-all - redireciona para landing page */}
      <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      
      {/* Componente de notificação de atualização */}
      <UpdateNotification />
    </div>
  );
}

export default App;