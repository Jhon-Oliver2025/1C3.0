/**
 * Componente de Cabeçalho Motivacional Reutilizável
 * Usado em todas as páginas para manter consistência visual
 */

import React from 'react';
import './MotivationalHeader.css';

interface MotivationalHeaderProps {
  text?: string;
  className?: string;
}

/**
 * Frases motivacionais para rotação aleatória
 */
const motivationalPhrases = [
  "A nova fronteira do investimento está ao seu alcance.",
  "Veja os sinais em meio ao caos e transforme sua jornada.",
  "Desbrave o universo cripto com clareza e precisão, do seu jeito.",
  "O futuro dos seus investimentos não é no espaço, mas em suas mãos.",
  "A melhor forma de prever o futuro é construí-lo agora.",
  "Nós transformamos a complexidade do mercado em sinais claros. Sua missão é seguir o plano.",
  "Hoje, você investe em ativos. Amanhã, você colhe um legado. Continue firme.",
  "Seja Bem Vindo ao nosso Ecosistema e a essa revolução Crypto."
];

/**
 * Componente do Cabeçalho Motivacional
 */
const MotivationalHeader: React.FC<MotivationalHeaderProps> = ({ 
  text, 
  className = '' 
}) => {
  // Seleciona uma frase aleatória se não for fornecida
  const displayText = text || motivationalPhrases[Math.floor(Math.random() * motivationalPhrases.length)];

  return (
    <div className={`motivational-header-container ${className}`}>
      <div className="motivational-header">
        <p className="motivational-text">{displayText}</p>
      </div>
      <div className="motivational-safety-gap"></div>
    </div>
  );
};

export default MotivationalHeader;