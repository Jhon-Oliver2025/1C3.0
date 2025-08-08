import { NavLink } from 'react-router-dom';
import styles from './Layout.module.css';
import logo2 from '../../assets/logo2.png';
import { FaBars } from 'react-icons/fa';

interface TopHeaderProps {
  isBackendOnline?: boolean;
  onMenuToggle?: () => void;
}

/**
 * Componente do cabeçalho superior com logo do sistema e indicador de status
 * @param isBackendOnline - Status de conexão com o backend
 * @param onMenuToggle - Função para alternar o menu lateral
 */
const TopHeader: React.FC<TopHeaderProps> = ({ isBackendOnline, onMenuToggle }) => {
  return (
    <header className="mobile-top-header">
      <button className="mobile-menu-button" onClick={onMenuToggle} aria-label="Menu">
        ☰
      </button>
      <div className="mobile-logo-status">
        <span>CRYPTO SIGNALS</span>
      </div>
      <div className="mobile-logo-container">
        <img 
          src={logo2} 
          alt="Logo do Sistema" 
          className={`mobile-system-logo ${isBackendOnline ? 'online' : 'offline'}`}
          title={isBackendOnline ? 'Backend Online' : 'Backend Offline'}
        />
      </div>
    </header>
  );
};

export default TopHeader;