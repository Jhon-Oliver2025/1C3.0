import { NavLink } from 'react-router-dom';
import styles from './Layout.module.css';
import logo2 from '../../assets/logo2.png';
import { FaBars } from 'react-icons/fa';

interface TopHeaderProps {
  isBackendOnline?: boolean;
  onMenuToggle?: () => void; // Novo prop para controlar o menu
}

const TopHeader: React.FC<TopHeaderProps> = ({ isBackendOnline, onMenuToggle }) => {
  return (
    <header className={styles.topHeader}>
      <button className={styles.menuButton} onClick={onMenuToggle}>
        <FaBars size={20} />
      </button>
      <div className={styles.logoContainer}>
        <NavLink to="/" end>
          <div className={`${styles.logoWrapper} ${isBackendOnline === true ? styles.online : (isBackendOnline === false ? styles.offline : '')}`}>
            <img src={logo2} alt="CrypTen Logo" className={styles.logo} />
          </div>
        </NavLink>
      </div>
    </header>
  );
};

export default TopHeader;