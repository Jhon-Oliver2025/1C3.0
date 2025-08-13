import { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import styles from './Navbar.module.css';
import logo3 from '/logo3.png';
// CORRIGIDO: Removidos FaChartBar, FaUser, FaCog que não são mais utilizados
import { FaHome, FaQuestionCircle, FaSignOutAlt, FaSignInAlt } from 'react-icons/fa';

interface NavbarProps {
  isAuthenticated: boolean;
  onLogout: () => void;
  isBackendOnline?: boolean; // MODIFIED: Made optional
}

const Navbar: React.FC<NavbarProps> = ({ isAuthenticated, onLogout, isBackendOnline }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.logoContainer}>
        <NavLink to="/" end className={styles.logoLink}>
          {/* MODIFIED: Conditional class application */}
          <div className={`${styles.logoWrapper} ${isBackendOnline === true ? styles.online : (isBackendOnline === false ? styles.offline : '')}`}>
            <img src={logo3} alt="CrypTen Logo" className={styles.crypTenLogo} />
          </div>
        </NavLink>
      </div>

      <div className={styles.desktopNav}>
        {isAuthenticated ? (
          <>
            <NavLink to="/dashboard" end className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Dashboard</NavLink>
            {/* REMOVIDO: <NavLink to="/btc-sentiment" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Sentimento BTC</NavLink> */}
            {/* REMOVIDO: <NavLink to="/minha-conta" className={({ isActive }) => isActive ? styles.activeNavLink : styles.navLink}>Minha Conta</NavLink> */}
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

      {/* Hamburger menu button */}
      <div className={styles.hamburger} onClick={toggleMobileMenu}>
        <div className={styles.bar}></div>
        <div className={styles.bar}></div>
        <div className={styles.bar}></div>
      </div>

      {/* Mobile menu/sidebar */}
      {isMobileMenuOpen && (
        <div className={styles.mobileMenuOverlay} onClick={toggleMobileMenu}>
          <div className={styles.mobileMenu} onClick={(e) => e.stopPropagation()}>
            {isAuthenticated ? (
              <>
                <NavLink to="/dashboard" end className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                  <FaHome /> Dashboard
                </NavLink>
                {/* REMOVIDO: <NavLink to="/btc-sentiment" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                  <FaChartBar /> Sentimento BTC
                </NavLink> */}
                {/* REMOVIDO: <NavLink to="/minha-conta" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                  <FaUser /> Minha Conta
                </NavLink> */}
                <NavLink to="/suporte" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                  <FaQuestionCircle /> Suporte
                </NavLink>
                {/* REMOVIDO: <NavLink to="/configuracoes" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                  <FaCog /> Configurações
                </NavLink> */}
                {/* REMOVIDO: <NavLink to="/chat" className={`${styles.mobileNavLink} ${styles.zionMobileButton}`} onClick={toggleMobileMenu}>
                  Zion
                </NavLink> */}
                <Link to="/" className={`${styles.mobileNavLink} ${styles.logoutLink}`} onClick={() => { onLogout(); toggleMobileMenu(); }}>
                  <FaSignOutAlt /> Sair
                </Link>
              </>
            ) : (
              <>
                {/* REMOVIDO: <NavLink to="/chat" className={`${styles.mobileNavLink} ${styles.zionMobileButton}`} onClick={toggleMobileMenu}>
                  Zion
                </NavLink> */}
                <NavLink to="/login" className={({ isActive }) => isActive ? styles.activeMobileNavLink : styles.mobileNavLink} onClick={toggleMobileMenu}>
                  <FaSignInAlt /> Login
                </NavLink>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
