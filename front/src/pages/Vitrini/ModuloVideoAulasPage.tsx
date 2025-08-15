import React from 'react';
import { PageRenderer } from '../../components/ElementorRenderer';
import { ElementorPage } from '../../types/elementor';
import StandardFooter from '../../components/StandardFooter/StandardFooter';
import moduloVideoAulasData from './Modulo-VideoAulas.json.json';

/**
 * Página Módulo de Vídeo Aulas
 * Renderiza a página de módulo com playlist de vídeos migrada do WordPress/Elementor
 */

const ModuloVideoAulasPage: React.FC = () => {
  // Converter os dados JSON para o tipo correto
  const pageData = moduloVideoAulasData as ElementorPage;
  
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