import { NavLink } from 'react-router-dom';
import styles from './Layout.module.css';
import logo2 from '../../assets/logo2.png'; // Importa o logo2.png

interface TopHeaderProps {
  isBackendOnline?: boolean; // MODIFIED: Made optional
}

const TopHeader: React.FC<TopHeaderProps> = ({ isBackendOnline }) => {
  return (
    <header className={styles.topHeader}>
      <div className={styles.logoContainer}>
        <NavLink to="/" end>
          {/* MODIFIED: Conditional class application */}
          <div className={`${styles.logoWrapper} ${isBackendOnline === true ? styles.online : (isBackendOnline === false ? styles.offline : '')}`}>
            <img src={logo2} alt="CrypTen Logo" className={styles.logo} />
          </div>
        </NavLink>
      </div>
    </header>
  );
};

export default TopHeader;