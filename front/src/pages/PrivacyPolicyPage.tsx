import React from 'react';
import styles from './LegalPages.module.css'; // Reutilizando o CSS genérico para páginas legais

const PrivacyPolicyPage: React.FC = () => {
  return (
    <div className={styles.legalPageContainer}>
      <div className={styles.legalContent}>
        <h1>Política de Privacidade</h1>
        <p>A CrypTen está comprometida em proteger a sua privacidade. Esta Política de Privacidade descreve como coletamos, usamos e compartilhamos suas informações pessoais quando você usa nossos serviços.</p>

        <h2>1. Informações que Coletamos</h2>
        <p>Coletamos informações que você nos fornece diretamente, como seu nome, endereço de e-mail e informações de pagamento quando você se registra para uma conta ou usa nossos serviços.</p>
        <p>Também coletamos automaticamente certas informações sobre seu dispositivo e uso dos serviços, incluindo seu endereço IP, tipo de navegador, páginas visitadas e horários de acesso.</p>

        <h2>2. Como Usamos Suas Informações</h2>
        <p>Usamos as informações coletadas para:</p>
        <ul>
          <li>Fornecer, operar e manter nossos serviços;</li>
          <li>Melhorar, personalizar e expandir nossos serviços;</li>
          <li>Entender e analisar como você usa nossos serviços;</li>
          <li>Desenvolver novos produtos, serviços, recursos e funcionalidades;</li>
          <li>Comunicar-nos com você, diretamente ou através de um de nossos parceiros, para atendimento ao cliente, para fornecer atualizações e outras informações relacionadas ao serviço, e para fins de marketing e promoção;</li>
          <li>Processar suas transações;</li>
          <li>Detectar e prevenir fraudes.</li>
        </ul>

        <h2>3. Compartilhamento de Suas Informações</h2>
        <p>Podemos compartilhar suas informações pessoais com terceiros nas seguintes situações:</p>
        <ul>
          <li>Com provedores de serviços que nos ajudam a operar nossos negócios (ex: processamento de pagamentos, hospedagem, análise de dados);</li>
          <li>Para cumprir obrigações legais ou responder a solicitações legais;</li>
          <li>Para proteger nossos direitos, privacidade, segurança ou propriedade, e/ou os de nossas afiliadas, você ou outros;</li>
          <li>Em conexão com uma fusão, venda de ativos da empresa, financiamento ou aquisição de toda ou parte de nosso negócio para outra empresa.</li>
        </ul>

        <h2>4. Segurança dos Dados</h2>
        <p>Implementamos medidas de segurança razoáveis para proteger suas informações pessoais contra acesso não autorizado, alteração, divulgação ou destruição. No entanto, nenhum método de transmissão pela Internet ou método de armazenamento eletrônico é 100% seguro.</p>

        <h2>5. Seus Direitos de Privacidade</h2>
        <p>Dependendo da sua localização, você pode ter certos direitos em relação às suas informações pessoais, como o direito de acessar, corrigir ou excluir seus dados. Para exercer esses direitos, entre em contato conosco.</p>

        <h2>6. Alterações nesta Política de Privacidade</h2>
        <p>Podemos atualizar nossa Política de Privacidade periodicamente. Notificaremos você sobre quaisquer alterações publicando a nova Política de Privacidade nesta página. Aconselhamos que você revise esta Política de Privacidade periodicamente para quaisquer alterações.</p>

        <h2>7. Contato</h2>
        <p>Se você tiver alguma dúvida sobre esta Política de Privacidade, entre em contato conosco através do nosso suporte.</p>

        <p>Última atualização: 23 de maio de 2024</p>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;