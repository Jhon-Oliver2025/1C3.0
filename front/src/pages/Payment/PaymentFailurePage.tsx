import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import styled from 'styled-components';
import { XCircle, ArrowLeft, RefreshCw, Home } from 'lucide-react';

// Styled Components
const FailureContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #000000 0%, #2e1a1a 50%, #3e1616 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
`;

const FailureCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  max-width: 500px;
  width: 100%;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(244, 67, 54, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
`;

const FailureIcon = styled.div`
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #f44336, #d32f2f);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 2rem;
  animation: shake 0.5s ease-in-out;
  
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }
  
  svg {
    color: white;
  }
`;

const FailureTitle = styled.h1`
  color: #ffffff;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
  background: linear-gradient(135deg, #f44336, #ef5350);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const FailureMessage = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 2rem;
`;

const ErrorDetails = styled.div`
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid rgba(244, 67, 54, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  
  h3 {
    color: #f44336;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
    font-size: 0.9rem;
  }
`;

const SupportInfo = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  
  h3 {
    color: #ffffff;
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  
  ul {
    color: rgba(255, 255, 255, 0.7);
    text-align: left;
    margin: 0;
    padding-left: 1.5rem;
    
    li {
      margin-bottom: 0.5rem;
    }
  }
`;

const ActionButtons = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
`;

const PrimaryButton = styled.button`
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 50%, #00bcd4 100%);
  border: none;
  color: white;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
  }
`;

const SecondaryButton = styled.button`
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.8);
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.5);
  }
`;

/**
 * Página de falha no pagamento
 * Exibida quando o pagamento não é processado com sucesso
 */
const PaymentFailurePage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Extrair informações dos parâmetros da URL
  const paymentId = searchParams.get('payment_id');
  const status = searchParams.get('status');
  const statusDetail = searchParams.get('status_detail');

  /**
   * Mapeia códigos de erro para mensagens amigáveis
   */
  const getErrorMessage = (status: string | null, statusDetail: string | null) => {
    if (status === 'rejected') {
      switch (statusDetail) {
        case 'cc_rejected_insufficient_amount':
          return 'Cartão rejeitado por saldo insuficiente.';
        case 'cc_rejected_bad_filled_security_code':
          return 'Código de segurança do cartão inválido.';
        case 'cc_rejected_bad_filled_date':
          return 'Data de vencimento do cartão inválida.';
        case 'cc_rejected_bad_filled_other':
          return 'Dados do cartão preenchidos incorretamente.';
        case 'cc_rejected_high_risk':
          return 'Pagamento rejeitado por segurança.';
        default:
          return 'Pagamento rejeitado pelo banco emissor.';
      }
    }
    
    if (status === 'cancelled') {
      return 'Pagamento cancelado pelo usuário.';
    }
    
    return 'Ocorreu um erro durante o processamento do pagamento.';
  };

  const handleTryAgain = () => {
    navigate('/vitrine-alunos');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  const handleContactSupport = () => {
    // Redirecionar para WhatsApp ou email de suporte
    window.open('https://wa.me/5511999999999?text=Olá, tive problemas com meu pagamento', '_blank');
  };

  return (
    <FailureContainer>
      <FailureCard>
        <FailureIcon>
          <XCircle size={50} />
        </FailureIcon>
        
        <FailureTitle>Pagamento Não Processado</FailureTitle>
        
        <FailureMessage>
          Infelizmente, não foi possível processar seu pagamento. 
          Não se preocupe, nenhum valor foi cobrado.
        </FailureMessage>

        {(status || statusDetail) && (
          <ErrorDetails>
            <h3>Detalhes do Erro</h3>
            <p>{getErrorMessage(status, statusDetail)}</p>
          </ErrorDetails>
        )}

        <SupportInfo>
          <h3>O que você pode fazer:</h3>
          <ul>
            <li>Verificar os dados do cartão e tentar novamente</li>
            <li>Tentar com outro cartão ou método de pagamento</li>
            <li>Entrar em contato com seu banco</li>
            <li>Falar com nosso suporte se o problema persistir</li>
          </ul>
        </SupportInfo>

        <ActionButtons>
          <PrimaryButton onClick={handleTryAgain}>
            <RefreshCw size={20} />
            Tentar Novamente
          </PrimaryButton>
          
          <SecondaryButton onClick={handleContactSupport}>
            Falar com Suporte
          </SecondaryButton>
          
          <SecondaryButton onClick={handleGoHome}>
            <Home size={20} />
            Voltar ao Início
          </SecondaryButton>
        </ActionButtons>

        {paymentId && (
          <p style={{ 
            color: 'rgba(255, 255, 255, 0.5)', 
            fontSize: '0.8rem', 
            marginTop: '2rem' 
          }}>
            Referência: {paymentId}
          </p>
        )}
      </FailureCard>
    </FailureContainer>
  );
};

export default PaymentFailurePage;