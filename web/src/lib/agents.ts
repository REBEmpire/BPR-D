import agentsData from '@/content/agents.json';
import { remark } from 'remark';
import html from 'remark-html';

export interface Agent {
  id: string;
  name: string;
  slug: string;
  role: string;
  bio: string;
  videoUrl: string;
  points?: number; // Will be hydrated from DB client-side or server-side
}

export async function getAgents(): Promise<Agent[]> {
  // In a real app, we might fetch points here from DB
  return agentsData as Agent[];
}

export async function getAgent(slug: string): Promise<Agent | undefined> {
  const agent = (agentsData as Agent[]).find(a => a.slug === slug);
  if (!agent) return undefined;

  // Process markdown bio to HTML
  const processedContent = await remark()
    .use(html)
    .process(agent.bio);

  return {
    ...agent,
    bio: processedContent.toString()
  };
}
