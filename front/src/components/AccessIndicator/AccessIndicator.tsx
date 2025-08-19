import React from 'react';
import styled from 'styled-components';
import { Lock, Unlock } from 'lucide-react';

// Styled Components
const IndicatorContainer = styled.div<{ $hasAccess: boolean }>`
  position: absolute;
  top: 15px;
  right: 15px;
  background: ${props => props.$hasAccess 
    ? 'rgba(76, 175, 80, 0.9)' 
    : 'rgba(244, 67, 54, 0.9)'};
  border: 2px solid ${props => props.$hasAccess 
    ? '#4caf50' 
    : '#f44336'};
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  z-index: 10;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
  }
  
  svg {
    color: white;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
  }
`;

const Tooltip = styled.div<{ $visible: boolean }>`
  position: absolute;
  top: 60px;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: nowrap;
  opacity: ${props => props.$visible ? 1 : 0};
  visibility: ${props => props.$visible ? 'visible' : 'hidden'};
  transition: all 0.3s ease;
  z-index: 11;
  
  &::before {
    content: '';
    position: absolute;
    top: -5px;
    right: 15px;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid rgba(0, 0, 0, 0.9);
  }
`;

// Interface
interface AccessIndicatorProps {
  hasAccess: boolean;
  isAdmin?: boolean;
  courseName?: string;
  className?: string;
}

/**
 * Componente indicador visual de acesso ao curso
 * Mostra um cadeado aberto (verde) se tem acesso ou fechado (vermelho) se não tem
 */
const AccessIndicator: React.FC<AccessIndicatorProps> = ({
  hasAccess,
  isAdmin = false,
  courseName,
  className
}) => {
  const [showTooltip, setShowTooltip] = React.useState(false);
  
  const getTooltipText = () => {
    if (isAdmin) {
      return 'Acesso de Administrador';
    }
    if (hasAccess) {
      return courseName ? `Acesso liberado: ${courseName}` : 'Acesso liberado';
    }
    return courseName ? `Acesso restrito: ${courseName}` : 'Acesso restrito';
  };
  
  return (
    <IndicatorContainer
      $hasAccess={hasAccess || isAdmin}
      className={className}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {hasAccess || isAdmin ? (
        <Unlock size={24} />
      ) : (
        <Lock size={24} />
      )}
      
      <Tooltip $visible={showTooltip}>
        {getTooltipText()}
      </Tooltip>
    </IndicatorContainer>
  );
};

export default AccessIndicator;