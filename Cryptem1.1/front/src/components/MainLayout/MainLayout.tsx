
import React, { useState, useEffect, useCallback } from 'react'; // Added useCallback
import { Outlet, useNavigate, useLocation } from 'react-router-dom'; // NEW: Added useLocation
import TopHeader from '../Layout/TopHeader';
import BottomNavBar from '../Layout/BottomNavBar';
import Navbar from '../Navbar/Navbar';
import styles from '../Layout/Layout.module.css';

const MainLayout: React.FC = () => {
  // --- DEBUG: Hardcoding state and disabling useEffect for debugging rendering issues ---
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false); // State for backend status
  const navigate = useNavigate();
  const location = useLocation(); // Get current location

  // Function to check backend status
  const checkBackendStatus = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/status'); // Endpoint de status do seu backend
      setIsBackendOnline(response.ok); // Se a resposta for 200-299, está online
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

    return () => clearInterval(intervalId); // Cleanup interval
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
      {/* Mostra a Navbar de desktop em telas maiores */}
      <div className={styles.desktopNavContainer}>
        <Navbar 
          isAuthenticated={isAuthenticated} 
          onLogout={handleLogout} 
          isBackendOnline={isDashboardRoute ? isBackendOnline : undefined} // MODIFIED: Pass undefined if not dashboard
        />
      </div>

      {/* Mostra o TopHeader em telas menores */}
      <div className={styles.mobileNavContainer}>
        <TopHeader 
          isBackendOnline={isDashboardRoute ? isBackendOnline : undefined} // MODIFIED: Pass undefined if not dashboard
        />
      </div>

      <main className={styles.mainContent}>
        <Outlet /> {/* Renderiza as rotas aninhadas */}
      </main>

      {/* Mostra a BottomNavBar em telas menores */}
      {isAuthenticated && (
        <div className={styles.mobileNavContainer}>
          <BottomNavBar onLogout={handleLogout} />
        </div>
      )}
    </div>
  );
};

export default MainLayout;
