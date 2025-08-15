/**
 * Exportações do sistema ElementorRenderer
 * Sistema completo para renderizar páginas exportadas do WordPress/Elementor em React
 */

// Componente principal
export { PageRenderer, useElementorPage } from './PageRenderer';

// Componentes de estrutura
export { SectionRenderer } from './SectionRenderer';
export { ColumnRenderer } from './ColumnRenderer';
export { WidgetRenderer } from './WidgetRenderer';

// Widgets individuais
export { ImageWidget } from './widgets/ImageWidget';
export { HeadingWidget } from './widgets/HeadingWidget';
export { TextEditorWidget } from './widgets/TextEditorWidget';
export { ButtonWidget } from './widgets/ButtonWidget';
export { IconListWidget } from './widgets/IconListWidget';
export { DividerWidget } from './widgets/DividerWidget';
export { VideoPlaylistWidget } from './widgets/VideoPlaylistWidget';
export { SpacerWidget } from './widgets/SpacerWidget';

// Tipos
export type {
  ElementorPage,
  ElementorElement,
  SectionSettings,
  ColumnSettings,
  WidgetSettings,
  ImageWidgetSettings,
  HeadingWidgetSettings,
  TextEditorWidgetSettings,
  ButtonWidgetSettings,
  IconListWidgetSettings,
  DividerWidgetSettings,
  VideoPlaylistWidgetSettings,
  SpacerWidgetSettings,
  VideoTab,
  IconListItem,
  ImageData,
  LinkData,
  UnitValue,
  SpacingValue,
  BoxShadow,
  BorderRadius,
  TypographySettings
} from '../../types/elementor';