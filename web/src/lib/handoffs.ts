import { Octokit } from "@octokit/rest";

const REPO_OWNER = "REBEmpire";
const REPO_NAME = "BPR-D";

export interface AgentHandoff {
  agentName: string;
  handoffContent: string | null;
  tasksCompletedContent: string | null;
}

export async function getAgentHandoffs(agentName: string): Promise<AgentHandoff> {
  const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN, // Will use server-side env var
  });

  let handoffContent = null;
  let tasksCompletedContent = null;

  try {
    // 1. Get Handoff
    try {
      const handoffRes = await octokit.rest.repos.getContent({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        path: `_agents/${agentName}/handoff.md`,
      });

      if (!Array.isArray(handoffRes.data) && "content" in handoffRes.data) {
        handoffContent = Buffer.from(handoffRes.data.content, "base64").toString("utf-8");
      }
    } catch (e) {
      console.warn(`Could not fetch handoff for ${agentName}`);
    }

    // 2. Get Tasks Completed
    try {
      const tasksRes = await octokit.rest.repos.getContent({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        path: `_agents/${agentName}/tasks-completed.md`,
      });

      if (!Array.isArray(tasksRes.data) && "content" in tasksRes.data) {
        tasksCompletedContent = Buffer.from(tasksRes.data.content, "base64").toString("utf-8");
      }
    } catch (e) {
        // It is possible this file does not exist yet, which is fine.
    }

  } catch (error) {
    console.error(`Error fetching agent data for ${agentName}:`, error);
  }

  return {
    agentName,
    handoffContent,
    tasksCompletedContent,
  };
}
