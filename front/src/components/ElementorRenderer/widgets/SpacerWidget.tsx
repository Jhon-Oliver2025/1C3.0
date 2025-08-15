import React from 'react';
import styled from 'styled-components';
import { ElementorElement, SpacerWidgetSettings } from '../../../types/elementor';

interface SpacerWidgetProps {
  widget: ElementorElement;
}

const StyledSpacer = styled.div<{ settings: SpacerWidgetSettings }>`
  ${props => props.settings.space && `
    height: ${props.settings.space.size}${props.settings.space.unit};
  `}
  
  ${props => props.settings._margin && `
    margin: ${props.settings._margin.top}${props.settings._margin.unit} 
            ${props.settings._margin.right}${props.settings._margin.unit} 
            ${props.settings._margin.bottom}${props.settings._margin.unit} 
            ${props.settings._margin.left}${props.settings._margin.unit};
  `}
`;

export const SpacerWidget: React.FC<SpacerWidgetProps> = ({ widget }) => {
  const settings = widget.settings as SpacerWidgetSettings;
  
  return <StyledSpacer settings={settings} />;
};