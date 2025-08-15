import React from 'react';
import styled from 'styled-components';
import { ElementorElement, DividerWidgetSettings } from '../../../types/elementor';

interface DividerWidgetProps {
  widget: ElementorElement;
}

const StyledDivider = styled.hr<{ settings: DividerWidgetSettings }>`
  border: none;
  height: 1px;
  background-color: #333;
  margin: 20px 0;
  
  ${props => props.settings.gap && `
    margin-top: ${props.settings.gap.size}${props.settings.gap.unit};
    margin-bottom: ${props.settings.gap.size}${props.settings.gap.unit};
  `}
`;

export const DividerWidget: React.FC<DividerWidgetProps> = ({ widget }) => {
  const settings = widget.settings as DividerWidgetSettings;
  
  return <StyledDivider settings={settings} />;
};