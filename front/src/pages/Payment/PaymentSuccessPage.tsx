import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import styled from 'styled-components';
import { CheckCircle, ArrowRight, Home } from 'lucide-react';
import { useCourseAccess } from '../../hooks/useCourseAccess';

// Styled Components
const SuccessContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
`;

const SuccessCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  max-width: 500px;
  width: 100%;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
`;

const SuccessIcon = styled.div`
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #4caf50, #2e7d32);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 2rem;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7);
    }
    70% {
      transform: scale(1.05);
      box-shadow: 0 0 0 10px rgba(76, 175, 80, 0);
    }
    100% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(76, 175, 80, 0);
    }
  }
  
  svg {
    color: white;
  }
`;

const SuccessTitle = styled.h1`
  color: #ffffff;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
  background: linear-gradient(135deg, #4caf50, #81c784);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const SuccessMessage = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 2rem;
`;

const CourseInfo = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  
  h3 {
    color: #ffffff;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
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

const LoadingSpinner = styled.div`
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #4caf50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

/**
 * Página de sucesso do pagamento
 * Exibida após a confirmação de pagamento bem-sucedido
 */
const PaymentSuccessPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { refreshUserCourses } = useCourseAccess();
  const [isLoading, setIsLoading] = useState(true);
  const [courseInfo, setCourseInfo] = useState<{
    name: string;
    description: string;
  } | null>(null);

  // Extrair informações dos parâmetros da URL
  const paymentId = searchParams.get('payment_id');
  const status = searchParams.get('status');
  const externalReference = searchParams.get('external_reference');

  useEffect(() => {
    // Aguardar um pouco para o webhook processar
    const timer = setTimeout(async () => {
      try {
        // Atualizar lista de cursos do usuário
        await refreshUserCourses();
        
        // Extrair informações do curso da referência externa
        if (externalReference) {
          const parts = externalReference.split('_');
          if (parts.length >= 2) {
            const courseId = parts[1];
            
            // Mapear IDs dos cursos para nomes
            const courseNames: Record<string, { name: string; description: string }> = {
              'despertar_crypto': {
                name: 'Despertar Crypto - 10 Aulas',
                description: 'Curso completo de introdução às criptomoedas'
              },
              'masterclass': {
                name: 'Masterclass - Trading Avançado',
                description: 'Curso avançado de trading e análise técnica'
              },
              'app_mentoria': {
                name: 'App 1Crypten e Mentoria',
                description: 'Acesso ao app exclusivo e mentoria personalizada'
              }
            };
            
            setCourseInfo(courseNames[courseId] || {
              name: 'Curso Adquirido',
              description: 'Parabéns pela sua compra!'
            });
          }
        }
      } catch (error) {
        console.error('Erro ao processar sucesso do pagamento:', error);
      } finally {
        setIsLoading(false);
      }
    }, 3000); // Aguardar 3 segundos

    return () => clearTimeout(timer);
  }, [externalReference, refreshUserCourses]);

  const handleGoToCourse = () => {
    navigate('/vitrine-alunos');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  if (isLoading) {
    return (
      <SuccessContainer>
        <SuccessCard>
          <LoadingSpinner />
          <SuccessTitle>Processando...</SuccessTitle>
          <SuccessMessage>
            Estamos confirmando seu pagamento e liberando o acesso ao curso.
            Aguarde alguns instantes.
          </SuccessMessage>
        </SuccessCard>
      </SuccessContainer>
    );
  }

  return (
    <SuccessContainer>
      <SuccessCard>
        <SuccessIcon>
          <CheckCircle size={50} />
        </SuccessIcon>
        
        <SuccessTitle>Pagamento Confirmado!</SuccessTitle>
        
        <SuccessMessage>
          Parabéns! Seu pagamento foi processado com sucesso e você já tem acesso ao curso.
        </SuccessMessage>

        {courseInfo && (
          <CourseInfo>
            <h3>{courseInfo.name}</h3>
            <p>{courseInfo.description}</p>
          </CourseInfo>
        )}

        <ActionButtons>
          <PrimaryButton onClick={handleGoToCourse}>
            Acessar Meus Cursos
            <ArrowRight size={20} />
          </PrimaryButton>
          
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
            ID do Pagamento: {paymentId}
          </p>
        )}
      </SuccessCard>
    </SuccessContainer>
  );
};

export default PaymentSuccessPage;