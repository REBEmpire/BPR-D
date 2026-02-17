import OpenAI from 'openai';

export class AbacusAgent {
  private client: OpenAI;
  private model: string;

  constructor() {
    this.client = new OpenAI({
      baseURL: 'https://routellm.abacus.ai/v1',
      apiKey: process.env.ABACUS_PRIMARY_KEY || process.env.ABACUS_BACKUP_KEY,
    });
    this.model = 'gpt-5'; // Default or as configured
  }

  async sendMessage(messages: { role: 'system' | 'user' | 'assistant'; content: string }[]) {
    try {
      const response = await this.client.chat.completions.create({
        model: this.model,
        messages: messages,
      });
      return response.choices[0].message.content;
    } catch (error) {
      console.error('Abacus Agent Error:', error);
      throw error;
    }
  }
}
