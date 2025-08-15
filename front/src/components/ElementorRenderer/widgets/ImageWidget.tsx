import React from 'react';
import styled from 'styled-components';
import { ElementorElement, ImageWidgetSettings } from '../../../types/elementor';

/**
 * Widget de Imagem do Elementor
 * Suporta links, captions, hover effects e responsividade
 */

interface ImageWidgetProps {
  widget: ElementorElement;
}

const ImageContainer = styled.div<{ settings: ImageWidgetSettings }>`
  display: inline-block;
  position: relative;
  
  /* Alinhamento */
  ${props => props.settings.align === 'center' && `
    text-align: center;
    margin-left: auto;
    margin-right: auto;
  `}
  
  ${props => props.settings.align === 'left' && `
    text-align: left;
  `}
  
  ${props => props.settings.align === 'right' && `
    text-align: right;
    margin-left: auto;
  `}
  
  /* Width */
  ${props => props.settings.width && `
    width: ${props.settings.width.size}${props.settings.width.unit};
  `}
  
  /* Height */
  ${props => props.settings.height && `
    height: ${props.settings.height.size}${props.settings.height.unit};
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
  
  /* Hover animation */
  ${props => props.settings.hover_animation === 'float' && `
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
    }
  `}
  
  /* Mouse track effect */
  ${props => props.settings.motion_fx_mouseTrack_effect === 'yes' && `
    transition: transform 0.1s ease;
  `}
  
  /* Responsividade - Tablet */
  @media (max-width: 1024px) {
    /* Width tablet */
    ${props => props.settings.width_tablet && `
      width: ${props.settings.width_tablet.size}${props.settings.width_tablet.unit};
    `}
    
    /* Height tablet */
    ${props => props.settings.height_tablet && `
      height: ${props.settings.height_tablet.size}${props.settings.height_tablet.unit};
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
    /* Alinhamento mobile */
    ${props => props.settings.align_mobile === 'center' && `
      text-align: center;
      margin-left: auto;
      margin-right: auto;
    `}
    
    ${props => props.settings.align_mobile === 'left' && `
      text-align: left;
      margin-left: 0;
      margin-right: auto;
    `}
    
    ${props => props.settings.align_mobile === 'right' && `
      text-align: right;
      margin-left: auto;
      margin-right: 0;
    `}
    
    /* Width mobile */
    ${props => props.settings.width_mobile && `
      width: ${props.settings.width_mobile.size}${props.settings.width_mobile.unit};
    `}
    
    /* Height mobile */
    ${props => props.settings.height_mobile && `
      height: ${props.settings.height_mobile.size}${props.settings.height_mobile.unit};
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

const StyledImage = styled.img<{ settings: ImageWidgetSettings }>`
  max-width: 100%;
  height: auto;
  display: block;
  
  /* Border radius */
  ${props => props.settings.image_border_radius && `
    border-radius: ${props.settings.image_border_radius.top}${props.settings.image_border_radius.unit} 
                   ${props.settings.image_border_radius.right}${props.settings.image_border_radius.unit} 
                   ${props.settings.image_border_radius.bottom}${props.settings.image_border_radius.unit} 
                   ${props.settings.image_border_radius.left}${props.settings.image_border_radius.unit};
  `}
  
  /* Box shadow */
  ${props => props.settings.image_box_shadow_box_shadow_type === 'yes' && props.settings.image_box_shadow_box_shadow && `
    box-shadow: ${props.settings.image_box_shadow_box_shadow.horizontal}px 
                ${props.settings.image_box_shadow_box_shadow.vertical}px 
                ${props.settings.image_box_shadow_box_shadow.blur}px 
                ${props.settings.image_box_shadow_box_shadow.spread}px 
                ${props.settings.image_box_shadow_box_shadow.color};
  `}
  
  /* Responsividade - Tablet */
  @media (max-width: 1024px) {
    /* Border radius tablet */
    ${props => props.settings.image_border_radius_tablet && `
      border-radius: ${props.settings.image_border_radius_tablet.top}${props.settings.image_border_radius_tablet.unit} 
                     ${props.settings.image_border_radius_tablet.right}${props.settings.image_border_radius_tablet.unit} 
                     ${props.settings.image_border_radius_tablet.bottom}${props.settings.image_border_radius_tablet.unit} 
                     ${props.settings.image_border_radius_tablet.left}${props.settings.image_border_radius_tablet.unit};
    `}
  }
  
  /* Responsividade - Mobile */
  @media (max-width: 768px) {
    /* Border radius mobile */
    ${props => props.settings.image_border_radius_mobile && `
      border-radius: ${props.settings.image_border_radius_mobile.top}${props.settings.image_border_radius_mobile.unit} 
                     ${props.settings.image_border_radius_mobile.right}${props.settings.image_border_radius_mobile.unit} 
                     ${props.settings.image_border_radius_mobile.bottom}${props.settings.image_border_radius_mobile.unit} 
                     ${props.settings.image_border_radius_mobile.left}${props.settings.image_border_radius_mobile.unit};
    `}
  }
`;

const ImageCaption = styled.div<{ settings: ImageWidgetSettings }>`
  /* Alinhamento */
  ${props => props.settings.caption_align === 'center' && `
    text-align: center;
  `}
  
  ${props => props.settings.caption_align === 'left' && `
    text-align: left;
  `}
  
  ${props => props.settings.caption_align === 'right' && `
    text-align: right;
  `}
  
  /* Cor do texto */
  ${props => props.settings.text_color && `
    color: ${props.settings.text_color};
  `}
  
  /* Background */
  ${props => props.settings.caption_background_color && `
    background-color: ${props.settings.caption_background_color};
  `}
  
  /* Typography */
  ${props => props.settings.caption_typography_font_family && `
    font-family: ${props.settings.caption_typography_font_family};
  `}
  
  ${props => props.settings.caption_typography_font_size && `
    font-size: ${props.settings.caption_typography_font_size.size}${props.settings.caption_typography_font_size.unit};
  `}
  
  ${props => props.settings.caption_typography_font_weight && `
    font-weight: ${props.settings.caption_typography_font_weight};
  `}
  
  ${props => props.settings.caption_typography_line_height && `
    line-height: ${props.settings.caption_typography_line_height.size}${props.settings.caption_typography_line_height.unit};
  `}
  
  ${props => props.settings.caption_typography_word_spacing && `
    word-spacing: ${props.settings.caption_typography_word_spacing.size}${props.settings.caption_typography_word_spacing.unit};
  `}
  
  /* Spacing */
  ${props => props.settings.caption_space && `
    margin-top: ${props.settings.caption_space.size}${props.settings.caption_space.unit};
  `}
  
  /* Responsividade - Mobile */
  @media (max-width: 768px) {
    /* Font size mobile */
    ${props => props.settings.caption_typography_font_size_mobile && `
      font-size: ${props.settings.caption_typography_font_size_mobile.size}${props.settings.caption_typography_font_size_mobile.unit};
    `}
    
    /* Spacing mobile */
    ${props => props.settings.caption_space_mobile && `
      margin-top: ${props.settings.caption_space_mobile.size}${props.settings.caption_space_mobile.unit};
    `}
  }
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

export const ImageWidget: React.FC<ImageWidgetProps> = ({ widget }) => {
  const settings = widget.settings as ImageWidgetSettings;
  
  if (!settings.image?.url) {
    return null;
  }
  
  const imageElement = (
    <StyledImage
      settings={settings}
      src={settings.image.url}
      alt={settings.image.alt || settings.caption || ''}
      loading="lazy"
    />
  );
  
  const captionElement = settings.caption && settings.caption_source === 'custom' ? (
    <ImageCaption settings={settings}>
      {settings.caption}
    </ImageCaption>
  ) : null;
  
  const content = (
    <>
      {imageElement}
      {captionElement}
    </>
  );
  
  // Se tem link, envolver em <a>
  if (settings.link_to === 'custom' && settings.link?.url) {
    return (
      <ImageContainer settings={settings}>
        <a
          href={settings.link.url}
          target={getLinkTarget(settings.link.is_external)}
          rel={getLinkRel(settings.link.is_external, settings.link.nofollow)}
          style={{ textDecoration: 'none', color: 'inherit' }}
        >
          {content}
        </a>
      </ImageContainer>
    );
  }
  
  return (
    <ImageContainer settings={settings}>
      {content}
    </ImageContainer>
  );
};