import React from 'react';
import { useNavigate } from 'react-router-dom'; // Importar useNavigate para o botão
// import Navbar from '../components/Navbar/Navbar.tsx'; // REMOVA ESTA LINHA
import styles from './LandingPage.module.css';
import logo from '../assets/logo.png'; // Importar o logo.png

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const handleEnterClick = () => {
    navigate('/login'); // Redireciona para a página de login
  };

  return (
    <>
      {/* REMOVA ESTE BLOCO: Navbar para a Landing Page (não autenticado) */}
      {/* <Navbar
        isAuthenticated={false}
        isBackendOnline={true} // Assumimos que o backend está online para a página de entrada
        onLogout={() => {}} // Função vazia, pois não há logout na Landing Page
      /> */}
      <div className={styles.landingPageContainer}>
        <img src={logo} alt="CryptoSignals Logo" className={styles.landingPageLogo} /> {/* Adiciona o logo */}
        <h1>Bem-vindo ao Futuro Cripto.</h1> {/* Texto do título atualizado */}
        <p>Construa seu patrimônio com estratégias inteligentes.</p> {/* Texto do parágrafo atualizado */}
        <button onClick={handleEnterClick} className={styles.enterButton}>
          Entrar
        </button>
      </div>
    </>
  );
};

export default LandingPage;