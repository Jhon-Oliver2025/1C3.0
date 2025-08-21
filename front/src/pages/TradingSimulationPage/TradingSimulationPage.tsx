/**
 * Página de Simulação de Trading
 * Página dedicada para exibir a simulação financeira com $1.000 USD
 */

import React from 'react';
import TradingSimulation from '../../components/TradingSimulation/TradingSimulation';
import styles from './TradingSimulationPage.module.css';
import '../Dashboard/DashboardMobile.css';

const TradingSimulationPage: React.FC = () => {
  return (
    <div className={styles.container}>
      {/* CONTAINER MOTIVACIONAL NO TOPO DA DIV PRINCIPAL (4px) */}
      <div className="mobile-motivation-header-container">
        {/* Seção Motivacional */}
        <div className="mobile-motivational">
          <p className="mobile-motivational-text">
            Transforme dados em decisões inteligentes e maximize seus resultados.
          </p>
        </div>

        {/* Espaçamento de Segurança (4px) */}
        <div className="mobile-safety-gap"></div>
      </div>

      {/* Componente principal de simulação */}
      <div className={styles.content}>
        <TradingSimulation />
      </div>
    </div>
  );
};

export default TradingSimulationPage;