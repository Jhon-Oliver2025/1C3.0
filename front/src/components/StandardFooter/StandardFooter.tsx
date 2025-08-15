import React from 'react';
import styled from 'styled-components';

/**
 * Componente de rodapé padrão para todas as páginas
 * Baseado no Footer original mas simplificado conforme especificações:
 * - Mesma fonte e cor (#808080)
 * - Sem ícones de redes sociais
 * - Apenas links: Política de Privacidade e Termos de Serviço
 */

const FooterContainer = styled.footer`
  background-color: #000000; /* Cor de fundo preta */
  color: #808080;
  padding: 40px 20px;
  font-size: 0.9em;
  border-top: 1px solid #333;
  margin-top: 40px;
`;

const FooterContent = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
`;

const FooterLinks = styled.div`
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    gap: 1rem;
    flex-direction: column;
    align-items: center;
  }
`;

const FooterLink = styled.a`
  color: #808080;
  text-decoration: none;
  font-size: 0.9em;
  
  &:hover {
    text-decoration: underline;
  }
`;

const Copyright = styled.div`
  text-align: center;
  margin-top: 20px;
  font-size: 0.8em;
  color: #555;
`;

const StandardFooter: React.FC = () => {
  return (
    <FooterContainer>
      <FooterContent>
        <FooterLinks>
          <FooterLink href="/privacy-policy">Política de Privacidade</FooterLink>
          <FooterLink href="/terms-of-service">Termos de Serviço</FooterLink>
        </FooterLinks>
        
        <Copyright>
          © 1Crypten. Todos os direitos reservados.
        </Copyright>
      </FooterContent>
    </FooterContainer>
  );
};

export default StandardFooter;