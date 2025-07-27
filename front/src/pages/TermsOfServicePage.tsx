import React from 'react';
import styles from './LegalPages.module.css'; // Vamos criar um CSS genérico para páginas legais

const TermsOfServicePage: React.FC = () => {
  return (
    <div className={styles.legalPageContainer}>
      <div className={styles.legalContent}>
        <h1>Termos de Serviço</h1>
        <p>Bem-vindo aos Termos de Serviço da CrypTen. Ao acessar ou usar nossos serviços, você concorda em cumprir e estar vinculado aos seguintes termos e condições. Por favor, leia-os cuidadosamente.</p>

        <h2>1. Aceitação dos Termos</h2>
        <p>Ao usar os serviços da CrypTen, você concorda com estes Termos de Serviço e com nossa Política de Privacidade. Se você não concordar com qualquer parte destes termos, não deverá usar nossos serviços.</p>

        <h2>2. Uso dos Serviços</h2>
        <p>Você concorda em usar os serviços da CrypTen apenas para fins lícitos e de maneira que não infrinja os direitos de, ou restrinja ou iniba o uso e o desfrute dos serviços por terceiros.</p>

        <h2>3. Contas de Usuário</h2>
        <p>Para acessar certas funcionalidades dos nossos serviços, você pode ser obrigado a criar uma conta. Você é responsável por manter a confidencialidade de suas informações de conta e por todas as atividades que ocorrem sob sua conta.</p>

        <h2>4. Propriedade Intelectual</h2>
        <p>Todo o conteúdo e materiais disponíveis nos serviços da CrypTen, incluindo, mas não se limitando a texto, gráficos, logotipos, ícones, imagens, clipes de áudio, downloads digitais e software, são propriedade da CrypTen ou de seus licenciadores e são protegidos por leis de direitos autorais e outras leis de propriedade intelectual.</p>

        <h2>5. Limitação de Responsabilidade</h2>
        <p>A CrypTen não será responsável por quaisquer danos diretos, indiretos, incidentais, especiais, consequenciais ou exemplares, incluindo, mas não se limitando a, danos por perda de lucros, boa vontade, uso, dados ou outras perdas intangíveis, resultantes do uso ou da incapacidade de usar os serviços.</p>

        <h2>6. Alterações nos Termos</h2>
        <p>A CrypTen reserva-se o direito de modificar estes Termos de Serviço a qualquer momento. Quaisquer alterações serão efetivas imediatamente após a publicação dos termos revisados em nosso site. Seu uso continuado dos serviços após a publicação de quaisquer alterações constitui sua aceitação dessas alterações.</p>

        <h2>7. Lei Aplicável</h2>
        <p>Estes Termos de Serviço serão regidos e interpretados de acordo com as leis do [Seu País/Estado], sem levar em conta seus princípios de conflito de leis.</p>

        <h2>8. Contato</h2>
        <p>Se você tiver alguma dúvida sobre estes Termos de Serviço, entre em contato conosco através do nosso suporte.</p>

        <p>Última atualização: 23 de maio de 2024</p>
      </div>
    </div>
  );
};

export default TermsOfServicePage;