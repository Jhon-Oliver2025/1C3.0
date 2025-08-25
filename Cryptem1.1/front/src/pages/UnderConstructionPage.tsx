import React from 'react';
import styles from './UnderConstructionPage.module.css';

const UnderConstructionPage: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.contentBox}>
        <h1 className={styles.title}>Página em Construção</h1>
        <p className={styles.message}>
          Em breve, esta funcionalidade estará em pleno funcionamento!
        </p>
        <p className={styles.subMessage}>
          Agradecemos a sua paciência enquanto trabalhamos para trazer as melhores novidades.
        </p>
      </div>
    </div>
  );
};

export default UnderConstructionPage;