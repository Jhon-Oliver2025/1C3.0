import React, { useState, useRef, useEffect } from 'react';
import styles from './ChatInterface.module.css';
import zionHeader from '/src/assets/zion.png';

// Definição da interface para uma mensagem
interface Message {
  text: string;
  sender: 'user' | 'bot';
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    { text: 'Olá! Eu sou Zion, sua assistente de IA. Como posso te ajudar hoje?', sender: 'bot' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messageListRef = useRef<HTMLDivElement>(null);

  // Efeito para rolar para a última mensagem
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text) return;

    const userMessage: Message = { text, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5002/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
        },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      const agentResponse = responseData.response?.reply || 'Não consegui processar sua mensagem. Tente novamente.';
      
      setMessages(prev => [...prev, { 
        text: agentResponse,
        sender: 'bot' 
      }]);

    } catch (error) {
      console.error('Erro na requisição:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setMessages(prev => [...prev, { 
        text: `Desculpe, estou com problemas para me conectar. Detalhe: ${errorMessage}`, 
        sender: 'bot' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      {/* Header with zion.png */}
      <div className={styles.chatHeader}>
        <img 
          src={zionHeader} 
          alt="Zion AI Assistant" 
          className={styles.headerImage}
        />
      </div>
      
      <div className={styles.messageList} ref={messageListRef}>
        {messages.map((msg, index) => (
          <div key={index} className={`${styles.message} ${styles[msg.sender]}`}>
            <div className={styles.messageContent}>
              <p>{msg.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className={`${styles.message} ${styles.bot}`}>
            <div className={styles.messageContent}>
              <p>Zion está digitando...</p>
            </div>
          </div>
        )}
      </div>
      <div className={styles.inputArea}>
        <input
          type="text"
          placeholder="Digite sua mensagem aqui..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading}>
          Enviar
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;