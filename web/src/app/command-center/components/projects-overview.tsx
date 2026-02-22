'use client';

import { useState, useEffect } from 'react';
import { Plus, ChevronDown, ChevronRight } from 'lucide-react';
import { CC_AGENTS, CC_AGENT_LIST, PROJECT_STATUSES } from '@/lib/command-center-agents';

interface Project {
  id: number;
  name: string;
  description: string;
  status: string;
  assigned_agents: string[];
  created_at: string;
}

export function ProjectsOverview() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [expandedProject, setExpandedProject] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    assignedAgents: [] as string[]
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch('/api/command-center/projects');
      const data = await res.json();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  };

  const createProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/command-center/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (data.project) {
        setProjects([data.project, ...projects]);
        setFormData({ name: '', description: '', assignedAgents: [] });
        setShowForm(false);
      }
    } catch (err) {
      console.error('Failed to create project:', err);
    }
  };

  const updateProjectStatus = async (id: number, status: string) => {
    try {
      await fetch('/api/command-center/projects', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status })
      });
      setProjects(projects.map(p => p.id === id ? { ...p, status } : p));
    } catch (err) {
      console.error('Failed to update project:', err);
    }
  };

  const toggleAgentSelection = (agentId: string) => {
    setFormData(prev => ({
      ...prev,
      assignedAgents: prev.assignedAgents.includes(agentId)
        ? prev.assignedAgents.filter(id => id !== agentId)
        : [...prev.assignedAgents, agentId]
    }));
  };

  const getStatusInfo = (status: string) => {
    return PROJECT_STATUSES.find(s => s.value === status) || PROJECT_STATUSES[0];
  };

  const getStatusIndex = (status: string) => {
    const index = PROJECT_STATUSES.findIndex(s => s.value === status);
    return index === -1 ? 0 : index;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <span>📁</span> Projects Overview
          </h2>
          <p className="text-muted-foreground">Track active work and workflows</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/50 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Project
        </button>
      </div>

      {/* Add Form */}
      {showForm && (
        <form onSubmit={createProject} className="bg-black/30 rounded-xl border border-blue-500/20 p-6 space-y-4">
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Project Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Project name..."
              required
              className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Project description..."
              rows={3}
              className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Assign Agents</label>
            <div className="flex flex-wrap gap-2">
              {CC_AGENT_LIST.map(agent => (
                <button
                  key={agent.id}
                  type="button"
                  onClick={() => toggleAgentSelection(agent.id)}
                  className={`flex items-center gap-1 px-3 py-1 rounded-full border transition-all ${
                    formData.assignedAgents.includes(agent.id)
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
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-6 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/50 rounded-lg transition-colors"
            >
              Create Project
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-6 py-2 bg-slate-500/20 hover:bg-slate-500/30 border border-slate-500/50 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Projects Grid */}
      <div className="grid gap-4">
        {projects.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <span className="text-4xl block mb-2">📂</span>
            <p>No projects yet. Create one to get started.</p>
          </div>
        ) : (
          projects.map(project => {
            const statusInfo = getStatusInfo(project.status);
            const statusIndex = getStatusIndex(project.status);
            const progress = ((statusIndex + 1) / PROJECT_STATUSES.length) * 100;
            const isExpanded = expandedProject === project.id;

            return (
              <div
                key={project.id}
                className="bg-black/30 rounded-xl border border-purple-500/20 overflow-hidden"
              >
                <div
                  className="p-4 cursor-pointer hover:bg-white/5 transition-colors"
                  onClick={() => setExpandedProject(isExpanded ? null : project.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                      <h3 className="font-semibold text-lg">{project.name}</h3>
                      <span className={`px-2 py-0.5 rounded text-xs ${statusInfo.color}`}>
                        {statusInfo.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {project.assigned_agents?.map(agentId => {
                        const agent = CC_AGENTS[agentId];
                        if (!agent) return null;
                        return (
                          <span
                            key={agentId}
                            className={`w-8 h-8 rounded-full flex items-center justify-center ${agent.bgColor} border ${agent.borderColor}`}
                            title={agent.name}
                          >
                            {agent.icon}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                  {/* Progress Bar */}
                  <div className="mt-3 h-1 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-cyan-500 transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>

                {isExpanded && (
                  <div className="border-t border-purple-500/20 p-4 bg-black/20">
                    <p className="text-muted-foreground mb-4">{project.description || 'No description'}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">Status:</span>
                      <div className="flex gap-1">
                        {PROJECT_STATUSES.map((status, idx) => (
                          <button
                            key={status.value}
                            onClick={(e) => {
                              e.stopPropagation();
                              updateProjectStatus(project.id, status.value);
                            }}
                            className={`px-3 py-1 text-xs rounded transition-colors ${
                              project.status === status.value
                                ? `${status.color} border border-current`
                                : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
                            }`}
                          >
                            {status.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
