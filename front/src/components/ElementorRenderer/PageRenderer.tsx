import React from 'react';
import styled from 'styled-components';
import { ElementorPage } from '../../types/elementor';
import { SectionRenderer } from './SectionRenderer';

/**
 * Componente principal para renderizar páginas completas do Elementor
 * Converte JSON exportado do WordPress/Elementor em componentes React
 */

interface PageRendererProps {
  pageData: ElementorPage;
  className?: string;
  logoComponent?: React.ReactNode; // Adiciona a prop para o componente do logo
}

const PageContainer = styled.div<{ $pageSettings: any }>`
  min-height: 100vh;
  width: 100%;
  
  /* Background da página */
  ${props => props.$pageSettings.background_background === 'classic' && props.$pageSettings.background_color && `
    background-color: ${props.$pageSettings.background_color};
  `}
  
  /* Hide title se configurado */
  ${props => props.$pageSettings.hide_title === 'yes' && `
    .page-title {
      display: none;
    }
  `}
  
  /* Grid settings */
  ${props => props.$pageSettings.ha_grid_zindex && `
    z-index: ${props.$pageSettings.ha_grid_zindex};
  `}
`;

const ElementorContent = styled.main`
  width: 100%;
  
  /* Reset de estilos para compatibilidade */
  * {
    box-sizing: border-box;
  }
  
  /* Estilos globais para elementos do Elementor */
  .elementor-row {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
  }
  
  .elementor-column {
    position: relative;
    min-height: 1px;
  }
  
  /* Links padrão */
  a {
    color: inherit;
    text-decoration: none;
    
    &:hover {
      text-decoration: none;
    }
  }
  
  /* Imagens responsivas */
  img {
    max-width: 100%;
    height: auto;
  }
  
  /* Font Awesome icons */
  .fas, .far, .fab {
    font-family: 'Font Awesome 5 Free', 'Font Awesome 5 Brands';
    font-weight: 900;
  }
  
  .far {
    font-weight: 400;
  }
  
  /* Responsividade global */
  @media (max-width: 768px) {
    .elementor-row {
      flex-direction: column;
    }
    
    .elementor-column {
      width: 100% !important;
      max-width: 100% !important;
      flex: 0 0 100% !important;
    }
  }
`;

/**
 * Componente de loading para quando os dados estão carregando
 */
const LoadingPlaceholder = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  color: #666;
  font-size: 16px;
`;

/**
 * Componente de erro para quando há problemas com os dados
 */
const ErrorPlaceholder = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  color: #e74c3c;
  text-align: center;
  
  h3 {
    margin-bottom: 10px;
    color: #e74c3c;
  }
  
  p {
    color: #666;
    max-width: 400px;
  }
`;

/**
 * Valida se os dados da página são válidos
 */
const validatePageData = (pageData: ElementorPage): boolean => {
  if (!pageData) return false;
  if (!pageData.content || !Array.isArray(pageData.content)) return false;
  if (!pageData.page_settings) return false;
  
  return true;
};

/**
 * Renderiza uma página completa do Elementor
 */
export const PageRenderer: React.FC<PageRendererProps> = ({
  pageData,
  className = '',
  logoComponent // Adiciona a prop logoComponent
}) => {
  // Loading state
  if (!pageData) {
    return (
      <LoadingPlaceholder>
        Carregando página...
      </LoadingPlaceholder>
    );
  }
  
  // Validação dos dados
  if (!validatePageData(pageData)) {
    return (
      <ErrorPlaceholder>
        <h3>Erro ao carregar página</h3>
        <p>
          Os dados da página estão corrompidos ou em formato inválido.
          Verifique se o arquivo JSON foi exportado corretamente do Elementor.
        </p>
      </ErrorPlaceholder>
    );
  }
  
  return (
    <PageContainer 
      $pageSettings={pageData.page_settings}
      className={`elementor-page ${className}`}
    >
      {logoComponent && logoComponent} {/* Renderiza o logo se ele for fornecido */}
      <ElementorContent>
        {pageData.content.map((section) => (
          <SectionRenderer 
            key={section.id} 
            section={section} 
          />
        ))}
      </ElementorContent>
    </PageContainer>
  );
};

/**
 * Hook para carregar dados de página do Elementor
 */
export const useElementorPage = (pageJsonPath: string) => {
  const [pageData, setPageData] = React.useState<ElementorPage | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  
  React.useEffect(() => {
    const loadPageData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Importar o JSON dinamicamente
        const response = await fetch(pageJsonPath);
        if (!response.ok) {
          throw new Error(`Erro ao carregar página: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!validatePageData(data)) {
          throw new Error('Dados da página inválidos');
        }
        
        setPageData(data);
      } catch (err) {
        console.error('Erro ao carregar página do Elementor:', err);
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };
    
    if (pageJsonPath) {
      loadPageData();
    }
  }, [pageJsonPath]);
  
  return { pageData, loading, error };
};