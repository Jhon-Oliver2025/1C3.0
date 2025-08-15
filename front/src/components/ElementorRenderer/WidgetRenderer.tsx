import React from 'react';
import { ElementorElement } from '../../types/elementor';
import { ImageWidget } from './widgets/ImageWidget';
import { HeadingWidget } from './widgets/HeadingWidget';
import { TextEditorWidget } from './widgets/TextEditorWidget';
import { ButtonWidget } from './widgets/ButtonWidget';
import { IconListWidget } from './widgets/IconListWidget';
import { DividerWidget } from './widgets/DividerWidget';
import { VideoPlaylistWidget } from './widgets/VideoPlaylistWidget';
import { SpacerWidget } from './widgets/SpacerWidget';

/**
 * Componente principal para renderizar widgets do Elementor
 * Faz o roteamento para o componente específico baseado no widgetType
 */

interface WidgetRendererProps {
  widget: ElementorElement;
}

export const WidgetRenderer: React.FC<WidgetRendererProps> = ({ widget }) => {
  const { widgetType } = widget;
  
  // Roteamento para o componente específico do widget
  switch (widgetType) {
    case 'image':
      return <ImageWidget widget={widget} />;
      
    case 'heading':
      return <HeadingWidget widget={widget} />;
      
    case 'text-editor':
      return <TextEditorWidget widget={widget} />;
      
    case 'button':
      return <ButtonWidget widget={widget} />;
      
    case 'icon-list':
      return <IconListWidget widget={widget} />;
      
    case 'divider':
      return <DividerWidget widget={widget} />;
      
    case 'video-playlist':
      return <VideoPlaylistWidget widget={widget} />;
      
    case 'spacer':
      return <SpacerWidget widget={widget} />;
      
    default:
      // Widget não implementado - renderizar placeholder
      console.warn(`Widget type "${widgetType}" not implemented yet`);
      return (
        <div 
          style={{
            padding: '10px',
            border: '1px dashed #ccc',
            borderRadius: '4px',
            margin: '5px 0',
            backgroundColor: '#f9f9f9',
            color: '#666',
            fontSize: '12px',
            textAlign: 'center'
          }}
        >
          Widget "{widgetType}" não implementado
        </div>
      );
  }
};