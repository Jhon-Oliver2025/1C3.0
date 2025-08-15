import React, { useState } from 'react';
import styled from 'styled-components';
import { Shield, Lock, CreditCard, CheckCircle, Star, Clock, Users, Award, Zap } from 'lucide-react';
import MercadoPagoCheckout from '../../components/MercadoPagoCheckout/MercadoPagoCheckout';
import StandardFooter from '../../components/StandardFooter/StandardFooter';
import BannerChe01 from '../../assets/Checkouts/BannerChe01.png';
import Selo1 from '../../assets/Checkouts/selo 1.png';
import Selo2 from '../../assets/Checkouts/selo 2.png';
import Selo3 from '../../assets/Checkouts/selo 3 .png';

// Styled Components
const CheckoutContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #16213e 100%);
  color: white;
`;

const TopBanner = styled.div`
  width: 100%;
  height: 300px;
  background-image: url(${BannerChe01});
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  background-color: rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 3rem;
  border-radius: 12px;
  margin: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 1024px) {
    height: 250px;
    margin: 1.5rem;
  }
  
  @media (max-width: 768px) {
    height: 180px;
    margin: 1rem;
  }
  
  @media (max-width: 480px) {
    height: 150px;
    margin: 0.5rem;
  }
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 3rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
`;

const CheckoutSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  height: fit-content;
`;

const GuaranteesSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const SelosVerticalBanner = styled.div`
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  
  h3 {
    color: #333;
    font-size: 1.1rem;
    margin-bottom: 1rem;
    text-align: center;
    font-weight: 600;
  }
  
  .selos-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
  }
  
  .selo-item {
    width: 100%;
    height: 180px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid rgba(0, 0, 0, 0.05);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      background: white;
    }
  }
  
  @media (max-width: 768px) {
    .selo-item {
      height: 120px;
    }
  }
`;

const GuaranteeCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #4caf50;
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    
    li {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: rgba(255, 255, 255, 0.8);
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      
      svg {
        color: #4caf50;
        flex-shrink: 0;
      }
    }
  }
`;

const TestimonialsSection = styled.div`
  margin-top: 4rem;
  padding: 0 2rem;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
  
  h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

const TestimonialsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
`;

const TestimonialCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
  
  .stars {
    display: flex;
    gap: 0.25rem;
    margin-bottom: 1rem;
    
    svg {
      color: #ffc107;
    }
  }
  
  .testimonial-text {
    font-style: italic;
    line-height: 1.6;
    margin-bottom: 1.5rem;
    color: rgba(255, 255, 255, 0.9);
  }
  
  .author {
    display: flex;
    align-items: center;
    gap: 1rem;
    
    .avatar {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: linear-gradient(135deg, #2196f3, #00bcd4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 1.2rem;
    }
    
    .info {
      .name {
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.25rem;
      }
      
      .location {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.6);
      }
    }
  }
`;

const CourseTitle = styled.h1`
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #2196f3, #00bcd4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const CourseSubtitle = styled.p`
  text-align: center;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
