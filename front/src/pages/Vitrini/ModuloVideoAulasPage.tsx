import React from 'react';
import { PageRenderer } from '../../components/ElementorRenderer';
import { ElementorPage } from '../../types/elementor';
import StandardFooter from '../../components/StandardFooter/StandardFooter';

/**
 * Página Módulo de Vídeo Aulas
 * Renderiza a página de módulo com playlist de vídeos migrada do WordPress/Elementor
 */

const ModuloVideoAulasPage: React.FC = () => {
  // Dados temporários para o módulo de vídeo aulas
  const pageData: ElementorPage = {
    id: 'modulo-video-aulas',
    title: 'Módulo de Vídeo Aulas',
    content: [],
    settings: {}
  };
  
  return (
    <div className="modulo-video-aulas-page">
      <PageRenderer 
        pageData={pageData}
        className="modulo-video-aulas"
      />
      <StandardFooter />
    </div>
  );
};

export default ModuloVideoAulasPage;