import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styles from './LoginPage.module.css';
import logo from '../assets/logo.png';

const RegisterPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState(''); // Novo estado para confirmar senha
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage('');

        // Verifica se as senhas são iguais
        if (password !== confirmPassword) {
            setMessage('As senhas não coincidem.');
            return; // Interrompe a função se as senhas não forem iguais
        }

        try {
            const response = await fetch('/api/auth/register', { // CORRIGIDO: endpoint correto
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    username: email, // CORRIGIDO: backend espera username
                    email: email,
                    password 
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro no registro');
            }

            setMessage(data.message);
            console.log('Registro bem-sucedido:', data);
            navigate('/login');

        } catch (error: any) {
            console.error('Erro de rede ou servidor:', error);
            setMessage(error.message || 'Ocorreu um erro ao tentar registrar.');
        }
    };

    return (
        <div className={styles.loginPageContainer}>
            <div className={styles.loginCard}>
                <div className={styles.logoSection}>
                    <Link to="/"> {/* Adicione esta linha */}
                        <img src={logo} alt="CrypTen Logo" className={styles.crypTenLogo} />
                    </Link> {/* Adicione esta linha */}
                </div>
                <h2>Criar Nova Conta</h2>
                <p>Preencha os dados para se registrar</p>

                <form onSubmit={handleRegister}>
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
                        <label htmlFor="password">Senha</label>
                        <input
                            type="password"
                            id="password"
                            placeholder="********"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            autoComplete="new-password"
                            required
                        />
                    </div>
                    <div className={styles.formGroup}>
                        <label htmlFor="confirmPassword">Confirmar Senha</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            placeholder="********"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            autoComplete="new-password"
                            required
                        />
                    </div>
                    <button type="submit" className={styles.loginButton}>Registrar</button>
                </form>
                {message && <p className={styles.errorMessage}>{message}</p>}
                <p className={styles.registerLink}>
                    Já tem uma conta? <Link to="/login">Faça login aqui</Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;