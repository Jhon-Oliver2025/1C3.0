import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './LoginPage.module.css';
import logo from '../assets/logo.png';
import { Link } from 'react-router-dom'; // Importe o componente Link

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null); // Estado para mensagens de erro
  const [loading, setLoading] = useState(false); // Estado para indicar carregamento

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      console.log('Enviando requisição de login para:', '/api/auth/login');
      console.log('Dados enviados:', { username: email, password: '***' });
      
      // Usar proxy do nginx em vez de conectar diretamente na porta 5000
      const response = await fetch('/api/auth/login', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // CORRIGIDO: O backend espera 'username' e 'password', não 'email'
        body: JSON.stringify({ username: email, password }),
      });

      console.log('Status da resposta:', response.status);
      console.log('Headers da resposta:', response.headers);
      console.log('Response OK:', response.ok);
      
      const data = await response.json();
      console.log('Resposta do backend (data):', data);

      if (response.ok) {
        localStorage.setItem('token', data.token);
        navigate('/dashboard');
      } else {
        setError(data.message || 'Erro ao fazer login. Verifique suas credenciais.');
      }
    } catch (err) {
      console.error('Erro de rede ou servidor:', err);
      setError('Não foi possível conectar ao servidor. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
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
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
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
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          {error && <p className={styles.errorMessage}>{error}</p>} {/* Exibe a mensagem de erro */}
          <button type="submit" className={styles.loginButton} disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'} {/* Altera o texto do botão durante o carregamento */}
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