declare module 'react-chatbot-kit' {
  import React from 'react';
  
  interface Config {
    botName: string;
    initialMessages: Array<{
      message: string;
      type: string;
      widget?: string;
    }>;
    widgets?: any[];
  }

  export interface ChatBotProps {
    config: Config;
    messageParser: any;
    actionProvider: any;
  }

  const ChatBot: React.FC<ChatBotProps>;
  export default ChatBot;
}