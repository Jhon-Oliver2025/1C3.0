import React from 'react';
import styled from 'styled-components';
import { ElementorElement, ButtonWidgetSettings } from '../../../types/elementor';

interface ButtonWidgetProps {
  widget: ElementorElement;
}

const StyledButton = styled.a<{ settings: ButtonWidgetSettings }>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  
  /* Typography */
  ${props => props.settings.typography_font_family && `font-family: ${props.settings.typography_font_family};`}
  ${props => props.settings.typography_font_weight && `font-weight: ${props.settings.typography_font_weight};`}
  
  /* Cores */
  ${props => props.settings.button_text_color && `color: ${props.settings.button_text_color};`}
  ${props => props.settings.background_color && `background-color: ${props.settings.background_color};`}
  
  /* Border radius */
  ${props => props.settings.border_radius && `
    border-radius: ${props.settings.border_radius.top}${props.settings.border_radius.unit};
  `}
  
  /* Alinhamento */
  ${props => props.settings.align === 'center' && `margin: 0 auto;`}
  ${props => props.settings.align === 'right' && `margin-left: auto;`}
  
  /* Text shadow */
  ${props => props.settings.text_shadow_text_shadow_type === 'yes' && `text-shadow: 0 1px 3px rgba(0,0,0,0.3);`}
  
  /* Hover */
  &:hover {
    ${props => props.settings.button_background_hover_color && `background-color: ${props.settings.button_background_hover_color};`}
    transform: translateY(-1px);
  }
  
  /* Hide responsivo */
  ${props => props.settings.hide_desktop === 'hidden-desktop' && `
    @media (min-width: 1025px) { display: none; }
  `}
  
  ${props => props.settings.hide_tablet === 'hidden-tablet' && `
    @media (max-width: 1024px) and (min-width: 769px) { display: none; }
  `}
  
  ${props => props.settings.hide_mobile === 'hidden-mobile' && `
    @media (max-width: 768px) { display: none; }
  `}
  
  /* Mobile */
  @media (max-width: 768px) {
    ${props => props.settings.align_mobile === 'center' && `margin: 0 auto;`}
  }
`;

const IconElement = styled.i<{ indent?: number }>`
  ${props => props.indent && `margin-right: ${props.indent}px;`}
`;

export const ButtonWidget: React.FC<ButtonWidgetProps> = ({ widget }) => {
  const settings = widget.settings as ButtonWidgetSettings;
  
  if (!settings.text) {
    return null;
  }
  
  const href = settings.link?.url || '#';
  const target = settings.link?.is_external ? '_blank' : '_self';
  
  return (
    <StyledButton 
      settings={settings}
      href={href}
      target={target}
    >
      {settings.selected_icon?.value && (
        <IconElement 
          className={settings.selected_icon.value}
          indent={settings.icon_indent?.size}
        />
      )}
      {settings.text}
    </StyledButton>
  );
};