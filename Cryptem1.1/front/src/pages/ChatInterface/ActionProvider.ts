class ActionProvider {
  createChatBotMessage: any;

  constructor(createChatBotMessage: any) {
    this.createChatBotMessage = createChatBotMessage;
  }

  handleMessage(message: string) {
    console.log('ActionProvider handling message:', message);
  }
}

export default ActionProvider;