`;

/**
 * Página de checkout dedicada para o curso Despertar Crypto
 * Layout com banner no topo, checkout à esquerda, garantias à direita e depoimentos embaixo
 */
const CheckoutDespertarCryptoPage: React.FC = () => {
  // Dados do curso Despertar Crypto
  const courseData = {
    id: 'despertar_crypto',
    name: 'Despertar Crypto - 10 Aulas',
    description: 'Curso completo de introdução às criptomoedas com 10 aulas práticas e objetivas.',
    price: 197.00
  };

  // Depoimentos fictícios
  const testimonials = [
    {
      id: 1,
      name: 'Carlos Silva',
      location: 'São Paulo, SP',
      avatar: 'CS',
      text: 'Incrível! Em apenas 2 semanas já consegui entender o mercado crypto e fazer meus primeiros investimentos com segurança. O curso é muito didático e prático.',
      rating: 5
    },
    {
      id: 2,
      name: 'Maria Santos',
      location: 'Rio de Janeiro, RJ',
      avatar: 'MS',
      text: 'Sempre tive medo de investir em crypto, mas o curso me deu toda a confiança que precisava. Já estou vendo resultados positivos!',
      rating: 5
    },
    {
      id: 3,
      name: 'João Oliveira',
      location: 'Belo Horizonte, MG',
      avatar: 'JO',
      text: 'Melhor investimento que já fiz! O conteúdo é de altíssima qualidade e o suporte é excepcional. Recomendo para todos.',
      rating: 5
    },
    {
      id: 4,
      name: 'Ana Costa',
      location: 'Porto Alegre, RS',
      avatar: 'AC',
      text: 'Curso fantástico! Consegui triplicar meu investimento inicial seguindo as estratégias ensinadas. Vale cada centavo!',
      rating: 5
    },
    {
      id: 5,
      name: 'Pedro Ferreira',
      location: 'Brasília, DF',
      avatar: 'PF',
      text: 'Conteúdo muito bem estruturado e fácil de entender. Mesmo sendo iniciante, consegui acompanhar tudo perfeitamente.',
      rating: 5
    },
    {
      id: 6,
      name: 'Luciana Alves',
      location: 'Salvador, BA',
      avatar: 'LA',
      text: 'Excelente curso! As aulas são objetivas e cheias de informações valiosas. Já indiquei para vários amigos.',
      rating: 5
    }
  ];

  return (
    <CheckoutContainer>
      {/* Banner do Topo */}
      <TopBanner />

      {/* Conteúdo Principal */}
      <MainContent>
        {/* Seção do Checkout (Esquerda) */}
        <CheckoutSection>
          <MercadoPagoCheckout
            courseId={courseData.id}
            course={{
              name: courseData.name,
              description: courseData.description,
              price: courseData.price
            }}
            onSuccess={(paymentData) => {
              console.log('Pagamento realizado:', paymentData);
            }}
            onError={(error) => {
              console.error('Erro no pagamento:', error);
            }}
          />
        </CheckoutSection>

        {/* Seção de Garantias e Segurança (Direita) */}
        <GuaranteesSection>
          {/* Banner Vertical com Selos */}
          <SelosVerticalBanner>
            <h3>🏆 Selos de Qualidade</h3>
            <div className="selos-container">
              <div className="selo-item">
                <img src={Selo3} alt="Selo de Qualidade 3" />
              </div>
              <div className="selo-item">
                <img src={Selo2} alt="Selo de Qualidade 2" />
              </div>
              <div className="selo-item">
                <img src={Selo1} alt="Selo de Qualidade 1" />
              </div>
            </div>
          </SelosVerticalBanner>

          {/* Garantias */}
          <GuaranteeCard>
            <h3>
              <Shield size={20} />
              Garantias do Curso
            </h3>
            <ul>
              <li>
                <CheckCircle size={16} />
                Garantia de 7 dias ou seu dinheiro de volta
              </li>
              <li>
                <CheckCircle size={16} />
                Acesso vitalício ao conteúdo
              </li>
              <li>
                <CheckCircle size={16} />
                Atualizações gratuitas por 1 ano
              </li>
              <li>
                <CheckCircle size={16} />
                Suporte direto com especialistas
              </li>
              <li>
                <CheckCircle size={16} />
                Certificado de conclusão
              </li>
            </ul>
          </GuaranteeCard>

          {/* Segurança do Pagamento */}
          <GuaranteeCard>
            <h3>
              <Lock size={20} />
              Segurança do Pagamento
            </h3>
            <ul>
              <li>
                <CreditCard size={16} />
                Processado pelo Mercado Pago
              </li>
              <li>
                <Shield size={16} />
                Criptografia SSL 256 bits
              </li>
              <li>
                <CheckCircle size={16} />
                Dados protegidos e seguros
              </li>
              <li>
                <Award size={16} />
                Certificado de segurança PCI DSS
              </li>
            </ul>
          </GuaranteeCard>

          {/* Informações Adicionais */}
          <GuaranteeCard>
            <h3>
              <Zap size={20} />
              Por que escolher agora?
            </h3>
            <ul>
              <li>
                <Clock size={16} />
                Acesso imediato após pagamento
              </li>
              <li>
                <Users size={16} />
                +5.000 alunos já transformaram suas vidas
              </li>
              <li>
                <Star size={16} />
                Avaliação 4.9/5 estrelas
              </li>
              <li>
                <Award size={16} />
                Método comprovado e testado
              </li>
            </ul>
          </GuaranteeCard>
        </GuaranteesSection>
      </MainContent>

      {/* Seção de Depoimentos */}
      <TestimonialsSection>
        <h2>O que nossos alunos estão dizendo</h2>
        <TestimonialsGrid>
          {testimonials.map((testimonial) => (
            <TestimonialCard key={testimonial.id}>
              <div className="stars">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} size={16} fill="currentColor" />
                ))}
              </div>
              <div className="testimonial-text">
                "{testimonial.text}"
              </div>
              <div className="author">
                <div className="avatar">
                  {testimonial.avatar}
                </div>
                <div className="info">
                  <div className="name">{testimonial.name}</div>
                  <div className="location">{testimonial.location}</div>
                </div>
              </div>
            </TestimonialCard>
          ))}
        </TestimonialsGrid>
      </TestimonialsSection>
      
      {/* Rodapé Padrão */}
      <StandardFooter />
    </CheckoutContainer>
  );
};

export default CheckoutDespertarCryptoPage;