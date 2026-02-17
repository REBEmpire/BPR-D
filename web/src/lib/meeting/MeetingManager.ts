/* eslint-disable @typescript-eslint/no-explicit-any */
import fs from 'fs';
import path from 'path';
import { GrokAgent } from '../ai-agents/grok';
import { ClaudeAgent } from '../ai-agents/claude';
import { GeminiAgent } from '../ai-agents/gemini';
import { AbacusAgent } from '../ai-agents/abacus';

export interface Message {
  id: string;
  sender: 'user' | 'grok' | 'claude' | 'gemini' | 'abacus' | 'system';
  content: string;
  timestamp: number;
  type: 'text' | 'decision_request' | 'file_update';
  metadata?: any;
}

export interface MeetingState {
  id: string;
  topic: string;
  status: 'idle' | 'active' | 'paused' | 'completed';
  participants: string[];
  transcript: Message[];
  currentTurn: string | null;
  pendingDecision: {
    id: string;
    description: string;
    options: string[];
  } | null;
}

const DATA_DIR = path.join(process.cwd(), 'data');
const STATE_FILE = path.join(DATA_DIR, 'active_meeting.json');

export class MeetingManager {
  private state: MeetingState;
  private agents: {
    grok: GrokAgent;
    claude: ClaudeAgent;
    gemini: GeminiAgent;
    abacus: AbacusAgent;
  };

  constructor() {
    this.agents = {
      grok: new GrokAgent(),
      claude: new ClaudeAgent(),
      gemini: new GeminiAgent(),
      abacus: new AbacusAgent(),
    };
    this.state = this.loadState();
  }

  private loadState(): MeetingState {
    if (fs.existsSync(STATE_FILE)) {
      try {
        return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
      } catch (e) {
        console.error('Failed to load meeting state:', e);
      }
    }
    return this.getInitialState();
  }

  private getInitialState(): MeetingState {
    return {
      id: Date.now().toString(),
      topic: '',
      status: 'idle',
      participants: ['grok', 'claude', 'gemini', 'abacus'],
      transcript: [],
      currentTurn: null,
      pendingDecision: null,
    };
  }

  private saveState() {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    fs.writeFileSync(STATE_FILE, JSON.stringify(this.state, null, 2));
  }

  public async startMeeting(topic: string) {
    this.state = this.getInitialState();
    this.state.status = 'active';
    this.state.topic = topic;
    this.addMessage('system', `Meeting started: ${topic}`);
    this.saveState();

    // Initial kick-off by Grok (Chief)
    // Relay Logic Step 1: Grok sets the plan
    await this.processTurn('grok',
        `We are here to execute a relay mission on the topic: "${topic}". \n` +
        `Your goal is to define the HIGH LEVEL PLAN and STRATEGY. \n` +
        `Do not write code yet. Outline the steps for Claude and the others.`
    );
  }

  public async processTurn(agentName: string, inputContext?: string) {
    this.state.currentTurn = agentName;
    this.saveState();

    const agent = this.agents[agentName as keyof typeof this.agents];
    if (!agent) {
      console.error(`Agent ${agentName} not found`);
      return;
    }

    // Construct context from transcript
    const history = this.state.transcript.map(m => ({
      role: m.sender === 'user' || m.sender === 'system' ? 'user' : 'assistant',
      content: `${m.sender.toUpperCase()}: ${m.content}`
    }));

    // Inject Relay Instructions based on Role if not provided manually
    let contextToUse = inputContext;
    if (!contextToUse) {
        switch(agentName) {
            case 'grok':
                contextToUse = "Review the feedback. Adjust the plan if needed, or give the go-ahead for the next phase.";
                break;
            case 'claude':
                contextToUse = "Review Grok's plan. Provide detailed ARCHITECTURE, FILE STRUCTURE, and SAFETY/SECURITY analysis. Identify potential pitfalls.";
                break;
            case 'gemini':
                contextToUse = "Review the plan and architecture. You are the IMPLEMENTER. Provide specific code snippets, file contents, or commands. Focus on 'getting it done'.";
                break;
            case 'abacus':
                contextToUse = "Review everything. You are the INNOVATOR and QA. Suggest optimizations, catch edge cases, or draft the final documentation/handoffs.";
                break;
        }
    }

    if (contextToUse) {
        history.push({ role: 'user', content: `(System Instruction): ${contextToUse}` });
    }

    // Call Agent
    let response = '';
    try {
        if (agentName === 'gemini') {
             const geminiHistory = history.map(h => ({
                 role: h.role === 'assistant' ? 'model' : 'user',
                 parts: [{ text: h.content }]
             }));
             response = await (agent as GeminiAgent).sendMessage(geminiHistory as any);
        } else {
             response = await (agent as any).sendMessage(history);
        }
    } catch (e) {
        response = `[Error generating response: ${e}]`;
    }

    this.addMessage(agentName as any, response);

    // Auto-handoff logic
    const nextAgent = this.getNextAgent(agentName);

    if (nextAgent) {
        if (nextAgent === 'grok') {
            // End of round -> Wait for User
            this.state.currentTurn = null;
            this.addMessage('system', 'Round complete. Awaiting Chief approval to proceed.');
        } else {
            // Automatically trigger next agent in chain
            // We use a slight delay or just await to keep it synchronous for this MVP
            await this.processTurn(nextAgent);
        }
    }

    this.saveState();
  }

  private getNextAgent(current: string): string | null {
      const order = ['grok', 'claude', 'gemini', 'abacus'];
      const idx = order.indexOf(current);
      if (idx === -1 || idx === order.length - 1) return 'grok';
      return order[idx + 1];
  }

  public addMessage(sender: Message['sender'], content: string, type: Message['type'] = 'text') {
    const msg: Message = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      sender,
      content,
      timestamp: Date.now(),
      type
    };
    this.state.transcript.push(msg);
    this.saveState();
  }

  public getState() {
      return this.state;
  }

  public async userFeedback(approved: boolean, comment?: string) {
      this.addMessage('user', `User Feedback: ${approved ? 'YES/PROCEED' : 'NO/STOP'}. ${comment || ''}`);

      if (approved) {
          await this.processTurn('grok',
            comment ? `The user approved with comment: "${comment}". Incorporate this into the plan and proceed.` : "The user approved. Proceed with the next iteration."
          );
      } else {
          this.state.status = 'paused';
          this.addMessage('system', 'Meeting paused by user.');
          this.saveState();
      }
  }
}
