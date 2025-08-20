
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../Navbar/Navbar';

// Adicionar interface para props
interface MainLayoutProps {
  children?: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Function to check backend status
  const checkBackendStatus = useCallback(async () => {
    try {
      // Usar proxy do nginx em vez de conectar diretamente na porta 5000
      const response = await fetch('/api/status');
      setIsBackendOnline(response.ok);
    } catch (error) {
      console.error('Erro ao verificar status do backend:', error);
      setIsBackendOnline(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);

    // Check backend status immediately and then every 30 seconds
    checkBackendStatus();
    const intervalId = setInterval(checkBackendStatus, 30000);

    return () => clearInterval(intervalId);
  }, [checkBackendStatus]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/login');
  };

  // Determine if the current route is the dashboard
  const isDashboardRoute = location.pathname === '/dashboard';

  return (
    <div style={{ minHeight: '100vh' }}>
      {/* ÚNICO HEADER DO SISTEMA */}
      <Navbar 
        isAuthenticated={isAuthenticated} 
        onLogout={handleLogout} 
        isBackendOnline={isDashboardRoute ? isBackendOnline : undefined}
      />

      {/* Main Content */}
      <main style={{ paddingTop: isDashboardRoute ? '60px' : '70px' }}>
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
