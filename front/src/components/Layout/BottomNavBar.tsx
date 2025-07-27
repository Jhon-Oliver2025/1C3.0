import { NavLink } from 'react-router-dom';
import {
  FaHome,
  FaChartBar,
  FaUser,
  FaCog,
  FaQuestionCircle,
  FaSignOutAlt, // Ícone de sair
} from 'react-icons/fa';
import styles from './Layout.module.css';

interface BottomNavBarProps {
  onLogout: () => void;
}

const BottomNavBar: React.FC<BottomNavBarProps> = ({ onLogout }) => {
  return (
    <nav className={styles.bottomNavBar}>
      <NavLink to="/dashboard" className={({ isActive }) => `${styles.iconWrapper} ${isActive ? styles.activeIcon : ''}`}>
        <FaHome />
        <span>Início</span>
      </NavLink>
      <NavLink to="/btc-sentiment" className={({ isActive }) => `${styles.iconWrapper} ${isActive ? styles.activeIcon : ''}`}>
        <FaChartBar />
        <span>Sentimento</span>
      </NavLink>
      <NavLink to="/minha-conta" className={({ isActive }) => `${styles.iconWrapper} ${isActive ? styles.activeIcon : ''}`}>
        <FaUser />
        <span>Conta</span>
      </NavLink>
      <NavLink to="/configuracoes" className={({ isActive }) => `${styles.iconWrapper} ${isActive ? styles.activeIcon : ''}`}>
        <FaCog />
        <span>Ajustes</span>
      </NavLink>
      <NavLink to="/suporte" className={({ isActive }) => `${styles.iconWrapper} ${isActive ? styles.activeIcon : ''}`}>
        <FaQuestionCircle />
        <span>Suporte</span>
      </NavLink>
      <div className={styles.iconWrapper} onClick={onLogout}>
        <FaSignOutAlt />
        <span>Sair</span>
      </div>
    </nav>
  );
};

export default BottomNavBar;
