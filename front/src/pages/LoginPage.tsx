import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './LoginPage.module.css';
import logo from '../assets/logo.png';
import { Link } from 'react-router-dom';
import { usePWA } from '../components/PWA/PWAProvider';

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, authLoading: isLoading, authError: error, isAuthenticated, clearAuthError: clearError } = usePWA();

  // Redirecionar se já estiver autenticado
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError(); // Limpar erros anteriores

    const success = await login(email, password);
    if (success) {
      navigate('/dashboard', { replace: true });
    }
  };

  // Limpar erro quando o usuário começar a digitar
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (error) clearError();
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    if (error) clearError();
  };

  return (
    <div className={styles.loginPageContainer}>
      <div className={styles.loginCard}>
        <div className={styles.logoSection}>
          <Link to="/"> {/* Adicione esta linha */}
            <img src={logo} alt="CrypTen Logo" className={styles.crypTenLogo} />
          </Link> {/* Adicione esta linha */}
          {/* Se você tiver um texto específico para o logo, pode adicioná-lo aqui */}
          {/* <span className={styles.crypTenText}>CrypTen</span> */}
        </div>
        <h2>Vamos Começar</h2>
        <p>Insira os seus dados para continuar</p>

        <form onSubmit={handleLogin}>
          <div className={styles.formGroup}>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              placeholder="seuemail@exemplo.com"
              value={email}
              onChange={handleEmailChange}
              autoComplete="username"
              disabled={isLoading}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              placeholder="********"
              value={password}
              onChange={handlePasswordChange}
              autoComplete="current-password"
              disabled={isLoading}
              required
            />
          </div>
          {error && <p className={styles.errorMessage}>{error}</p>} {/* Exibe a mensagem de erro */}
          <button type="submit" className={styles.loginButton} disabled={isLoading}>
            {isLoading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
        {/* Adiciona o link para a página de registro */}
        <p className={styles.registerLink}>
          Não tem uma conta? <Link to="/register">Crie sua conta aqui</Link>
        </p>
        {/* Adiciona o link para a página de recuperação de senha */}
        <p className={styles.forgotPasswordLink}>
          <Link to="/forgot-password">Esqueceu sua senha?</Link>
        </p>
        {/* Adiciona os links para Termos de Serviço e Política de Privacidade */}
        {/* MOVIDO PARA DENTRO DO loginCard */}
        <div className={styles.policyLinks}>
          <p>Ao usar este serviço, você concorda com nossos</p>
          <p>
            <Link to="/terms-of-service">Termos de Serviço</Link> e <Link to="/privacy-policy">Política de Privacidade</Link>.
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;