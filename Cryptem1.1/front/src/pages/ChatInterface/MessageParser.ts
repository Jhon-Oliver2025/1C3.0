class MessageParser {
  actionProvider: any;

  constructor(actionProvider: any) {
    this.actionProvider = actionProvider;
  }

  parse(message: string) {
    console.log('Message received:', message);
  }
}

export default MessageParser;