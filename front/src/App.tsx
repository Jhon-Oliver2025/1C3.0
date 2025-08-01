import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
// REMOVIDO: import ChatInterface from './pages/ChatInterface/ChatInterface';

// Importe o novo componente MainLayout
import MainLayout from './components/MainLayout/MainLayout';

// Importe o novo componente UnderConstructionPage
import UnderConstructionPage from './pages/UnderConstructionPage';

// Importações das novas páginas
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
// REMOVIDO: import BtcSentimentPage from './pages/BtcSentimentPage';
// REMOVIDO: import MinhaContaPage from './pages/MinhaContaPage';

function App() {
  return (
    <Routes>
      {/* Rotas que NÃO usam a Navbar (ex: login, registro) */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/terms-of-service" element={<TermsOfServicePage />} />
      <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />

      {/* Rotas que usam a Navbar e o contexto de autenticação */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        {/* REMOVIDO: <Route path="/btc-sentiment" element={<BtcSentimentPage />} /> */}
        {/* REMOVIDO: <Route path="/minha-conta" element={<MinhaContaPage />} /> */}
        <Route path="/suporte" element={<UnderConstructionPage />} />
        {/* REMOVIDO: <Route path="/configuracoes" element={<UnderConstructionPage />} /> */}
        {/* REMOVIDO: <Route path="/chat" element={<ChatInterface />} /> */}
      </Route>
    </Routes>
  );
}

export default App;