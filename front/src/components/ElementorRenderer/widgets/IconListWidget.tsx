import React from 'react';
import styled from 'styled-components';
import { ElementorElement, IconListWidgetSettings } from '../../../types/elementor';

/**
 * Widget de Lista de Ícones do Elementor
 * Usado para navegação e listas com links
 */

interface IconListWidgetProps {
  widget: ElementorElement;
}

const IconListContainer = styled.div<{ settings: IconListWidgetSettings }>`
  /* View inline */
  ${props => props.settings.view === 'inline' && `
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
  `}
  
  /* View vertical (padrão) */
  ${props => props.settings.view !== 'inline' && `
    display: flex;
    flex-direction: column;
    gap: 10px;
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
  
  /* Z-index */
  ${props => props.settings._z_index && `
    z-index: ${props.settings._z_index};
  `}
  
  /* Responsividade - Mobile */
  @media (max-width: 768px) {
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

const IconListItem = styled.a<{ settings: IconListWidgetSettings }>`
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: all 0.3s ease;
  
  /* Cor do texto */
  ${props => props.settings.text_color && `
    color: ${props.settings.text_color};
  `}
  
  /* Typography */
  ${props => props.settings.icon_typography_font_family && `
    font-family: ${props.settings.icon_typography_font_family};
  `}
  
  ${props => props.settings.icon_typography_font_size && `
    font-size: ${props.settings.icon_typography_font_size.size}${props.settings.icon_typography_font_size.unit};
  `}
  
  ${props => props.settings.icon_typography_font_weight && `
    font-weight: ${props.settings.icon_typography_font_weight};
  `}
  
  ${props => props.settings.icon_typography_line_height && `
    line-height: ${props.settings.icon_typography_line_height.size}${props.settings.icon_typography_line_height.unit};
  `}
  
  &:hover {
    opacity: 0.8;
    transform: translateY(-1px);
  }
  
  &:visited {
    color: inherit;
  }
`;

const IconElement = styled.i`
  margin-right: 8px;
  font-size: inherit;
`;

/**
 * Determina se o link deve abrir em nova aba
 */
const getLinkTarget = (isExternal: string | boolean | undefined): string => {
  if (isExternal === 'on' || isExternal === true) {
    return '_blank';
  }
  return '_self';
};

/**
 * Determina o rel do link
 */
const getLinkRel = (isExternal: string | boolean | undefined, nofollow: string | boolean | undefined): string => {
  const rels = [];
  
  if (isExternal === 'on' || isExternal === true) {
    rels.push('noopener', 'noreferrer');
  }
  
  if (nofollow === 'on' || nofollow === true) {
    rels.push('nofollow');
  }
  
  return rels.join(' ');
};

/**
 * Renderiza o ícone se disponível
 */
const renderIcon = (iconValue: string) => {
  if (!iconValue) return null;
  
  // Font Awesome icons
  if (iconValue.startsWith('fas ') || iconValue.startsWith('far ') || iconValue.startsWith('fab ')) {
    return <IconElement className={iconValue} />;
  }
  
  return null;
};

export const IconListWidget: React.FC<IconListWidgetProps> = ({ widget }) => {
  const settings = widget.settings as IconListWidgetSettings;
  
  if (!settings.icon_list || settings.icon_list.length === 0) {
    return null;
  }
  
  return (
    <IconListContainer settings={settings}>
      {settings.icon_list.map((item) => {
        const href = item.link?.url || '#';
        const target = getLinkTarget(item.link?.is_external);
        const rel = getLinkRel(item.link?.is_external, item.link?.nofollow);
        
        return (
          <IconListItem
            key={item._id}
            href={href}
            target={target}
            rel={rel}
            settings={settings}
          >
            {renderIcon(item.selected_icon?.value || '')}
            <span>{item.text}</span>
          </IconListItem>
        );
      })}
    </IconListContainer>
  );
};