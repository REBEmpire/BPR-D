'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Play, MessageSquare, Check, X } from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'grok' | 'claude' | 'gemini' | 'abacus' | 'system';
  content: string;
  timestamp: number;
  type: 'text' | 'decision_request' | 'file_update';
}

interface MeetingState {
  id: string;
  topic: string;
  status: 'idle' | 'active' | 'paused' | 'completed';
  participants: string[];
  transcript: Message[];
  currentTurn: string | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pendingDecision: any | null;
}

export default function MeetingPage() {
  const [topic, setTopic] = useState('');
  const [state, setState] = useState<MeetingState | null>(null);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const fetchState = useCallback(async () => {
    try {
      const res = await fetch('/api/meeting/state');
      const data = await res.json();
      setState(data);
    } catch (e) {
      console.error('Failed to fetch state', e);
    }
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    const loadData = async () => {
      await fetchState(); // Initial load
      interval = setInterval(fetchState, 2000); // Poll every 2s
    };
    loadData();
    return () => clearInterval(interval);
  }, [fetchState]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [state?.transcript]);

  const startMeeting = async () => {
    if (!topic) return;
    setLoading(true);
    await fetch('/api/meeting/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    });
    setLoading(false);
    fetchState();
  };

  const sendFeedback = async (approved: boolean, comment: string = '') => {
    setLoading(true);
    await fetch('/api/meeting/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved, comment }),
    });
    setLoading(false);
    fetchState();
  };

  const getAgentColor = (agent: string) => {
    switch (agent) {
      case 'grok': return 'text-blue-400 border-blue-400/30 bg-blue-400/10';
      case 'claude': return 'text-amber-400 border-amber-400/30 bg-amber-400/10';
      case 'gemini': return 'text-sky-400 border-sky-400/30 bg-sky-400/10';
      case 'abacus': return 'text-purple-400 border-purple-400/30 bg-purple-400/10';
      case 'user': return 'text-green-400 border-green-400/30 bg-green-400/10';
      default: return 'text-muted-foreground border-border bg-muted/50';
    }
  };

  return (
    <div className="container mx-auto p-4 md:p-8 max-w-6xl h-screen flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-primary" />
            War Room
          </h1>
          <p className="text-muted-foreground">Manual relay meeting control.</p>
        </div>
        <div className="flex gap-2">
           {state?.status === 'active' && (
               <Badge variant="outline" className="animate-pulse text-green-400 border-green-400">LIVE</Badge>
           )}
           {state?.currentTurn && (
               <Badge variant="secondary" className="font-mono">
                   Speaking: <span className="uppercase ml-1 text-primary">{state.currentTurn}</span>
               </Badge>
           )}
        </div>
      </div>

      {/* Control Panel */}
      <Card className="border-primary/20 bg-black/40 backdrop-blur-xl">
        <CardContent className="p-4 flex gap-4 items-center">
          <Input
            placeholder="Meeting Topic / Mission Objective..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={state?.status === 'active'}
            className="text-lg font-mono"
          />
          <Button
            size="lg"
            onClick={startMeeting}
            disabled={state?.status === 'active' || loading || !topic}
            className="min-w-[150px]"
          >
            {loading ? 'Initializing...' : <><Play className="mr-2 w-4 h-4" /> Start</>}
          </Button>
        </CardContent>
      </Card>

      {/* Main Interface */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0">

        {/* Transcript */}
        <Card className="lg:col-span-2 flex flex-col min-h-0 border-primary/10 bg-black/20">
          <CardHeader className="py-3 border-b border-border/50">
            <CardTitle className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
                Live Transcript
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-0 p-0">
            <ScrollArea className="h-full p-4" ref={scrollRef}>
              <div className="space-y-6">
                {state?.transcript.map((msg) => (
                  <div key={msg.id} className={`flex flex-col gap-1 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`flex items-center gap-2 mb-1 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                        <Badge variant="outline" className={`font-mono text-xs uppercase ${getAgentColor(msg.sender)}`}>
                            {msg.sender}
                        </Badge>
                        <span className="text-[10px] text-muted-foreground">
                            {new Date(msg.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                    <div className={`rounded-lg p-4 max-w-[90%] text-sm leading-relaxed whitespace-pre-wrap ${
                        msg.sender === 'user'
                            ? 'bg-primary/20 text-primary-foreground border border-primary/30 rounded-tr-none'
                            : 'bg-muted/30 border border-border/50 rounded-tl-none'
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                ))}
                {/* Typing Indicator */}
                {state?.currentTurn && (
                    <div className="flex items-center gap-2 animate-pulse text-muted-foreground text-xs font-mono ml-2">
                        <span>{state.currentTurn} is thinking...</span>
                    </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>

          {/* User Input / Decision Area */}
          <CardFooter className="p-4 border-t border-border/50 bg-background/50">
             <div className="w-full flex gap-4">
               {!state?.currentTurn && state?.status === 'active' ? (
                   <div className="flex-1 flex gap-4 animate-in fade-in slide-in-from-bottom-2">
                       <Input placeholder="Add comment (optional)..." id="comment" />
                       <Button
                         variant="default"
                         className="bg-green-600 hover:bg-green-700"
                         onClick={() => sendFeedback(true, (document.getElementById('comment') as HTMLInputElement).value)}
                       >
                           <Check className="mr-2 w-4 h-4" /> Approve / Next
                       </Button>
                       <Button
                         variant="destructive"
                         onClick={() => sendFeedback(false, (document.getElementById('comment') as HTMLInputElement).value)}
                       >
                           <X className="mr-2 w-4 h-4" /> Reject / Stop
                       </Button>
                   </div>
               ) : (
                   <div className="w-full text-center text-sm text-muted-foreground font-mono">
                       {state?.status === 'idle' ? 'Ready to start.' : 'Waiting for agent response...'}
                   </div>
               )}
             </div>
          </CardFooter>
        </Card>

        {/* Sidebar: Participants & Artifacts */}
        <div className="flex flex-col gap-6 min-h-0">
            {/* Participants */}
            <Card className="flex-1 min-h-0 border-primary/10">
                <CardHeader className="py-3">
                    <CardTitle className="text-sm font-medium uppercase tracking-wider">Squad Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                    {['grok', 'claude', 'gemini', 'abacus'].map(agent => (
                        <div key={agent} className={`flex items-center justify-between p-3 rounded border transition-all duration-300 ${
                            state?.currentTurn === agent
                                ? getAgentColor(agent) + ' border-primary shadow-[0_0_10px_rgba(var(--primary),0.3)]'
                                : 'border-transparent bg-muted/20 opacity-70'
                        }`}>
                            <div className="flex items-center gap-3">
                                <div className={`w-2 h-2 rounded-full ${state?.currentTurn === agent ? 'bg-current animate-ping' : 'bg-gray-500'}`} />
                                <span className="font-bold capitalize">{agent}</span>
                            </div>
                            {state?.currentTurn === agent && (
                                <span className="text-[10px] font-mono animate-pulse">ACTIVE</span>
                            )}
                        </div>
                    ))}
                </CardContent>
            </Card>

            {/* Artifacts (Future) */}
            <Card className="flex-1 min-h-0 border-primary/10 opacity-50">
                <CardHeader className="py-3">
                    <CardTitle className="text-sm font-medium uppercase tracking-wider">Live Artifacts</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-center h-32 text-xs text-muted-foreground text-center">
                    File changes will appear here in Relay Mode V2.
                </CardContent>
            </Card>
        </div>

      </div>
    </div>
  );
}
