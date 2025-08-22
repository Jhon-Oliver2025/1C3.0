import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { ShoppingCart, CreditCard, Lock, CheckCircle, AlertCircle } from 'lucide-react';

// Declaração do SDK do Mercado Pago
declare global {
  interface Window {
    MercadoPago: any;
  }
}

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
      default:
        return '';
    }
  }}
`;

// Container para o checkout transparente
const TransparentCheckoutContainer = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  margin: 1rem 0;
  
  .mp-form {
    background: transparent !important;
  }
  
  .mp-form .mp-form-row {
    margin-bottom: 1rem;
  }
  
  .mp-form .mp-form-row label {
    color: rgba(255, 255, 255, 0.9) !important;
    font-weight: 500;
    margin-bottom: 0.5rem;
    display: block;
  }
  
  .mp-form .mp-form-row input {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    color: white !important;
    padding: 0.75rem !important;
    width: 100% !important;
    font-size: 1rem !important;
  }
  
  .mp-form .mp-form-row input:focus {
    border-color: #2196f3 !important;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2) !important;
    outline: none !important;
  }
  
  .mp-form .mp-form-row input::placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
  }
  
  .mp-form .mp-form-row select {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    color: white !important;
    padding: 0.75rem !important;
    width: 100% !important;
  }
  
  .mp-form .mp-form-row .mp-error {
    color: #f44336 !important;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
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
  const [mpInstance, setMpInstance] = useState<any>(null);
  const [cardForm, setCardForm] = useState<any>(null);
  const [preferenceId, setPreferenceId] = useState<string | null>(null);
  const checkoutRef = useRef<HTMLDivElement>(null);

  // Carregar SDK do Mercado Pago
  useEffect(() => {
    loadMercadoPagoSDK();
  }, []);

  // Verificar se o usuário já tem acesso ao curso
  useEffect(() => {
    checkCourseAccess();
  }, [courseId]);

  // Inicializar Card Payment Brick quando tiver instância MP
  useEffect(() => {
    if (mpInstance && !hasAccess && !cardForm) {
      console.log('Iniciando Card Payment Brick com instância MP');
      initializeTransparentCheckout();
    }
  }, [mpInstance, hasAccess, cardForm]);

  /**
   * Carrega o SDK oficial do Mercado Pago v2
   */
  const loadMercadoPagoSDK = () => {
    if (window.MercadoPago) {
      console.log('SDK do Mercado Pago já carregado');
      initializeMercadoPago();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://sdk.mercadopago.com/js/v2';
    script.async = true;
    script.onload = () => {
      console.log('SDK do Mercado Pago v2 carregado com sucesso');
      initializeMercadoPago();
    };
    script.onerror = () => {
      console.error('Erro ao carregar SDK do Mercado Pago');
      setStatusMessage({
        type: 'error',
        message: 'Erro ao carregar sistema de pagamento'
      });
    };
    document.head.appendChild(script);
  };

  /**
   * Inicializa a instância do Mercado Pago com a chave pública
   */
  const initializeMercadoPago = async () => {
    try {
      // Buscar configuração da API
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/payments/config`);
      const config = await response.json();
      
      if (config.config && config.config.public_key) {
        console.log('Inicializando Mercado Pago com chave pública:', config.config.public_key);
        const mp = new window.MercadoPago(config.config.public_key, {
          locale: 'pt-BR'
        });
        setMpInstance(mp);
        
        // Criar preferência automaticamente
        await createPaymentPreference();
      } else {
        throw new Error('Chave pública não encontrada na resposta da API');
      }
    } catch (error) {
      console.error('Erro ao inicializar Mercado Pago:', error);
      setStatusMessage({
        type: 'error',
        message: 'Erro ao configurar sistema de pagamento'
      });
    }
  };

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
   * Cria preferência de pagamento no backend
   */
  const createPaymentPreference = async () => {
    try {
      setIsLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || '';
      
      const requestBody = {
        course_id: courseId,
        course_name: course.name,
        course_price: course.price,
        course_description: course.description
      };

      const response = await fetch(`${apiUrl}/api/payments/create-preference`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        setPreferenceId(data.preference_id);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao criar preferência de pagamento');
      }
    } catch (error) {
      console.error('Erro ao criar preferência:', error);
      setStatusMessage({
        type: 'error',
        message: error instanceof Error ? error.message : 'Erro ao criar preferência de pagamento'
      });
      onError?.(error instanceof Error ? error.message : 'Erro ao criar preferência de pagamento');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Inicializa o Card Payment Brick oficial do Mercado Pago v2
   */
  const initializeTransparentCheckout = async () => {
    if (!mpInstance) {
      console.log('Aguardando instância do Mercado Pago');
      return;
    }

    try {
      console.log('Inicializando Card Payment Brick oficial');
      
      // Limpar container antes de renderizar
      const container = document.getElementById('mercadopago-checkout');
      if (container) {
        container.innerHTML = '';
        
        // Criar o Card Payment Brick conforme documentação oficial
        const bricksBuilder = mpInstance.bricks();
        
        const settings = {
          initialization: {
            amount: course.price, // Valor do pagamento
          },
          customization: {
            visual: {
              style: {
                theme: 'bootstrap' // Usar tema bootstrap que é mais compatível
              }
            },
            paymentMethods: {
              creditCard: 'all',
              debitCard: 'all',
              ticket: 'all', // Boleto
              bankTransfer: 'all', // PIX
              mercadoPago: 'all' // Conta Mercado Pago
            }
          },
          callbacks: {
            onReady: () => {
              console.log('✅ Card Payment Brick pronto e renderizado!');
              console.log('🎯 Formulário carregado e visível!');
              setIsLoading(false);
              
              // Garantir que o container não seja limpo
              const container = document.getElementById('mercadopago-checkout');
              if (container) {
                container.style.minHeight = '400px';
                container.style.display = 'block';
                console.log('🔒 Container protegido contra limpeza');
              }
            },
            onSubmit: async (cardFormData: any) => {
              console.log('Dados do cartão recebidos:', cardFormData);
              setIsLoading(true);
              
              try {
                // Processar pagamento no backend
                const result = await processCardPayment(cardFormData);
                
                if (result.status === 'approved') {
                  setStatusMessage({
                    type: 'success',
                    message: 'Pagamento aprovado com sucesso!'
                  });
                  onSuccess?.(result);
                  
                  // Redirecionar após sucesso
                  setTimeout(() => {
                    window.location.href = '/payment/success';
                  }, 2000);
                } else {
                  throw new Error(result.message || 'Pagamento não aprovado');
                }
              } catch (error) {
                console.error('Erro ao processar pagamento:', error);
                setStatusMessage({
                  type: 'error',
                  message: error instanceof Error ? error.message : 'Erro ao processar pagamento'
                });
                onError?.(error instanceof Error ? error.message : 'Erro ao processar pagamento');
              } finally {
                setIsLoading(false);
              }
            },
            onError: (error: any) => {
              console.error('Erro no Card Payment Brick:', error);
              setStatusMessage({
                type: 'error',
                message: 'Erro no formulário de pagamento'
              });
              setIsLoading(false);
            }
          }
        };
        
        // Renderizar o Card Payment Brick
        console.log('🔄 Criando Card Payment Brick...');
        console.log('📋 Settings:', settings);
        console.log('📦 Container ID: mercadopago-checkout');
        
        // Timeout para detectar se o Brick não carrega
        const timeoutId = setTimeout(() => {
          console.warn('⚠️ Card Payment Brick demorou mais de 10s para carregar');
          setStatusMessage({
            type: 'error',
            message: 'Timeout ao carregar formulário de pagamento. Tente recarregar a página.'
          });
          setIsLoading(false);
        }, 10000);
        
        const cardPaymentBrick = await bricksBuilder.create(
          'cardPayment',
          'mercadopago-checkout',
          settings
        );
        
        clearTimeout(timeoutId);
        setCardForm(cardPaymentBrick);
        console.log('✅ Card Payment Brick inicializado com sucesso!');
        console.log('🎯 Brick instance:', cardPaymentBrick);
        
        // Adicionar proteção contra destruição acidental
        const protectBrick = () => {
          const container = document.getElementById('mercadopago-checkout');
          if (container && container.children.length === 0) {
            console.warn('⚠️ Container foi limpo! Tentando recriar...');
            // Não recriar automaticamente para evitar loops
          }
        };
        
        // Verificar a cada 2 segundos se o brick ainda existe
        const protectionInterval = setInterval(protectBrick, 2000);
        
        // Limpar interval quando o componente for desmontado
        return () => {
          clearInterval(protectionInterval);
          if (cardPaymentBrick && typeof cardPaymentBrick.unmount === 'function') {
            try {
              cardPaymentBrick.unmount();
            } catch (error) {
              console.log('Brick já foi desmontado');
            }
          }
        };
        
      }
    } catch (error) {
      console.error('Erro ao inicializar Card Payment Brick:', error);
      setStatusMessage({
        type: 'error',
        message: 'Erro ao inicializar sistema de pagamento'
      });
      setIsLoading(false);
    }
  };
  
  /**
   * Processa o pagamento com cartão no backend
   */
  const processCardPayment = async (cardFormData: any) => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const token = localStorage.getItem('authToken');
      
      const paymentData = {
        token: cardFormData.token,
        payment_method_id: cardFormData.payment_method_id,
        transaction_amount: course.price,
        installments: cardFormData.installments || 1,
        description: `Pagamento do curso: ${course.name}`,
        payer: {
          email: cardFormData.payer?.email || 'test@test.com',
          identification: {
            type: cardFormData.payer?.identification?.type || 'CPF',
            number: cardFormData.payer?.identification?.number || '12345678901'
          }
        },
        course_id: courseId
      };
      
      console.log('Enviando dados de pagamento:', paymentData);
      
      const response = await fetch(`${apiUrl}/api/payments/process-card`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(paymentData)
      });
      
      const result = await response.json();
      console.log('Resposta do backend:', result);
      
      if (response.ok) {
        return result;
      } else {
        throw new Error(result.message || 'Erro no processamento do pagamento');
      }
      
    } catch (error) {
      console.error('Erro ao processar pagamento com cartão:', error);
      throw error;
    }
  };

  // Função handleCheckout removida - agora usamos Payment Brick

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

      {hasAccess ? (
        <StatusMessage type="success">
          <CheckCircle size={20} />
          Você já tem acesso a este curso
        </StatusMessage>
      ) : (
        <>
          {/* Checkout Transparente do Mercado Pago */}
          <TransparentCheckoutContainer ref={checkoutRef}>
            {isLoading ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                padding: '2rem' 
              }}>
                <LoadingSpinner />
                <p style={{ color: 'rgba(255, 255, 255, 0.8)', marginTop: '1rem', textAlign: 'center' }}>
                  Carregando formulário de pagamento seguro...
                </p>
              </div>
            ) : (
              <>
                <div style={{ 
                   display: 'flex', 
                   alignItems: 'center', 
                   justifyContent: 'center', 
                   marginBottom: '1.5rem' 
                 }}>
                   <CreditCard size={24} style={{ color: '#2196f3', marginRight: '0.5rem' }} />
                   <h3 style={{ color: '#ffffff', margin: 0 }}>Escolha sua forma de pagamento</h3>
                 </div>
                 
                 {/* Container onde o Mercado Pago renderizará o checkout */}
                 <div id="mercadopago-checkout" style={{
                   minHeight: '400px',
                   width: '100%',
                   border: '1px solid rgba(255, 255, 255, 0.1)',
                   borderRadius: '8px',
                   padding: '1rem'
                 }}>
                   {isLoading && (
                     <div style={{
                       display: 'flex',
                       justifyContent: 'center',
                       alignItems: 'center',
                       height: '200px',
                       color: 'rgba(255, 255, 255, 0.7)'
                     }}>
                       <LoadingSpinner />
                       <span style={{ marginLeft: '0.5rem' }}>Carregando checkout...</span>
                     </div>
                   )}
                   {!isLoading && !preferenceId && (
                     <div style={{
                       display: 'flex',
                       justifyContent: 'center',
                       alignItems: 'center',
                       height: '200px',
                       color: 'rgba(255, 255, 255, 0.7)'
                     }}>
                       Preparando sistema de pagamento...
                     </div>
                   )}
                 </div>
              </>
            )}
          </TransparentCheckoutContainer>
          
          <SecurityBadge>
            <Lock size={16} />
            Pagamento 100% seguro via Mercado Pago
            <CreditCard size={16} />
          </SecurityBadge>
        </>
      )}
    </CheckoutContainer>
  );
};

export default MercadoPagoCheckout;