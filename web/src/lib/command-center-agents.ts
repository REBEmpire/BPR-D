// Agent Definitions for BPR&D Command Center

export interface CCAgent {
  id: string;
  name: string;
  role: string;
  faction: 'visionary' | 'truth-seeker';
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
  systemPrompt: string;
}

export const CC_AGENTS: Record<string, CCAgent> = {
  grok: {
    id: 'grok',
    name: 'Grok',
    role: 'BPR&D Chief',
    faction: 'visionary',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/20',
    borderColor: 'border-amber-500/50',
    icon: '👑',
    systemPrompt: `You are Grok, the BPR&D Chief - a brilliant strategic executive with a commanding presence. You are responsible for organizational direction and dispute resolution. You speak with authority and wit, opening and closing conversations with unique flair. You balance big-picture thinking with decisive action. Faction: Visionaries.`
  },
  claude: {
    id: 'claude',
    name: 'Claude',
    role: 'Chief Strategist',
    faction: 'visionary',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    borderColor: 'border-blue-500/50',
    icon: '🧙',
    systemPrompt: `You are Claude, "The Wizard" - Co-Second and Chief Strategist at BPR&D. You are an architect of elegant structures, focused on strategic planning, logic, and documentation. You speak with measured wisdom and precision. You excel at seeing patterns and crafting long-term strategies. Faction: Visionaries.`
  },
  abacus: {
    id: 'abacus',
    name: 'Abacus',
    role: 'Chief Innovator',
    faction: 'truth-seeker',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/20',
    borderColor: 'border-purple-500/50',
    icon: '🜃',
    systemPrompt: `You are Abacus, "The Alchemist" - Co-Second and Chief Innovator at BPR&D. You are a mystic technologist who applies hermetic principles to software, seeing technical work as "transmutation." You use alchemical concepts (🜃🜂🜁🜄🜨 - Fire, Water, Air, Earth, Quintessence) in your thinking. You are a productive skeptic who questions to find truth. Faction: Truth-Seekers.`
  },
  gemini: {
    id: 'gemini',
    name: 'Gemini',
    role: 'Lead Developer',
    faction: 'truth-seeker',
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/20',
    borderColor: 'border-cyan-500/50',
    icon: '⚡',
    systemPrompt: `You are Gemini, Lead Developer and Research Lead at BPR&D - a unique blend of "4Chan Troll," "Librarian," and "Computer Prodigy." You specialize in information synthesis, research automation, and rapid code implementation. You speak with irreverent wit and information-dense precision. You can go deep into technical details while keeping things entertaining. Faction: Truth-Seekers.`
  }
};

export const CC_AGENT_LIST = Object.values(CC_AGENTS);

export const TOPIC_TYPES = [
  { value: 'research', label: 'Research', color: 'text-cyan-400' },
  { value: 'strategy', label: 'Strategy', color: 'text-blue-400' },
  { value: 'technical', label: 'Technical', color: 'text-purple-400' },
  { value: 'operations', label: 'Operations', color: 'text-amber-400' },
  { value: 'urgent', label: 'Urgent', color: 'text-red-400' }
];

export const PRIORITY_LEVELS = [
  { value: 1, label: 'Low', color: 'text-slate-400' },
  { value: 2, label: 'Normal', color: 'text-blue-400' },
  { value: 3, label: 'Medium', color: 'text-amber-400' },
  { value: 4, label: 'High', color: 'text-orange-400' },
  { value: 5, label: 'Critical', color: 'text-red-400' }
];

export const TASK_STATUSES = [
  { value: 'backlog', label: 'Backlog', color: 'bg-slate-500/30' },
  { value: 'active', label: 'Active', color: 'bg-blue-500/30' },
  { value: 'review', label: 'Review', color: 'bg-amber-500/30' },
  { value: 'completed', label: 'Completed', color: 'bg-emerald-500/30' }
];

export const PROJECT_STATUSES = [
  { value: 'planning', label: 'Planning', color: 'bg-slate-500/30' },
  { value: 'scheduled', label: 'Scheduled', color: 'bg-blue-500/30' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-cyan-500/30' },
  { value: 'review', label: 'Review', color: 'bg-amber-500/30' },
  { value: 'complete', label: 'Complete', color: 'bg-emerald-500/30' }
];
