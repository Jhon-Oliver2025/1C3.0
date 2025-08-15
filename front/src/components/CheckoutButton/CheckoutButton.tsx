import React, { useState } from 'react';
import styled from 'styled-components';
import { ShoppingCart, CreditCard, Lock } from 'lucide-react';

// Styled Components para o botão de checkout
const CheckoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 2rem;
`;

const PriceSection = styled.div`
  text-align: center;
  margin-bottom: 1rem;
  
  .original-price {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.6);
    text-decoration: line-through;
    margin-bottom: 0.5rem;
  }
  
  .current-price {
    font-size: 2.5rem;
    font-weight: bold;
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }
  
  .installments {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
  }
`;

const CheckoutButton = styled.button<{ loading?: boolean }>`
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 50%, #00bcd4 100%);
  border: none;
  color: white;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: ${props => props.loading ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
  opacity: ${props => props.loading ? 0.7 : 1};
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const SecurityBadge = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.5rem;
`;

const BenefitsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 1rem 0;
  
  li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.9rem;
    
    &:before {
      content: '✓';
      color: #4caf50;
      font-weight: bold;
    }
  }
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

// Interface para props do componente
interface CheckoutButtonProps {
  courseTitle: string;
  originalPrice: number;
  currentPrice: number;
  installments?: number;
  onCheckout: () => Promise<void>;
  benefits?: string[];
}

/**
 * Componente de botão de checkout integrado com Mercado Pago
 * Exibe preço, parcelamento e inicia o processo de pagamento
 */
const CheckoutButtonComponent: React.FC<CheckoutButtonProps> = ({
  courseTitle,
  originalPrice,
  currentPrice,
  installments = 12,
  onCheckout,
  benefits = [
    'Acesso vitalício ao curso',
    '8 aulas práticas e objetivas',
    'Suporte direto com especialistas',
    'Certificado de conclusão',
    'Atualizações gratuitas',
    'Garantia de 7 dias'
  ]
}) => {
  const [isLoading, setIsLoading] = useState(false);
  
  /**
   * Manipula o clique no botão de checkout
   */
  const handleCheckout = async () => {
    setIsLoading(true);
    try {
      await onCheckout();
    } catch (error) {
      console.error('Erro no checkout:', error);
      alert('Erro ao processar pagamento. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const installmentValue = currentPrice / installments;
  const discountPercentage = Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
  
  return (
    <CheckoutContainer>
      <PriceSection>
        {originalPrice > currentPrice && (
          <div className="original-price">
            De R$ {originalPrice.toFixed(2).replace('.', ',')}
          </div>
        )}
        
        <div className="current-price">
          R$ {currentPrice.toFixed(2).replace('.', ',')}
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
          ou {installments}x de R$ {installmentValue.toFixed(2).replace('.', ',')} sem juros
        </div>
      </PriceSection>
      
      <BenefitsList>
        {benefits.map((benefit, index) => (
          <li key={index}>{benefit}</li>
        ))}
      </BenefitsList>
      
      <CheckoutButton 
        onClick={handleCheckout} 
        disabled={isLoading}
        loading={isLoading}
      >
        {isLoading ? (
          <>
            <LoadingSpinner />
            Processando...
          </>
        ) : (
          <>
            <ShoppingCart size={20} />
            Comprar Agora - {courseTitle}
          </>
        )}
      </CheckoutButton>
      
      <SecurityBadge>
        <Lock size={16} />
        Pagamento 100% seguro via Mercado Pago
        <CreditCard size={16} />
      </SecurityBadge>
    </CheckoutContainer>
  );
};

export default CheckoutButtonComponent;