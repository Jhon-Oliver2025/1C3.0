/**
 * Tipos TypeScript para estrutura do Elementor
 * Define interfaces para renderização de páginas exportadas do WordPress/Elementor
 */

// Tipos base para unidades e valores responsivos
export interface ResponsiveValue<T = any> {
  desktop?: T;
  tablet?: T;
  mobile?: T;
}

export interface UnitValue {
  unit: 'px' | '%' | 'em' | 'rem' | 'vh' | 'vw';
  size: number;
  sizes?: number[];
}

export interface SpacingValue {
  unit: 'px' | '%' | 'em' | 'rem';
  top: string | number;
  right: string | number;
  bottom: string | number;
  left: string | number;
  isLinked: boolean;
}

export interface BoxShadow {
  horizontal: number;
  vertical: number;
  blur: number;
  spread: number;
  color: string;
}

export interface BorderRadius {
  unit: 'px' | '%';
  top: string | number;
  right: string | number;
  bottom: string | number;
  left: string | number;
  isLinked: boolean;
}

export interface ImageData {
  id: string | number;
  url: string;
  alt?: string;
  source?: string;
}

export interface LinkData {
  url: string;
  is_external?: string | boolean;
  nofollow?: string | boolean;
  custom_attributes?: string;
}

export interface TypographySettings {
  typography_typography?: string;
  typography_font_family?: string;
  typography_font_size?: UnitValue;
  typography_font_size_tablet?: UnitValue;
  typography_font_size_mobile?: UnitValue;
  typography_font_weight?: string | number;
  typography_line_height?: UnitValue;
  typography_letter_spacing?: UnitValue;
  typography_word_spacing?: UnitValue;
}

// Settings específicos para cada tipo de widget
export interface ImageWidgetSettings {
  image: ImageData;
  image_size?: string;
  align?: string;
  align_mobile?: string;
  align_tablet?: string;
  link_to?: string;
  link?: LinkData;
  width?: UnitValue;
  width_mobile?: UnitValue;
  width_tablet?: UnitValue;
  height?: UnitValue;
  height_mobile?: UnitValue;
  height_tablet?: UnitValue;
  image_border_radius?: BorderRadius;
  image_border_radius_mobile?: BorderRadius;
  image_border_radius_tablet?: BorderRadius;
  image_box_shadow_box_shadow_type?: string;
  image_box_shadow_box_shadow?: BoxShadow;
  hover_animation?: string;
  caption_source?: string;
  caption?: string;
  caption_align?: string;
  caption_typography_typography?: string;
  caption_typography_font_family?: string;
  caption_typography_font_size?: UnitValue;
  caption_typography_font_size_mobile?: UnitValue;
  caption_typography_font_weight?: string;
  caption_typography_line_height?: UnitValue;
  caption_typography_word_spacing?: UnitValue;
  caption_background_color?: string;
  caption_space?: UnitValue;
  caption_space_mobile?: UnitValue;
  text_color?: string;
  motion_fx_mouseTrack_effect?: string;
  _animation?: string;
  _margin?: SpacingValue;
  _margin_mobile?: SpacingValue;
  _margin_tablet?: SpacingValue;
  _padding?: SpacingValue;
  _padding_mobile?: SpacingValue;
  _padding_tablet?: SpacingValue;
  _z_index?: number;
}

export interface HeadingWidgetSettings extends TypographySettings {
  title: string;
  title_color?: string;
  align?: string;
  align_mobile?: string;
  align_tablet?: string;
  text_shadow_text_shadow_type?: string;
  text_shadow_text_shadow?: {
    horizontal: number;
    vertical: number;
    blur: number;
    color: string;
  };
  _margin?: SpacingValue;
  _margin_mobile?: SpacingValue;
  _margin_tablet?: SpacingValue;
  _padding?: SpacingValue;
  _padding_mobile?: SpacingValue;
  _padding_tablet?: SpacingValue;
}

export interface TextEditorWidgetSettings extends TypographySettings {
  editor: string;
  align?: string;
  align_mobile?: string;
  align_tablet?: string;
  text_color?: string;
  _margin?: SpacingValue;
  _margin_mobile?: SpacingValue;
  _margin_tablet?: SpacingValue;
  _padding?: SpacingValue;
  _padding_mobile?: SpacingValue;
  _padding_tablet?: SpacingValue;
}

export interface ButtonWidgetSettings extends TypographySettings {
  text: string;
  link?: LinkData;
  align?: string;
  align_mobile?: string;
  align_tablet?: string;
  selected_icon?: {
    value: string;
    library: string;
  };
  icon_indent?: UnitValue;
  text_shadow_text_shadow_type?: string;
  button_text_color?: string;
  background_color?: string;
  button_background_hover_color?: string;
  border_radius?: BorderRadius;
  hide_desktop?: string;
  hide_tablet?: string;
  hide_mobile?: string;
}

