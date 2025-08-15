import React from 'react';
import styled from 'styled-components';
import { ElementorElement, HeadingWidgetSettings } from '../../../types/elementor';

/**
 * Widget de Heading (Título) do Elementor
 * Suporta typography, cores, sombras e responsividade
 */

interface HeadingWidgetProps {
  widget: ElementorElement;
}

const StyledHeading = styled.div<{ settings: HeadingWidgetSettings; tag: string }>`
  /* Typography */
  ${props => props.settings.typography_font_family && `
    font-family: ${props.settings.typography_font_family};
  `}
  
  ${props => props.settings.typography_font_size && `
    font-size: ${props.settings.typography_font_size.size}${props.settings.typography_font_size.unit};
  `}
  
  ${props => props.settings.typography_font_weight && `
    font-weight: ${props.settings.typography_font_weight};
  `}
  
  ${props => props.settings.typography_line_height && `
    line-height: ${props.settings.typography_line_height.size}${props.settings.typography_line_height.unit};
  `}
  
  ${props => props.settings.typography_letter_spacing && `
    letter-spacing: ${props.settings.typography_letter_spacing.size}${props.settings.typography_letter_spacing.unit};
  `}
  
  ${props => props.settings.typography_word_spacing && `
    word-spacing: ${props.settings.typography_word_spacing.size}${props.settings.typography_word_spacing.unit};
  `}
  
  /* Cor do título */
  ${props => props.settings.title_color && `
    color: ${props.settings.title_color};
  `}
  
  /* Alinhamento */
  ${props => props.settings.align === 'center' && `
    text-align: center;
  `}
  
  ${props => props.settings.align === 'left' && `
    text-align: left;
  `}
  
  ${props => props.settings.align === 'right' && `
    text-align: right;
  `}
  
  ${props => props.settings.align === 'justify' && `
    text-align: justify;
  `}
  
  /* Text shadow */
  ${props => props.settings.text_shadow_text_shadow_type === 'yes' && props.settings.text_shadow_text_shadow && `
    text-shadow: ${props.settings.text_shadow_text_shadow.horizontal}px 
                 ${props.settings.text_shadow_text_shadow.vertical}px 
                 ${props.settings.text_shadow_text_shadow.blur}px 
                 ${props.settings.text_shadow_text_shadow.color};
  `}
  
  /* Margin */
  ${props => props.settings._margin && `
    margin: ${props.settings._margin.top}${props.settings._margin.unit} 
            ${props.settings._margin.right}${props.settings._margin.unit} 
            ${props.settings._margin.bottom}${props.settings._margin.unit} 
            ${props.settings._margin.left}${props.settings._margin.unit};
  `}
  
  /* Padding */
  ${props => props.settings._padding && `
    padding: ${props.settings._padding.top}${props.settings._padding.unit} 
             ${props.settings._padding.right}${props.settings._padding.unit} 
             ${props.settings._padding.bottom}${props.settings._padding.unit} 
             ${props.settings._padding.left}${props.settings._padding.unit};
  `}
  
  /* Responsividade - Tablet */
  @media (max-width: 1024px) {
    /* Font size tablet */
    ${props => props.settings.typography_font_size_tablet && `
      font-size: ${props.settings.typography_font_size_tablet.size}${props.settings.typography_font_size_tablet.unit};
    `}
    
    /* Alinhamento tablet */
    ${props => props.settings.align_tablet === 'center' && `
      text-align: center;
    `}
    
    ${props => props.settings.align_tablet === 'left' && `
      text-align: left;
    `}
    
    ${props => props.settings.align_tablet === 'right' && `
      text-align: right;
    `}
    
    /* Margin tablet */
    ${props => props.settings._margin_tablet && `
      margin: ${props.settings._margin_tablet.top}${props.settings._margin_tablet.unit} 
              ${props.settings._margin_tablet.right}${props.settings._margin_tablet.unit} 
              ${props.settings._margin_tablet.bottom}${props.settings._margin_tablet.unit} 
              ${props.settings._margin_tablet.left}${props.settings._margin_tablet.unit};
    `}
    
    /* Padding tablet */
    ${props => props.settings._padding_tablet && `
      padding: ${props.settings._padding_tablet.top}${props.settings._padding_tablet.unit} 
               ${props.settings._padding_tablet.right}${props.settings._padding_tablet.unit} 
               ${props.settings._padding_tablet.bottom}${props.settings._padding_tablet.unit} 
               ${props.settings._padding_tablet.left}${props.settings._padding_tablet.unit};
    `}
  }
  
  /* Responsividade - Mobile */
  @media (max-width: 768px) {
    /* Font size mobile */
    ${props => props.settings.typography_font_size_mobile && `
      font-size: ${props.settings.typography_font_size_mobile.size}${props.settings.typography_font_size_mobile.unit};
    `}
    
    /* Alinhamento mobile */
    ${props => props.settings.align_mobile === 'center' && `
      text-align: center;
    `}
    
    ${props => props.settings.align_mobile === 'left' && `
      text-align: left;
    `}
    
    ${props => props.settings.align_mobile === 'right' && `
      text-align: right;
    `}
    
    /* Margin mobile */
    ${props => props.settings._margin_mobile && `
      margin: ${props.settings._margin_mobile.top}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.right}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.bottom}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.left}${props.settings._margin_mobile.unit};
    `}
    
    /* Padding mobile */
    ${props => props.settings._padding_mobile && `
      padding: ${props.settings._padding_mobile.top}${props.settings._padding_mobile.unit} 
               ${props.settings._padding_mobile.right}${props.settings._padding_mobile.unit} 
               ${props.settings._padding_mobile.bottom}${props.settings._padding_mobile.unit} 
               ${props.settings._padding_mobile.left}${props.settings._padding_mobile.unit};
    `}
  }
`;

/**
 * Determina a tag HTML baseada no conteúdo do título
 * Se contém <br>, usa div, senão usa h2 por padrão
 */
const getHeadingTag = (title: string): string => {
  // Se contém HTML (como <br>), usar div
  if (title.includes('<') || title.includes('&')) {
    return 'div';
  }
  
  // Por padrão, usar h2
  return 'h2';
};

/**
 * Limpa e processa o conteúdo do título
 * Remove <br> excessivos e processa HTML
 */
const processTitle = (title: string): string => {
  if (!title) return '';
  
  // Remover múltiplos <br> consecutivos no início
  let processed = title.replace(/^(<br\s*\/?\s*>\s*)+/gi, '');
  
  // Converter <br> para quebras de linha
  processed = processed.replace(/<br\s*\/?\s*>/gi, '\n');
  
  return processed;
};

export const HeadingWidget: React.FC<HeadingWidgetProps> = ({ widget }) => {
  const settings = widget.settings as HeadingWidgetSettings;
  
  if (!settings.title) {
    return null;
  }
  
  const tag = getHeadingTag(settings.title);
  const processedTitle = processTitle(settings.title);
  
  // Se contém HTML, usar dangerouslySetInnerHTML
  if (settings.title.includes('<') || settings.title.includes('&')) {
    return (
      <StyledHeading
        as={tag as any}
        settings={settings}
        tag={tag}
        dangerouslySetInnerHTML={{ __html: processedTitle }}
      />
    );
  }
  
  // Se é texto simples, renderizar normalmente
  return (
    <StyledHeading
      as={tag as any}
      settings={settings}
      tag={tag}
    >
      {processedTitle.split('\n').map((line, index) => (
        <React.Fragment key={index}>
          {line}
          {index < processedTitle.split('\n').length - 1 && <br />}
        </React.Fragment>
      ))}
    </StyledHeading>
  );
};