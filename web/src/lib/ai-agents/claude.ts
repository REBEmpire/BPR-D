import Anthropic from '@anthropic-ai/sdk';

export class ClaudeAgent {
  private client: Anthropic;
  private model: string;

  constructor() {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    this.model = 'claude-3-opus-20240229'; // Or latest available
  }

  async sendMessage(messages: { role: 'user' | 'assistant'; content: string }[]) {
    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 4096,
        messages: messages.map(m => ({
          role: m.role as 'user' | 'assistant',
          content: m.content
        })),
      });
      if (response.content[0].type === 'text') {
        return response.content[0].text;
      }
      return '';
    } catch (error) {
      console.error('Claude Agent Error:', error);
      throw error;
    }
  }
}
