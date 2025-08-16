import React from 'react';
import RealTimeStats from '../../components/RealTimeStats/RealTimeStats';
// Removido: mobile-essential.css (causava conflitos de header)

/**
 * Página de Estatísticas em Tempo Real
 * Exibe métricas detalhadas do sistema de trading
 */
const StatsPage: React.FC = () => {
  return (
    <div className="mobile-container">
      {/* Container Principal */}
      <main className="mobile-main-container">
        <div className="mobile-page-header">
          <h1 className="mobile-page-title">📊 Estatísticas em Tempo Real</h1>
          <p className="mobile-page-subtitle">Métricas e análises do sistema de trading</p>
        </div>
        
        {/* Componente de Estatísticas */}
        <RealTimeStats />
      </main>
    </div>
  );
};

export default StatsPage;