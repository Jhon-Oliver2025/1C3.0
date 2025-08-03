import React, { useState } from 'react';
import styles from './ForgotPasswordPage.module.css';
import logo from '../assets/logo.png';
import { Link } from 'react-router-dom'; // Adicione esta linha

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    setLoading(true);

    try {
      // Alterar linha 20
      const response = await fetch('/api/forgot-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email }),
      });
      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || 'Se o usuário existir, um e-mail com instruções de redefinição de senha foi enviado.');
      } else {
        setError(data.message || 'Erro ao solicitar redefinição de senha.');
      }

    } catch (err) {
      console.error('Erro de rede ou servidor:', err);
      setError('Não foi possível conectar ao servidor. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.forgotPasswordPageContainer}>
      <div className={styles.forgotPasswordCard}>
        <div className={styles.logoSection}>
          <Link to="/"> {/* Adicione esta linha */}
            <img src={logo} alt="CrypTen Logo" className={styles.crypTenLogo} />
          </Link> {/* Adicione esta linha */}
        </div>
        <h2>Esqueceu sua Senha?</h2>
        <p>Insira seu e-mail para receber um link de redefinição de senha.</p>

        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label htmlFor="email">E-mail</label>
            <input
              type="email"
              id="email"
              placeholder="seuemail@exemplo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          {message && <p className={styles.successMessage}>{message}</p>}
          {error && <p className={styles.errorMessage}>{error}</p>}
          <button type="submit" className={styles.submitButton} disabled={loading}>
            {loading ? 'Enviando...' : 'Redefinir Senha'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;