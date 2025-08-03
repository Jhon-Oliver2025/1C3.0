
import React, { useState, useEffect, useCallback } from 'react';
import { Outlet, useNavigate, useLocation, NavLink } from 'react-router-dom';
import TopHeader from '../Layout/TopHeader';
import Navbar from '../Navbar/Navbar';
import styles from '../Layout/Layout.module.css';
import { FaHome, FaQuestionCircle, FaSignOutAlt } from 'react-icons/fa';

// Adicionar interface para props
interface MainLayoutProps {
  children?: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  // Function to check backend status
  const checkBackendStatus = useCallback(async () => {
    try {
      // Alterar linha 26
      const response = await fetch('/api/status/');
      setIsBackendOnline(response.ok);
    } catch (error) {
      console.error('Erro ao verificar status do backend:', error);
      setIsBackendOnline(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    setIsAuthenticated(!!token);

    // Check backend status immediately and then every 5 seconds
    checkBackendStatus();
    const intervalId = setInterval(checkBackendStatus, 5000);

    return () => clearInterval(intervalId);
  }, [checkBackendStatus]);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
    navigate('/login');
  };

  // Determine if the current route is the dashboard
  const isDashboardRoute = location.pathname === '/dashboard';

  return (
    <div className={styles.layoutContainer}>
      {/* Sidebar mobile */}
      <div className={`${styles.sidebarOverlay} ${isMenuOpen ? styles.open : ''}`} onClick={toggleMenu} />
      <div className={`${styles.sidebar} ${isMenuOpen ? styles.open : ''}`}>
        <nav className={styles.sidebarNav}>
          {isAuthenticated ? (
            <>
              <NavLink to="/dashboard" className={({isActive}) => 
                `${styles.sidebarLink} ${isActive ? styles.active : ''}`} 
                onClick={toggleMenu}>
                <FaHome /> Dashboard
              </NavLink>
              {/* REMOVIDO: <NavLink to="/btc-sentiment" className={({isActive}) => 
                `${styles.sidebarLink} ${isActive ? styles.active : ''}`} 
                onClick={toggleMenu}>
                <FaChartBar /> Sentimento BTC
              </NavLink> */}
              {/* REMOVIDO: <NavLink to="/minha-conta" className={({isActive}) => 
                `${styles.sidebarLink} ${isActive ? styles.active : ''}`} 
                onClick={toggleMenu}>
                <FaUser /> Minha Conta
              </NavLink> */}
              <NavLink to="/suporte" className={({isActive}) => 
                `${styles.sidebarLink} ${isActive ? styles.active : ''}`} 
                onClick={toggleMenu}>
                <FaQuestionCircle /> Suporte
              </NavLink>
              {/* REMOVIDO: <NavLink to="/configuracoes" className={({isActive}) => 
                `${styles.sidebarLink} ${isActive ? styles.active : ''}`} 
                onClick={toggleMenu}>
                <FaCog /> Configurações
              </NavLink> */}
              <button className={styles.sidebarLink} onClick={handleLogout}>
                <FaSignOutAlt /> Sair
              </button>
            </>
          ) : (
            <NavLink to="/login" className={({isActive}) => 
              `${styles.sidebarLink} ${isActive ? styles.active : ''}`} 
              onClick={toggleMenu}>
              Login
            </NavLink>
          )}
        </nav>
      </div>

      {/* Desktop Navbar */}
      <div className={styles.desktopNavContainer}>
        <Navbar 
          isAuthenticated={isAuthenticated} 
          onLogout={handleLogout} 
          isBackendOnline={isDashboardRoute ? isBackendOnline : undefined}
        />
      </div>

      {/* Mobile Header */}
      <div className={styles.mobileNavContainer}>
        <TopHeader 
          isBackendOnline={isDashboardRoute ? isBackendOnline : undefined}
          onMenuToggle={toggleMenu}
        />
      </div>

      {/* Main Content */}
      <main className={styles.mainContent}>
        {children || <Outlet />}
      </main>
    </div>
  );
};

export default MainLayout;
