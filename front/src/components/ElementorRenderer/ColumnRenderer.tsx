import React from 'react';
import styled from 'styled-components';
import { ElementorElement, ColumnSettings } from '../../types/elementor';
import { WidgetRenderer } from './WidgetRenderer';

/**
 * Componente para renderizar colunas do Elementor
 * Converte settings de coluna em styled-components com responsividade
 */

interface ColumnRendererProps {
  column: ElementorElement;
}

const StyledColumn = styled.div<{ settings: ColumnSettings }>`
  /* Tamanho base da coluna */
  flex: 0 0 ${props => props.settings._column_size}%;
  max-width: ${props => props.settings._column_size}%;
  
  /* Tamanho inline customizado */
  ${props => props.settings._inline_size !== null && props.settings._inline_size !== undefined && `
    flex: 0 0 ${props.settings._inline_size}%;
    max-width: ${props.settings._inline_size}%;
  `}
  
  /* Posicionamento do conteúdo */
  display: flex;
  flex-direction: column;
  
  ${props => props.settings.content_position === 'center' && `
    justify-content: center;
    align-items: center;
  `}
  
  ${props => props.settings.content_position === 'top' && `
    justify-content: flex-start;
    align-items: center;
  `}
  
  ${props => props.settings.content_position === 'bottom' && `
    justify-content: flex-end;
    align-items: center;
  `}
  
  /* Padding */
  ${props => props.settings.padding && `
    padding: ${props.settings.padding.top}${props.settings.padding.unit} 
             ${props.settings.padding.right}${props.settings.padding.unit} 
             ${props.settings.padding.bottom}${props.settings.padding.unit} 
             ${props.settings.padding.left}${props.settings.padding.unit};
  `}
  
  /* Margin */
  ${props => props.settings.margin && `
    margin: ${props.settings.margin.top}${props.settings.margin.unit} 
            ${props.settings.margin.right}${props.settings.margin.unit} 
            ${props.settings.margin.bottom}${props.settings.margin.unit} 
            ${props.settings.margin.left}${props.settings.margin.unit};
  `}
  
  /* Z-index */
  ${props => props.settings.z_index && `
    z-index: ${props.settings.z_index};
  `}
  
  /* Responsividade - Tablet */
  @media (max-width: 1024px) {
    /* Hide on tablet */
    ${props => props.settings.hide_tablet === 'hidden-tablet' && `
      display: none;
    `}
    
    /* Tamanho tablet */
    ${props => props.settings._inline_size_tablet && `
      flex: 0 0 ${props.settings._inline_size_tablet}%;
      max-width: ${props.settings._inline_size_tablet}%;
    `}
    
    /* Content position tablet */
    ${props => props.settings.content_position_tablet === 'center' && `
      justify-content: center;
      align-items: center;
    `}
    
    /* Padding tablet */
    ${props => props.settings.padding_tablet && `
      padding: ${props.settings.padding_tablet.top}${props.settings.padding_tablet.unit} 
               ${props.settings.padding_tablet.right}${props.settings.padding_tablet.unit} 
               ${props.settings.padding_tablet.bottom}${props.settings.padding_tablet.unit} 
               ${props.settings.padding_tablet.left}${props.settings.padding_tablet.unit};
    `}
    
    /* Margin tablet */
    ${props => props.settings.margin_tablet && `
      margin: ${props.settings.margin_tablet.top}${props.settings.margin_tablet.unit} 
              ${props.settings.margin_tablet.right}${props.settings.margin_tablet.unit} 
              ${props.settings.margin_tablet.bottom}${props.settings.margin_tablet.unit} 
              ${props.settings.margin_tablet.left}${props.settings.margin_tablet.unit};
    `}
  }
  
  /* Responsividade - Mobile */
  @media (max-width: 768px) {
    /* Hide on mobile */
    ${props => props.settings.hide_mobile === 'hidden-mobile' && `
      display: none;
    `}
    
    /* Tamanho mobile */
    ${props => props.settings._inline_size_mobile && `
      flex: 0 0 ${props.settings._inline_size_mobile}%;
      max-width: ${props.settings._inline_size_mobile}%;
    `}
    
    /* Content position mobile */
    ${props => props.settings.content_position_mobile === 'center' && `
      justify-content: center;
      align-items: center;
    `}
    
    ${props => props.settings.content_position_mobile === 'top' && `
      justify-content: flex-start;
      align-items: center;
    `}
    
    /* Padding mobile */
    ${props => props.settings.padding_mobile && `
      padding: ${props.settings.padding_mobile.top}${props.settings.padding_mobile.unit} 
               ${props.settings.padding_mobile.right}${props.settings.padding_mobile.unit} 
               ${props.settings.padding_mobile.bottom}${props.settings.padding_mobile.unit} 
               ${props.settings.padding_mobile.left}${props.settings.padding_mobile.unit};
    `}
    
    /* Margin mobile */
    ${props => props.settings.margin_mobile && `
      margin: ${props.settings.margin_mobile.top}${props.settings.margin_mobile.unit} 
              ${props.settings.margin_mobile.right}${props.settings.margin_mobile.unit} 
              ${props.settings.margin_mobile.bottom}${props.settings.margin_mobile.unit} 
              ${props.settings.margin_mobile.left}${props.settings.margin_mobile.unit};
    `}
    
    /* Mobile: full width por padrão */
    ${props => !props.settings._inline_size_mobile && `
      flex: 0 0 100%;
      max-width: 100%;
    `}
  }
  
  /* Hide on desktop */
  ${props => props.settings.hide_desktop === 'hidden-desktop' && `
    @media (min-width: 1025px) {
      display: none;
    }
  `}
`;

/**
 * Renderiza uma coluna do Elementor
 * Pode conter widgets ou seções internas (inner sections)
 */
export const ColumnRenderer: React.FC<ColumnRendererProps> = ({ column }) => {
  const settings = column.settings as ColumnSettings;
  
  return (
    <StyledColumn settings={settings} className="elementor-column">
      {column.elements.map((element) => {
        // Se for uma seção interna, renderizar como seção
        if (element.elType === 'section' && element.isInner) {
          // Renderizar seção interna sem import circular
          return (
            <div key={element.id} className="elementor-inner-section">
              {element.elements.map((innerElement) => (
                element.elType === 'column' ? 
                  <ColumnRenderer key={innerElement.id} column={innerElement} /> :
                  <WidgetRenderer key={innerElement.id} widget={innerElement} />
              ))}
            </div>
          );
        }
        
        // Se for um widget, renderizar como widget
        if (element.elType === 'widget') {
          return <WidgetRenderer key={element.id} widget={element} />;
        }
        
        // Se for uma coluna, renderizar recursivamente
        if (element.elType === 'column') {
          return <ColumnRenderer key={element.id} column={element} />;
        }
        
        return null;
      })}
    </StyledColumn>
  );
};