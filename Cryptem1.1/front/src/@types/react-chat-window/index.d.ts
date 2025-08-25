declare module 'react-chat-window' {
  import React from 'react';
  
  interface Message {
    author: string;
    type: string;
    data: {
      text: string;
      [key: string]: any;
    };
  }

  interface LauncherProps {
    agentProfile: {
      teamName: string;
      imageUrl: string;
    };
    onMessageWasSent: (message: string) => void;
    messageList: Message[];
    showEmoji: boolean;
    isOpen: boolean;
    handleClick: () => void;
    style: React.CSSProperties;
  }

  export class Launcher extends React.Component<LauncherProps> {}
}