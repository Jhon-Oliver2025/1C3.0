import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ShoppingCart, CreditCard, Lock, CheckCircle, AlertCircle } from 'lucide-react';

// Styled Components
const CheckoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 2rem;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    margin: 1rem;
    max-width: calc(100% - 2rem);
    border-radius: 12px;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
    gap: 1rem;
  }
`;

const CourseInfo = styled.div`
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  h3 {
    color: #ffffff;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
    margin: 0;
  }
`;

const PriceSection = styled.div`
  text-align: center;
  margin: 1rem 0;
  
  .original-price {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.6);
    text-decoration: line-through;
    margin-bottom: 0.5rem;
    
    @media (max-width: 480px) {
      font-size: 0.9rem;
    }
  }
  
  .current-price {
    font-size: 2.5rem;
    font-weight: bold;
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    
    @media (max-width: 768px) {
      font-size: 2.2rem;
    }
    
    @media (max-width: 480px) {
      font-size: 1.8rem;
    }
  }
  
  .installments {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
    
    @media (max-width: 480px) {
      font-size: 0.8rem;
      line-height: 1.4;
    }
  }
`;

const CheckoutButton = styled.button<{ $loading?: boolean; disabled?: boolean }>`
  background: ${props => props.disabled ? 
    'rgba(255, 255, 255, 0.1)' : 
    'linear-gradient(135deg, #2196f3 0%, #1976d2 50%, #00bcd4 100%)'
  };
  border: none;
  color: ${props => props.disabled ? 'rgba(255, 255, 255, 0.5)' : 'white'};
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: ${props => (props.$loading || props.disabled) ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
  width: 100%;
  min-height: 56px;
  
  @media (max-width: 768px) {
    padding: 1.2rem 1.5rem;
    font-size: 1rem;
    min-height: 60px;
  }
  
  @media (max-width: 480px) {
    padding: 1rem;
    font-size: 0.95rem;
    min-height: 52px;
    gap: 0.5rem;
  }
  
  &:hover {
    transform: ${props => (props.$loading || props.disabled) ? 'none' : 'translateY(-2px)'};
    box-shadow: ${props => (props.$loading || props.disabled) ? 'none' : '0 8px 25px rgba(33, 150, 243, 0.3)'};
  }
  
  /* Melhor área de toque em mobile */
  @media (max-width: 768px) {
    &:active {
      transform: ${props => (props.$loading || props.disabled) ? 'none' : 'scale(0.98)'};
    }
  }
`;

const SecurityBadge = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 8px;
  color: #4caf50;
  font-size: 0.9rem;
  font-weight: 500;
`;

const LoadingSpinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const StatusMessage = styled.div<{ type: 'success' | 'error' | 'info' }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: 8px;
  font-weight: 500;
  
  ${props => {
    switch (props.type) {
      case 'success':
        return `
          background: rgba(76, 175, 80, 0.1);
          border: 1px solid rgba(76, 175, 80, 0.3);
          color: #4caf50;
        `;
      case 'error':
        return `
          background: rgba(244, 67, 54, 0.1);
          border: 1px solid rgba(244, 67, 54, 0.3);
          color: #f44336;
        `;
      case 'info':
        return `
          background: rgba(33, 150, 243, 0.1);
          border: 1px solid rgba(33, 150, 243, 0.3);
          color: #2196f3;
        `;
    }
  }}
`;

// Interfaces
interface Course {
  name: string;
  description: string;
  price: number;
}

interface MercadoPagoCheckoutProps {
  courseId: string;
  course: Course;
  onSuccess?: (paymentData: any) => void;
  onError?: (error: string) => void;
  className?: string;
}

/**
 * Componente de checkout integrado com Mercado Pago
 * Gerencia todo o fluxo de pagamento desde a criação da preferência até a confirmação
 */
const MercadoPagoCheckout: React.FC<MercadoPagoCheckoutProps> = ({
  courseId,
  course,
  onSuccess,
  onError,
  className
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [hasAccess, setHasAccess] = useState(false);
  const [checkingAccess, setCheckingAccess] = useState(true);
  const [statusMessage, setStatusMessage] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);

  // Verificar se o usuário já tem acesso ao curso
  useEffect(() => {
    checkCourseAccess();
  }, [courseId]);

  /**
   * Verifica se o usuário já tem acesso ao curso
   */
  const checkCourseAccess = async () => {
    try {
      setCheckingAccess(true);
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        setCheckingAccess(false);
        return;
      }

      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/check-access/${courseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setHasAccess(data.has_access);
        
        if (data.has_access) {
          setStatusMessage({
            type: 'success',
            message: 'Você já tem acesso a este curso!'
          });
        }
      }
    } catch (error) {
      console.error('Erro ao verificar acesso:', error);
    } finally {
      setCheckingAccess(false);
    }
  };

  /**
   * Inicia o processo de checkout
   */
  const handleCheckout = async () => {
    try {
      setIsLoading(true);
      setStatusMessage(null);
      
      const token = localStorage.getItem('authToken');
      if (!token) {
        setStatusMessage({
          type: 'error',
          message: 'Você precisa estar logado para comprar um curso'
        });
        return;
      }

      // Criar preferência de pagamento
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/create-preference`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          course_id: courseId,
          success_url: `${window.location.origin}/payment/success`,
          failure_url: `${window.location.origin}/payment/failure`
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.success && data.preference) {
          // Redirecionar para o Mercado Pago
          window.location.href = data.preference.init_point;
        } else {
          throw new Error('Erro ao criar preferência de pagamento');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao processar pagamento');
      }
    } catch (error) {
      console.error('Erro no checkout:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      
      setStatusMessage({
        type: 'error',
        message: errorMessage
      });
      
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const installmentValue = course.price / 12;
  const discountPercentage = 0; // Pode ser calculado se houver desconto

  if (checkingAccess) {
    return (
      <CheckoutContainer className={className}>
        <StatusMessage type="info">
          <LoadingSpinner />
          Verificando acesso ao curso...
        </StatusMessage>
      </CheckoutContainer>
    );
  }

  return (
    <CheckoutContainer className={className}>
      <CourseInfo>
        <h3>{course.name}</h3>
        <p>{course.description}</p>
      </CourseInfo>

      <PriceSection>
        <div className="current-price">
          R$ {course.price.toFixed(2).replace('.', ',')}
          {discountPercentage > 0 && (
            <span style={{ 
              fontSize: '1rem', 
              color: '#4caf50', 
              marginLeft: '0.5rem',
              background: 'rgba(76, 175, 80, 0.2)',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px'
            }}>
              -{discountPercentage}%
            </span>
          )}
        </div>
        
        <div className="installments">
          ou 12x de R$ {installmentValue.toFixed(2).replace('.', ',')} sem juros
        </div>
      </PriceSection>

      {statusMessage && (
        <StatusMessage type={statusMessage.type}>
          {statusMessage.type === 'success' && <CheckCircle size={20} />}
          {statusMessage.type === 'error' && <AlertCircle size={20} />}
          {statusMessage.type === 'info' && <AlertCircle size={20} />}
          {statusMessage.message}
        </StatusMessage>
      )}

      <CheckoutButton 
        onClick={handleCheckout} 
        disabled={isLoading || hasAccess}
        $loading={isLoading}
      >
        {isLoading ? (
          <>
            <LoadingSpinner />
            Processando...
          </>
        ) : hasAccess ? (
          <>
            <CheckCircle size={20} />
            Você já tem acesso
          </>
        ) : (
          <>
            <ShoppingCart size={20} />
            Comprar Agora
          </>
        )}
      </CheckoutButton>
      
      {!hasAccess && (
        <SecurityBadge>
          <Lock size={16} />
          Pagamento 100% seguro via Mercado Pago
          <CreditCard size={16} />
        </SecurityBadge>
      )}
    </CheckoutContainer>
  );
};

export default MercadoPagoCheckout;