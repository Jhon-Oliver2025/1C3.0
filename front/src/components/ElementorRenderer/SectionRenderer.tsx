import React from 'react';
import styled from 'styled-components';
import { ElementorElement, SectionSettings } from '../../types/elementor';
import { ColumnRenderer } from './ColumnRenderer';

/**
 * Componente para renderizar seções do Elementor
 * Converte settings do Elementor em styled-components
 */

interface SectionRendererProps {
  section: ElementorElement;
}

const StyledSection = styled.section<{ settings: SectionSettings }>`
  /* Layout básico */
  width: 100%;
  position: relative;
  
  /* Content width */
  ${props => props.settings.content_width && `
    max-width: ${props.settings.content_width.size}${props.settings.content_width.unit};
    margin-left: auto;
    margin-right: auto;
  `}
  
  /* Layout full width */
  ${props => props.settings.layout === 'full_width' && `
    max-width: 100%;
    width: 100%;
  `}
  
  /* Background */
  ${props => props.settings.background_background === 'classic' && props.settings.background_color && `
    background-color: ${props.settings.background_color};
  `}
  
  ${props => props.settings.background_background === 'gradient' && `
    background: linear-gradient(
      to bottom,
      ${props.settings.background_color || '#000000'} 0%,
      ${props.settings.background_color_b || '#262626'} 100%
    );
  `}
  
  ${props => props.settings.background_image && `
    background-image: url('${props.settings.background_image.url}');
    background-size: ${props.settings.background_size || 'cover'};
    background-repeat: ${props.settings.background_repeat || 'no-repeat'};
    background-position: ${props.settings.background_xpos?.size || 0}% ${props.settings.background_ypos?.size || 0}%;
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
  
  /* Gap entre colunas */
  ${props => props.settings.gap === 'no' && `
    .elementor-row {
      gap: 0;
    }
  `}
  
  ${props => props.settings.gap === 'narrow' && `
    .elementor-row {
      gap: 10px;
    }
  `}
  
  /* Responsividade - Tablet */
  @media (max-width: 1024px) {
    /* Hide on tablet */
    ${props => props.settings.hide_tablet === 'hidden-tablet' && `
      display: none;
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
    
    /* Background position mobile */
    ${props => props.settings.background_position_mobile && `
      background-position: ${props.settings.background_position_mobile};
    `}
  }
  
  /* Hide on desktop */
  ${props => props.settings.hide_desktop === 'hidden-desktop' && `
    @media (min-width: 1025px) {
      display: none;
    }
  `}
`;

const ElementorRow = styled.div<{ settings: SectionSettings }>`
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  
  /* Gap baseado na estrutura */
  ${props => props.settings.gap === 'narrow' && `
    gap: 10px;
  `}
  
  ${props => props.settings.gap === 'no' && `
    gap: 0;
  `}
  
  /* Mobile: stack columns */
  @media (max-width: 768px) {
    flex-direction: column;
    
    ${props => props.settings.gap_columns_custom_mobile && `
      gap: ${props.settings.gap_columns_custom_mobile.size}${props.settings.gap_columns_custom_mobile.unit};
    `}
  }
`;

const VideoBackground = styled.video`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -2;
`;

const BackgroundOverlay = styled.div<{ settings: SectionSettings }>`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  
  ${props => props.settings.background_overlay_background === 'gradient' && `
    background: linear-gradient(
      to bottom,
      ${props.settings.background_overlay_color || '#00000000'} ${props.settings.background_overlay_color_stop?.size || 50}%,
      ${props.settings.background_overlay_color_b || '#141414'} 100%
    );
    opacity: ${props.settings.background_overlay_opacity?.size || 1};
  `}
`;

/**
 * Extrai o ID do vídeo do YouTube da URL
 */
const getYouTubeVideoId = (url: string): string | null => {
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
  return match ? match[1] : null;
};

export const SectionRenderer: React.FC<SectionRendererProps> = ({ section }) => {
  const settings = section.settings as SectionSettings;
  
  // Renderizar vídeo de fundo se configurado
  const renderVideoBackground = () => {
    if (settings.background_background === 'video' && settings.background_video_link) {
      const videoId = getYouTubeVideoId(settings.background_video_link);
      if (videoId) {
        return (
          <VideoBackground
            autoPlay
            muted
            loop
            playsInline
            poster={settings.background_image?.url}
          >
            <source 
              src={`https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&loop=1&controls=0&showinfo=0&rel=0&iv_load_policy=3&modestbranding=1`} 
              type="video/mp4" 
            />
          </VideoBackground>
        );
      }
    }
    return null;
  };
  
  // Renderizar overlay de fundo
  const renderBackgroundOverlay = () => {
    if (settings.background_overlay_background) {
      return <BackgroundOverlay settings={settings} />;
    }
    return null;
  };
  
  return (
    <StyledSection settings={settings}>
      {renderVideoBackground()}
      {renderBackgroundOverlay()}
      
      <ElementorRow settings={settings} className="elementor-row">
        {section.elements.map((element) => (
          <ColumnRenderer key={element.id} column={element} />
        ))}
      </ElementorRow>
    </StyledSection>
  );
};