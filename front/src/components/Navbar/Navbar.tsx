import { useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import styles from './Navbar.module.css';
import logo3 from '/logo3.png';
import members1cT from '../../../src/assets/members1cT.png';
import { useAdminCheck } from '../../hooks/useAdminCheck';
// CORRIGIDO: Removidos FaChartBar, FaUser, FaCog que não são mais utilizados
import { FaHome, FaQuestionCircle, FaSignOutAlt, FaSignInAlt } from 'react-icons/fa';

interface NavbarProps {
  isAuthenticated: boolean;
  onLogout: () => void;
  isBackendOnline?: boolean; // MODIFIED: Made optional
}

const Navbar: React.FC<NavbarProps> = ({ isAuthenticated, onLogout, isBackendOnline }) => {
  const location = useLocation();
  const isDashboard = location.pathname === '/dashboard';
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isAdmin } = useAdminCheck();

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <nav className={styles.navbar}>
      {/* Botão Mobile Menu */}
      <button className={styles.mobileMenuButton} onClick={toggleMobileMenu} aria-label="Menu">
        ☰
      </button>
      <div className={styles.logoContainer}>
        {/* Logo removido - apenas espaço para organização */}
      </div>

      <div className={styles.desktopNav}>
        {isAuthenticated ? (
          <>
            <NavLink to="/dashboard" end className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Dashboard</NavLink>
            {/* REMOVIDO: <NavLink to="/btc-sentiment" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Sentimento BTC</NavLink> */}
            {/* REMOVIDO: <NavLink to="/minha-conta" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Minha Conta</NavLink> */}
            {isAdmin && (
              <NavLink to="/crm" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>CRM</NavLink>
            )}
            {isAdmin && (
              <NavLink to="/sales-admin" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Admin VSL</NavLink>
            )}
            {isAdmin && (
              <NavLink to="/btc-analysis" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>BTC Analysis</NavLink>
            )}
            {isAdmin && (
              <NavLink to="/simulacao-trading" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Investimentos Simulados</NavLink>
            )}
            <NavLink to="/suporte" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Suporte</NavLink>
            {/* REMOVIDO: <NavLink to="/configuracoes" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Configurações</NavLink> */}
            {/* REMOVIDO: <NavLink to="/chat" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Zion</NavLink> */}
            <Link to="/" className={`${styles.navLink} ${styles.logoutLink}`} onClick={onLogout}>Sair</Link>
          </>
        ) : (
          <>
            {/* REMOVIDO: <NavLink to="/chat" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Zion</NavLink> */}
            <NavLink to="/login" className={({ isActive }) => `${styles.navLink} ${isActive ? styles.activeNavLink : ''} ${styles.loginLink}`}>Login</NavLink>
          </>
        )}
      </div>

      {/* Logo no canto direito - com status apenas no dashboard */}
      <div className={styles.backendStatus}>
        <div className={`${styles.logoWrapper} ${isDashboard && isBackendOnline !== undefined ? (isBackendOnline ? styles.online : styles.offline) : ''}`}>
          <img 
            src={logo3} 
            alt={isDashboard && isBackendOnline !== undefined ? "Status do Backend" : "CrypTen Logo"} 
            className={styles.crypTenLogo}
            title={isDashboard && isBackendOnline !== undefined ? (isBackendOnline ? 'Backend Online' : 'Backend Offline') : 'CrypTen'}
          />
        </div>
      </div>



      {/* Mobile menu/sidebar */}
      {isMobileMenuOpen && (
        <div className={styles.mobileMenuOverlay} onClick={toggleMobileMenu}>
          <div className={styles.mobileMenu} onClick={(e) => e.stopPropagation()}>
            {isAuthenticated ? (
              <>
                {/* Seção Principal */}
                <div className={styles.menuSection}>
                  <h3 className={styles.menuSectionTitle}>Navegação</h3>
                  <NavLink to="/dashboard" end className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                    Dashboard
                  </NavLink>
                  <NavLink to="/vitrine-alunos" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                    Área de Membros
                  </NavLink>
                </div>

                {/* Seção Suporte */}
                <div className={styles.menuSection}>
                  <h3 className={styles.menuSectionTitle}>Ajuda</h3>
                  <NavLink to="/suporte" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                    Suporte
                  </NavLink>
                  <NavLink to="/app" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                    Baixar App
                  </NavLink>
                </div>
                
                {/* Seção Admin - apenas para administradores */}
                {isAdmin && (
                  <div className={styles.menuSection}>
                    <h3 className={styles.menuSectionTitle}>Administração</h3>
                    <NavLink to="/crm" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                      CRM
                    </NavLink>
                    <NavLink to="/sales-admin" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                      Admin VSL
                    </NavLink>
                    <NavLink to="/btc-analysis" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                      BTC Analysis
                    </NavLink>
                    <NavLink to="/simulacao-trading" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                      Investimentos Simulados
                    </NavLink>
                  </div>
                )}
                
                {/* Seção Logout */}
                <div className={styles.menuSection}>
                  <Link to="/" className={`${styles.mobileNavLink} ${styles.logoutLink}`} onClick={() => { onLogout(); toggleMobileMenu(); }}>
                    Sair
                  </Link>
                </div>
              </>
            ) : (
              <>
                <div className={styles.menuSection}>
                  <NavLink to="/login" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                    Login
                  </NavLink>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
