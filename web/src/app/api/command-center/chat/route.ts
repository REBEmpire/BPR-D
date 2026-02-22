import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { CC_AGENTS } from '@/lib/command-center-agents';
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize LLM clients
const xai = process.env.XAI_API_KEY ? new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: 'https://api.x.ai/v1'
}) : null;

const anthropic = process.env.ANTHROPIC_API_KEY ? new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
}) : null;

const gemini = process.env.GEMINI_API_KEY ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY) : null;

async function getAgentResponse(agentId: string, message: string, history: Array<{role: string, content: string}>) {
  const agent = CC_AGENTS[agentId];
  if (!agent) return null;

  const systemPrompt = agent.systemPrompt;
  const messagesForLLM = history.map(m => ({
    role: m.role as 'user' | 'assistant',
    content: m.content
  }));

  try {
    // Use Grok (xAI) for Grok agent
    if (agentId === 'grok' && xai) {
      const completion = await xai.chat.completions.create({
        model: 'grok-2-latest',
        messages: [
          { role: 'system', content: systemPrompt },
          ...messagesForLLM,
          { role: 'user', content: message }
        ],
        max_tokens: 1000
      });
      return completion.choices[0]?.message?.content || '';
    }

    // Use Claude for Claude agent
    if (agentId === 'claude' && anthropic) {
      const completion = await anthropic.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: systemPrompt,
        messages: [
          ...messagesForLLM.map(m => ({ role: m.role as 'user' | 'assistant', content: m.content })),
          { role: 'user', content: message }
        ]
      });
      const textBlock = completion.content.find(b => b.type === 'text');
      return textBlock ? textBlock.text : '';
    }

    // Use Gemini for Gemini agent
    if (agentId === 'gemini' && gemini) {
      const model = gemini.getGenerativeModel({ model: 'gemini-2.0-flash' });
      const chat = model.startChat({
        history: messagesForLLM.map(m => ({
          role: m.role === 'assistant' ? 'model' : 'user',
          parts: [{ text: m.content }]
        }))
      });
      const result = await chat.sendMessage(`${systemPrompt}\n\nUser: ${message}`);
      return result.response.text();
    }

    // Use Abacus/xAI fallback for Abacus agent
    if (agentId === 'abacus' && xai) {
      const completion = await xai.chat.completions.create({
        model: 'grok-2-latest',
        messages: [
          { role: 'system', content: systemPrompt },
          ...messagesForLLM,
          { role: 'user', content: message }
        ],
        max_tokens: 1000
      });
      return completion.choices[0]?.message?.content || '';
    }

    // Fallback: use any available LLM
    if (xai) {
      const completion = await xai.chat.completions.create({
        model: 'grok-2-latest',
        messages: [
          { role: 'system', content: systemPrompt },
          ...messagesForLLM,
          { role: 'user', content: message }
        ],
        max_tokens: 1000
      });
      return completion.choices[0]?.message?.content || '';
    }

    return `[${agent.name} is currently unavailable - no API key configured]`;
  } catch (error) {
    console.error(`Error getting response from ${agentId}:`, error);
    return `[${agent.name} encountered an error]`;
  }
}

export async function POST(request: NextRequest) {
  try {
    const { sessionId, message, agents } = await request.json();

    if (!sessionId || !message || !agents || agents.length === 0) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Save user message
    await query(
      'INSERT INTO chat_messages (session_id, agent_name, content, role) VALUES ($1, $2, $3, $4)',
      [sessionId, null, message, 'user']
    );

    // Get message history
    const historyResult = await query(
      'SELECT agent_name, content, role FROM chat_messages WHERE session_id = $1 ORDER BY created_at',
      [sessionId]
    );
    const history = historyResult.rows.map(row => ({
      role: row.role,
      content: row.agent_name ? `[${row.agent_name}]: ${row.content}` : row.content
    }));

    // Get responses from each selected agent
    const responses = [];
    for (const agentId of agents) {
      const responseContent = await getAgentResponse(agentId, message, history);
      if (responseContent) {
        // Save agent response
        const result = await query(
          'INSERT INTO chat_messages (session_id, agent_name, content, role) VALUES ($1, $2, $3, $4) RETURNING id, created_at',
          [sessionId, agentId, responseContent, 'assistant']
        );
        responses.push({
          id: result.rows[0].id,
          agent_name: agentId,
          content: responseContent,
          role: 'assistant',
          created_at: result.rows[0].created_at
        });

        // Add to history for next agent
        history.push({ role: 'assistant', content: `[${agentId}]: ${responseContent}` });
      }
    }

    // Log activity
    await query(
      'INSERT INTO cc_activity (action_type, description, agent_name) VALUES ($1, $2, $3)',
      ['chat', `Chat message from ${agents.join(', ')}`, agents[0]]
    );

    return NextResponse.json({ responses });
  } catch (error) {
    console.error('Chat error:', error);
    return NextResponse.json({ error: 'Failed to process chat' }, { status: 500 });
  }
}
