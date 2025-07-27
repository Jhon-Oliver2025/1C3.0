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

  const handleFileUpload = async (file: File) => {
    const base64Data = await new Promise<string>((resolve) => {
      const reader = new FileReader();
      reader.onload = () => resolve((reader.result as string).split(',')[1]);
      reader.readAsDataURL(file);
    });

    return {
      type: "file",
      file: {
        name: file.name,
        bytes: base64Data,
        mime_type: file.type
      }
    };
  };

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text) return;

    const userMessage: Message = { text, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    // Gerar IDs únicos para a sessão e tarefa
    const taskId = crypto.randomUUID();
    const sessionId = crypto.randomUUID();
    const callId = crypto.randomUUID();

    try {
      // Estruturar a mensagem no formato A2A
      const requestData = {
        jsonrpc: "2.0",
        id: callId,
        method: "message/send",
        params: {
          id: taskId,
          sessionId: sessionId,
          message: {
            role: "user",
            parts: [
              {
                type: "text",
                text: text
              }
            ]
          }
        }
      };

      // AQUI: Use o caminho do proxy e remova as variáveis evoUrl e apiKey daqui
      // O proxy no vite.config.ts já adicionará o header x-api-key
      const response = await fetch('/api', { // Use '/api' para que o proxy do Vite lide com a URL completa e a chave
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // 'x-api-key': import.meta.env.VITE_EVO_AI_API_KEY // Não é mais necessário aqui, o proxy adiciona
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // AQUI: Use o caminho do proxy para o EventSource também
      // O proxy do Vite não lida diretamente com EventSource, então precisamos da URL completa aqui
      // Mas a chave ainda vem do import.meta.env
      const eventSource = new EventSource(`${import.meta.env.VITE_EVO_AI_AGENT_BASE_URL}/stream?taskId=${taskId}&key=${import.meta.env.VITE_EVO_AI_API_KEY}`);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.result?.status?.message?.parts) {
          const responseText = data.result.status.message.parts
            .filter(part => part.type === "text")
            .map(part => part.text)
            .join("");

          setMessages(prev => [...prev.slice(0, -1), { 
            text: responseText, 
            sender: 'bot' 
          }]);
        }

        if (data.result?.final === true) {
          eventSource.close();
          setLoading(false);
        }
      };

      eventSource.onerror = (error) => {
        console.error("Error in SSE:", error);
        eventSource.close();
        setLoading(false);
      };

    } catch (error) {
      console.error('Erro na requisição:', error);
      setMessages(prev => [...prev, { 
        text: `Erro: ${error instanceof Error ? error.message : 'Falha na conexão'}`, 
        sender: 'bot' 
      }]);
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