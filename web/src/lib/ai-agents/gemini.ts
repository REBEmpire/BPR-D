import { GoogleGenerativeAI } from '@google/generative-ai';

export class GeminiAgent {
  private client: GoogleGenerativeAI;
  private model: string;

  constructor() {
    this.client = new GoogleGenerativeAI(process.env.GOOGLE_AI_API_KEY || process.env.GEMINI_API_KEY || '');
    this.model = 'gemini-1.5-pro-latest';
  }

  async sendMessage(messages: { role: 'user' | 'model'; parts: { text: string }[] }[]) {
    try {
      const model = this.client.getGenerativeModel({ model: this.model });
      // Transform messages to Gemini format
      const history = messages.slice(0, -1).map(m => ({
        role: m.role,
        parts: m.parts
      }));

      const chat = model.startChat({
        history: history,
      });
      const lastMessage = messages[messages.length - 1];
      const result = await chat.sendMessage(lastMessage.parts[0].text);
      return result.response.text();
    } catch (error) {
      console.error('Gemini Agent Error:', error);
      throw error;
    }
  }
}
