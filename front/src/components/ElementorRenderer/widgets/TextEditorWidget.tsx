import React from 'react';
import styled from 'styled-components';
import { ElementorElement, TextEditorWidgetSettings } from '../../../types/elementor';

interface TextEditorWidgetProps {
  widget: ElementorElement;
}

const StyledTextEditor = styled.div<{ settings: TextEditorWidgetSettings }>`
  /* Typography */
  ${props => props.settings.typography_font_family && `font-family: ${props.settings.typography_font_family};`}
  ${props => props.settings.typography_font_size && `font-size: ${props.settings.typography_font_size.size}${props.settings.typography_font_size.unit};`}
  ${props => props.settings.typography_font_weight && `font-weight: ${props.settings.typography_font_weight};`}
  ${props => props.settings.typography_line_height && `line-height: ${props.settings.typography_line_height.size}${props.settings.typography_line_height.unit};`}
  
  /* Cor do texto */
  ${props => props.settings.text_color && `color: ${props.settings.text_color};`}
  
  /* Alinhamento */
  ${props => props.settings.align && `text-align: ${props.settings.align};`}
  
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
  
  /* Responsividade - Mobile */
  @media (max-width: 768px) {
    ${props => props.settings.typography_font_size_mobile && `font-size: ${props.settings.typography_font_size_mobile.size}${props.settings.typography_font_size_mobile.unit};`}
    ${props => props.settings.align_mobile && `text-align: ${props.settings.align_mobile};`}
    
    ${props => props.settings._margin_mobile && `
      margin: ${props.settings._margin_mobile.top}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.right}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.bottom}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.left}${props.settings._margin_mobile.unit};
    `}
    
    ${props => props.settings._padding_mobile && `
      padding: ${props.settings._padding_mobile.top}${props.settings._padding_mobile.unit} 
               ${props.settings._padding_mobile.right}${props.settings._padding_mobile.unit} 
               ${props.settings._padding_mobile.bottom}${props.settings._padding_mobile.unit} 
               ${props.settings._padding_mobile.left}${props.settings._padding_mobile.unit};
    `}
  }
`;

export const TextEditorWidget: React.FC<TextEditorWidgetProps> = ({ widget }) => {
  const settings = widget.settings as TextEditorWidgetSettings;
  
  if (!settings.editor) {
    return null;
  }
  
  return (
    <StyledTextEditor 
      settings={settings}
      dangerouslySetInnerHTML={{ __html: settings.editor }}
    />
  );
};