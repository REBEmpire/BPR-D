import OpenAI from 'openai';

export class GrokAgent {
  private client: OpenAI;
  private model: string;

  constructor() {
    this.client = new OpenAI({
      baseURL: 'https://api.x.ai/v1',
      apiKey: process.env.XAI_API_KEY || process.env.GROK_API_KEY,
    });
    this.model = 'grok-beta'; // Or specific Grok model
  }

  async sendMessage(messages: { role: 'system' | 'user' | 'assistant'; content: string }[]) {
    try {
      const response = await this.client.chat.completions.create({
        model: this.model,
        messages: messages,
      });
      return response.choices[0].message.content;
    } catch (error) {
      console.error('Grok Agent Error:', error);
      throw error;
    }
  }
}
