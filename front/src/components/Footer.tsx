import React from 'react';
import styled from 'styled-components';

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
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;

  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
`;

const FooterColumn = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const FooterLink = styled.li`
  margin-bottom: 10px;

  a {
    color: #808080;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
`;

const SocialIcons = styled.div`
  margin-top: 20px;
  display: flex;
  gap: 15px;

  a {
    color: #808080;
    font-size: 1.5em;
    &:hover {
      color: #fff;
    }
  }
`;

const Copyright = styled.div`
  text-align: center;
  margin-top: 40px;
  font-size: 0.8em;
  color: #555;
`;

const Footer: React.FC = () => {
  return (
    <FooterContainer>
      <FooterContent>
        <FooterColumn>
          <FooterLink><a href="#">Áudio e Legendas</a></FooterLink>
          <FooterLink><a href="#">Centro de Ajuda</a></FooterLink>
          <FooterLink><a href="#">Cartão pré-pago</a></FooterLink>
          <FooterLink><a href="#">Imprensa</a></FooterLink>
        </FooterColumn>
        <FooterColumn>
          <FooterLink><a href="#">Relações com investidores</a></FooterLink>
          <FooterLink><a href="#">Carreiras</a></FooterLink>
          <FooterLink><a href="#">Termos de Uso</a></FooterLink>
          <FooterLink><a href="#">Informações corporativas</a></FooterLink>
        </FooterColumn>
        <FooterColumn>
          <FooterLink><a href="#">Privacidade</a></FooterLink>
          <FooterLink><a href="#">Preferências de cookies</a></FooterLink>
          <FooterLink><a href="#">Avisos legais</a></FooterLink>
        </FooterColumn>
        <FooterColumn>
          <FooterLink><a href="#">Entre em contato</a></FooterLink>
        </FooterColumn>
      </FooterContent>
      <SocialIcons>
        {/* Ícones de redes sociais - placeholders */}
        <a href="#"><i className="fab fa-facebook-f"></i></a>
        <a href="#"><i className="fab fa-instagram"></i></a>
        <a href="#"><i className="fab fa-twitter"></i></a>
        <a href="#"><i className="fab fa-youtube"></i></a>
      </SocialIcons>
      <Copyright>
        © 1Crypten. Todos os direitos reservados.
      </Copyright>
    </FooterContainer>
  );
};

export default Footer;