import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import ChatInterface from './pages/ChatInterface/ChatInterface'; // NEW import for ChatInterface

// Importe o novo componente MainLayout
import MainLayout from './components/MainLayout/MainLayout';

// Importe o novo componente UnderConstructionPage
import UnderConstructionPage from './pages/UnderConstructionPage';

// Importações das novas páginas
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import ResetPasswordPage from './pages/ResetPasswordPage'; // Importe a nova página
import BtcSentimentPage from './pages/BtcSentimentPage.tsx'; // Importe a nova página
import MinhaContaPage from './pages/MinhaContaPage'; // Adicione esta linha

function App() {
  return (
    <Router>
      <Routes>
        {/* Rotas que NÃO usam a Navbar (ex: login, registro) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} /> {/* Nova rota para Redefinir Senha */}
        <Route path="/terms-of-service" element={<TermsOfServicePage />} />
        <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />

        {/* Rotas que usam a Navbar e o contexto de autenticação */}
        {/* O MainLayout renderizará a Navbar e seu conteúdo (as rotas aninhadas) */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<LandingPage />} /> {/* Landing page com Navbar */}
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/btc-sentiment" element={<BtcSentimentPage />} /> {/* Adicione esta nova rota */}
          {/* Use UnderConstructionPage para as páginas em desenvolvimento */}
          {/* Substitua esta linha: */}
          {/* <Route path="/minha-conta" element={<UnderConstructionPage />} /> */}
          {/* Por esta: */}
          <Route path="/minha-conta" element={<MinhaContaPage />} />
          <Route path="/suporte" element={<UnderConstructionPage />} />
          <Route path="/configuracoes" element={<UnderConstructionPage />} />
          {/* NEW: Route for the chat interface, now inside MainLayout */}
          <Route path="/chat" element={<ChatInterface />} />
          {/* Adicione mais rotas protegidas/autenticadas aqui, se houver */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;