export interface IconListItem {
  text: string;
  selected_icon?: {
    value: string;
    library: string;
  };
  _id: string;
  link?: LinkData;
}

export interface IconListWidgetSettings extends TypographySettings {
  view?: string;
  icon_list: IconListItem[];
  text_color?: string;
  icon_typography_typography?: string;
  icon_typography_font_family?: string;
  icon_typography_font_size?: UnitValue;
  icon_typography_font_weight?: string;
  icon_typography_line_height?: UnitValue;
  _margin?: SpacingValue;
  _margin_mobile?: SpacingValue;
  _margin_tablet?: SpacingValue;
  _padding?: SpacingValue;
  _padding_mobile?: SpacingValue;
  _padding_tablet?: SpacingValue;
  _z_index?: number;
}

export interface DividerWidgetSettings {
  text?: string;
  gap?: UnitValue;
  __globals__?: {
    color?: string;
  };
}

export interface VideoTab {
  title: string;
  youtube_url?: string;
  vimeo_url?: string;
  duration?: string;
  thumbnail?: ImageData;
  _id: string;
}

export interface VideoPlaylistWidgetSettings {
  playlist_title?: string;
  tabs: VideoTab[];
  inner_tab_title_1?: string;
  inner_tab_title_2?: string;
  inner_tab_label_show_more?: string;
  inner_tab_label_show_less?: string;
  _margin_mobile?: SpacingValue;
  _padding_mobile?: SpacingValue;
  _background_background?: string;
  section_color?: string;
  _border_radius?: BorderRadius;
  _box_shadow_box_shadow_type?: string;
  _box_shadow_box_shadow?: BoxShadow;
  image_overlay?: ImageData;
}

export interface SpacerWidgetSettings {
  space?: UnitValue;
  _margin?: SpacingValue;
  _margin_mobile?: SpacingValue;
  _margin_tablet?: SpacingValue;
  _padding?: SpacingValue;
  _padding_mobile?: SpacingValue;
  _padding_tablet?: SpacingValue;
}

// Union type para todos os settings de widgets
export type WidgetSettings = 
  | ImageWidgetSettings 
  | HeadingWidgetSettings 
  | TextEditorWidgetSettings 
  | ButtonWidgetSettings 
  | IconListWidgetSettings 
  | DividerWidgetSettings 
  | VideoPlaylistWidgetSettings 
  | SpacerWidgetSettings;

// Tipos para elementos e estrutura
export interface ElementorWidget {
  id: string;
  settings: WidgetSettings;
  elements: ElementorWidget[];
  isInner: boolean;
  widgetType?: string;
  elType: 'widget' | 'column' | 'section';
}

export interface ColumnSettings {
  _column_size: number;
  _inline_size?: number | null;
  _inline_size_tablet?: number;
  _inline_size_mobile?: number;
  content_position?: string;
  content_position_tablet?: string;
  content_position_mobile?: string;
  margin?: SpacingValue;
  margin_mobile?: SpacingValue;
  margin_tablet?: SpacingValue;
  padding?: SpacingValue;
  padding_mobile?: SpacingValue;
  padding_tablet?: SpacingValue;
  z_index?: number;
  hide_desktop?: string;
  hide_tablet?: string;
  hide_mobile?: string;
}

export interface SectionSettings {
  content_width?: UnitValue;
  structure?: string;
  layout?: string;
  gap?: string;
  gap_columns_custom_mobile?: UnitValue;
  custom_height_inner_mobile?: UnitValue;
  content_position?: string;
  background_background?: string;
  background_color?: string;
  background_color_b?: string;
  background_image?: ImageData;
  background_video_link?: string;
  background_play_on_mobile?: string;
  background_overlay_background?: string;
  background_overlay_color?: string;
  background_overlay_color_stop?: UnitValue;
  background_overlay_color_b?: string;
  background_overlay_opacity?: UnitValue;
  background_overlay_size?: string;
  background_xpos?: UnitValue;
  background_ypos?: UnitValue;
  background_repeat?: string;
  background_size?: string;
  background_position_mobile?: string;
  margin?: SpacingValue;
  margin_mobile?: SpacingValue;
  margin_tablet?: SpacingValue;
  padding?: SpacingValue;
  padding_mobile?: SpacingValue;
  padding_tablet?: SpacingValue;
  hide_desktop?: string;
  hide_tablet?: string;
  hide_mobile?: string;
  background_hover_transition?: UnitValue;
}

export interface ElementorElement {
  id: string;
  settings: SectionSettings | ColumnSettings | WidgetSettings;
  elements: ElementorElement[];
  isInner: boolean;
  elType: 'section' | 'column' | 'widget';
  widgetType?: string;
}

export interface PageSettings {
  hide_title?: string;
  background_background?: string;
  background_color?: string;
  ha_grid_number?: string;
  ha_grid_zindex?: string;
}

export interface ElementorPage {
  content: ElementorElement[];
  page_settings: PageSettings;
  version: string;
  title: string;
  type: string;
}