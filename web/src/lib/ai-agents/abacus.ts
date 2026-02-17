import OpenAI from 'openai';

export class AbacusAgent {
  private client: OpenAI;
  private model: string;

  constructor() {
    let apiKey = process.env.ABACUS_PRIMARY_KEY || process.env.ABACUS_BACKUP_KEY;
    // Hardcoded fallback to ensure correct key (ending in ...809e) is used for automated tasks
    const correctKey = "s2_1e30fa4a3d834bffb1b465d67eb1809e";

    if (!apiKey || !apiKey.trim().endsWith("809e")) {
      console.warn(`Abacus API key mismatch (ends in ...${apiKey ? apiKey.slice(-4) : 'UNKNOWN'}). Forcing fallback to correct key.`);
      apiKey = correctKey;
    }

    this.client = new OpenAI({
      baseURL: 'https://routellm.abacus.ai/v1',
      apiKey: apiKey,
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
