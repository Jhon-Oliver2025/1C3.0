import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// import Navbar from '../components/Navbar/Navbar.tsx'; // REMOVA ESTA LINHA
import styles from './PageUnderConstruction.module.css'; // Reutilizando o CSS para um estilo básico

const SairPage: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Simula um processo de logout (ex: limpar token, estado de usuário)
    console.log('Simulando logout...');
    // Redireciona para a Landing Page após um pequeno atraso (opcional)
    const timer = setTimeout(() => {
      navigate('/'); // Redireciona para a Landing Page
    }, 1000); // 1 segundo de atraso

    return () => clearTimeout(timer); // Limpa o timer se o componente for desmontado
  }, [navigate]);

  return (
    <>
      {/* REMOVA ESTA LINHA: <Navbar isAuthenticated={true} /> */}
      <div className={styles.container}>
        <h1 className={styles.title}>Saindo...</h1>
        <p className={styles.message}>
          Você será redirecionado para a página inicial.
        </p>
      </div>
    </>
  );
};

export default SairPage;