import React, { useState } from 'react';
import styled from 'styled-components';
import { ElementorElement, VideoPlaylistWidgetSettings } from '../../../types/elementor';

/**
 * Widget de Playlist de Vídeos do Elementor
 * Componente customizado para reprodução de vídeos do YouTube/Vimeo
 */

interface VideoPlaylistWidgetProps {
  widget: ElementorElement;
}

const PlaylistContainer = styled.div<{ settings: VideoPlaylistWidgetSettings }>`
  display: flex;
  flex-direction: column;
  background-color: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  
  ${props => props.settings._border_radius && `
    border-radius: ${props.settings._border_radius.top}${props.settings._border_radius.unit};
  `}
  
  ${props => props.settings._box_shadow_box_shadow_type === 'yes' && props.settings._box_shadow_box_shadow && `
    box-shadow: ${props.settings._box_shadow_box_shadow.horizontal}px 
                ${props.settings._box_shadow_box_shadow.vertical}px 
                ${props.settings._box_shadow_box_shadow.blur}px 
                ${props.settings._box_shadow_box_shadow.spread}px 
                ${props.settings._box_shadow_box_shadow.color};
  `}
  
  ${props => props.settings.section_color && `
    background-color: ${props.settings.section_color};
  `}
  
  @media (max-width: 768px) {
    ${props => props.settings._margin_mobile && `
      margin: ${props.settings._margin_mobile.top}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.right}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.bottom}${props.settings._margin_mobile.unit} 
              ${props.settings._margin_mobile.left}${props.settings._margin_mobile.unit};
    `}
  }
`;

const PlaylistHeader = styled.div`
  padding: 20px;
  background-color: #2a2a2a;
  border-bottom: 1px solid #333;
`;

const PlaylistTitle = styled.h3`
  color: #ffffff;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
`;

const VideoPlayer = styled.div`
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  background-color: #000;
  
  iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
  }
`;

const PlaylistTabs = styled.div`
  display: flex;
  flex-direction: column;
  max-height: 400px;
  overflow-y: auto;
`;

const TabItem = styled.div<{ isActive: boolean }>`
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  border-bottom: 1px solid #333;
  transition: all 0.3s ease;
  
  ${props => props.isActive ? `
    background-color: #333;
    border-left: 3px solid #ff6b35;
  ` : `
    background-color: transparent;
    
    &:hover {
      background-color: #2a2a2a;
    }
  `}
`;

const TabThumbnail = styled.img`
  width: 60px;
  height: 45px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 15px;
`;

const TabContent = styled.div`
  flex: 1;
`;

const TabTitle = styled.div`
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
`;

const TabDuration = styled.div`
  color: #999;
  font-size: 12px;
`;

/**
 * Extrai o ID do vídeo do YouTube da URL
 */
const getYouTubeVideoId = (url: string): string | null => {
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
  return match ? match[1] : null;
};

/**
 * Extrai o ID do vídeo do Vimeo da URL
 */
const getVimeoVideoId = (url: string): string | null => {
  const match = url.match(/vimeo\.com\/(\d+)/);
  return match ? match[1] : null;
};

/**
 * Gera a URL do embed baseada na plataforma
 */
const getEmbedUrl = (youtubeUrl?: string, vimeoUrl?: string): string | null => {
  // Se for uma URL do YouTube, retorna null para não renderizar
  if (youtubeUrl) {
    return null;
  }
  
  if (vimeoUrl) {
    const videoId = getVimeoVideoId(vimeoUrl);
    if (videoId) {
      return `https://player.vimeo.com/video/${videoId}?autoplay=1`;
    }
  }
  
  return null;
};

/**
 * Gera a URL da thumbnail do YouTube
 */
const getYouTubeThumbnail = (url: string): string | null => {
  const videoId = getYouTubeVideoId(url);
  if (videoId) {
    return `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
  }
  return null;
};

export const VideoPlaylistWidget: React.FC<VideoPlaylistWidgetProps> = ({ widget }) => {
  const settings = widget.settings as VideoPlaylistWidgetSettings;
  const [activeTabIndex, setActiveTabIndex] = useState(0);
  
  if (!settings.tabs || settings.tabs.length === 0) {
    return null;
  }
  
  const activeTab = settings.tabs[activeTabIndex];
  const embedUrl = getEmbedUrl(activeTab.youtube_url, activeTab.vimeo_url);
  
  return (
    <PlaylistContainer settings={settings}>
      {settings.playlist_title && (
        <PlaylistHeader>
          <PlaylistTitle>{settings.playlist_title}</PlaylistTitle>
        </PlaylistHeader>
      )}
      
      {embedUrl && (
        <VideoPlayer>
          <iframe
            src={embedUrl}
            title={activeTab.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </VideoPlayer>
      )}
      
      <PlaylistTabs>
        {settings.tabs.map((tab, index) => {
          const thumbnailUrl = tab.thumbnail?.url || 
                              (tab.youtube_url ? getYouTubeThumbnail(tab.youtube_url) : null) ||
                              '/placeholder-video.jpg';
          
          return (
            <TabItem
              key={tab._id}
              isActive={index === activeTabIndex}
              onClick={() => setActiveTabIndex(index)}
            >
              <TabThumbnail
                src={thumbnailUrl}
                alt={tab.title}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/placeholder-video.jpg';
                }}
              />
              <TabContent>
                <TabTitle>{tab.title}</TabTitle>
                {tab.duration && (
                  <TabDuration>{tab.duration}</TabDuration>
                )}
              </TabContent>
            </TabItem>
          );
        })}
      </PlaylistTabs>
    </PlaylistContainer>
  );
};