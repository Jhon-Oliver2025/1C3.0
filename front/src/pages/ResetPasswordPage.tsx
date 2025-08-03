import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom'; // Adicione 'Link' aqui
import styles from './ResetPasswordPage.module.css';
import logo from '../assets/logo.png';

const ResetPasswordPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const tokenParam = queryParams.get('token');
    const userIdParam = queryParams.get('userId');

    console.log('location.search:', location.search); // Adicione esta linha
    console.log('tokenParam:', tokenParam);         // Adicione esta linha
    console.log('userIdParam:', userIdParam);       // Adicione esta linha

    if (tokenParam && userIdParam) {
      setToken(tokenParam);
      setUserId(userIdParam);
      setError(null); // Limpa o erro se os parâmetros forem encontrados
    } else {
      setError('Token ou ID de usuário inválido/ausente na URL.');
    }
  }, [location.search]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    setLoading(true);

    if (!token || !userId) {
      setError('Erro: Token ou ID de usuário não encontrado.');
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('As senhas não coincidem.');
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) { // Exemplo de validação de senha
      setError('A nova senha deve ter pelo menos 6 caracteres.');
      setLoading(false);
      return;
    }

    try {
      // Alterar linha 61
      const response = await fetch('/api/reset-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, userId, newPassword }),
      });
      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || 'Senha redefinida com sucesso! Você será redirecionado para a página de login.');
        setTimeout(() => navigate('/login'), 3000); // Redireciona após 3 segundos
      } else {
        setError(data.message || 'Erro ao redefinir senha. Token inválido ou expirado.');
      }

    } catch (err) {
      console.error('Erro de rede ou servidor:', err);
      setError('Não foi possível conectar ao servidor. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.resetPasswordPageContainer}>
      <div className={styles.resetPasswordCard}>
        <div className={styles.logoSection}>
          <Link to="/"> {/* Adicione esta linha */}
            <img src={logo} alt="CrypTen Logo" className={styles.crypTenLogo} />
          </Link> {/* Adicione esta linha */}
        </div>
        <h2>Redefinir Senha</h2>
        <p>Insira sua nova senha abaixo.</p>

        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label htmlFor="newPassword">Nova Senha</label>
            <input
              type="password"
              id="newPassword"
              placeholder="********"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label htmlFor="confirmPassword">Confirmar Nova Senha</label>
            <input
              type="password"
              id="confirmPassword"
              placeholder="********"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          {message && <p className={styles.successMessage}>{message}</p>}
          {error && <p className={styles.errorMessage}>{error}</p>}
          <button type="submit" className={styles.submitButton} disabled={loading || !token || !userId}>
            {loading ? 'Redefinindo...' : 'Redefinir Senha'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPasswordPage;