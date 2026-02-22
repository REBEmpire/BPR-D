'use client';

import { useState, useEffect, useRef } from 'react';
import { Send, Plus, Trash2 } from 'lucide-react';
import { CC_AGENTS, CC_AGENT_LIST, type Agent } from '@/lib/command-center-agents';

interface ChatMessage {
  id: number;
  agent_name: string | null;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
}

interface ChatSession {
  id: number;
  title: string;
  participants: string[];
  created_at: string;
}

export function ChatInterface() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [selectedAgents, setSelectedAgents] = useState<string[]>(['grok', 'claude', 'abacus', 'gemini']);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (activeSession) {
      fetchMessages(activeSession.id);
    }
  }, [activeSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const res = await fetch('/api/command-center/chat/sessions');
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    }
  };

  const fetchMessages = async (sessionId: number) => {
    try {
      const res = await fetch(`/api/command-center/chat/messages?sessionId=${sessionId}`);
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  };

  const createSession = async () => {
    try {
      const res = await fetch('/api/command-center/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ participants: selectedAgents })
      });
      const data = await res.json();
      if (data.session) {
        setSessions([data.session, ...sessions]);
        setActiveSession(data.session);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const deleteSession = async (sessionId: number) => {
    try {
      await fetch(`/api/command-center/chat/sessions?id=${sessionId}`, { method: 'DELETE' });
      setSessions(sessions.filter(s => s.id !== sessionId));
      if (activeSession?.id === sessionId) {
        setActiveSession(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !activeSession || selectedAgents.length === 0) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      agent_name: null,
      content: input,
      role: 'user',
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/command-center/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: activeSession.id,
          message: input,
          agents: selectedAgents
        })
      });

      const data = await res.json();
      if (data.responses) {
        setMessages(prev => [...prev, ...data.responses]);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAgent = (agentId: string) => {
    setSelectedAgents(prev =>
      prev.includes(agentId)
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  return (
    <div className="h-full flex gap-4">
      {/* Sessions Sidebar */}
      <div className="w-64 bg-black/30 rounded-xl border border-purple-500/20 flex flex-col">
        <div className="p-4 border-b border-purple-500/20">
          <button
            onClick={createSession}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Session
          </button>
        </div>
        <div className="flex-1 overflow-auto p-2 space-y-1">
          {sessions.map(session => (
            <div
              key={session.id}
              className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors ${
                activeSession?.id === session.id
                  ? 'bg-purple-500/20 border border-purple-500/30'
                  : 'hover:bg-white/5'
              }`}
              onClick={() => setActiveSession(session)}
            >
              <span className="text-sm truncate flex-1">{session.title || `Session ${session.id}`}</span>
              <button
                onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }}
                className="p-1 hover:bg-red-500/20 rounded"
              >
                <Trash2 className="w-3 h-3 text-red-400" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-black/30 rounded-xl border border-purple-500/20">
        {/* Agent Selector */}
        <div className="p-4 border-b border-purple-500/20">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm text-muted-foreground">Participants:</span>
            {CC_AGENT_LIST.map(agent => (
              <button
                key={agent.id}
                onClick={() => toggleAgent(agent.id)}
                className={`flex items-center gap-1 px-3 py-1 rounded-full border transition-all ${
                  selectedAgents.includes(agent.id)
                    ? `${agent.bgColor} ${agent.borderColor} ${agent.color}`
                    : 'bg-slate-800/50 border-slate-700 text-slate-400'
                }`}
              >
                <span>{agent.icon}</span>
                <span className="text-sm">{agent.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {!activeSession ? (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <span className="text-4xl block mb-2">🜃</span>
                <p>Select or create a session to begin</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <span className="text-4xl block mb-2">✨</span>
                <p>Start the conversation with your agents</p>
              </div>
            </div>
          ) : (
            messages.map(msg => {
              const agent = msg.agent_name ? CC_AGENTS[msg.agent_name] : null;
              return (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] p-4 rounded-xl ${
                      msg.role === 'user'
                        ? 'bg-purple-500/20 border border-purple-500/30'
                        : agent
                          ? `${agent.bgColor} ${agent.borderColor} border`
                          : 'bg-slate-800/50 border border-slate-700'
                    }`}
                  >
                    {agent && (
                      <div className={`flex items-center gap-2 mb-2 ${agent.color}`}>
                        <span>{agent.icon}</span>
                        <span className="font-semibold">{agent.name}</span>
                        <span className="text-xs opacity-60">{agent.role}</span>
                      </div>
                    )}
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              );
            })
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800/50 border border-slate-700 p-4 rounded-xl">
                <div className="flex items-center gap-2">
                  <span className="animate-pulse">✨</span>
                  <span className="text-muted-foreground">Agents are thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={sendMessage} className="p-4 border-t border-purple-500/20">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={activeSession ? "Message your agents..." : "Create a session first..."}
              disabled={!activeSession || isLoading}
              className="flex-1 bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!activeSession || isLoading || !input.trim()}
              className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 rounded-lg transition-colors disabled:opacity-50"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
