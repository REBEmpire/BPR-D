'use client';

import { useState, useEffect } from 'react';
import { Plus, Check, Filter } from 'lucide-react';
import { CC_AGENTS, CC_AGENT_LIST, TASK_STATUSES, PRIORITY_LEVELS } from '@/lib/command-center-agents';

interface Task {
  id: number;
  title: string;
  description: string;
  assigned_agents: string[];
  priority: number;
  status: string;
  created_at: string;
}

export function TaskDashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [filterAgent, setFilterAgent] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assignedAgents: [] as string[],
    priority: 3
  });

  useEffect(() => {
    fetchTasks();
  }, [filterAgent, filterStatus]);

  const fetchTasks = async () => {
    try {
      const params = new URLSearchParams();
      if (filterAgent) params.append('agent', filterAgent);
      if (filterStatus) params.append('status', filterStatus);
      const res = await fetch(`/api/command-center/tasks?${params}`);
      const data = await res.json();
      setTasks(data.tasks || []);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
    }
  };

  const createTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/command-center/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (data.task) {
        setTasks([data.task, ...tasks]);
        setFormData({ title: '', description: '', assignedAgents: [], priority: 3 });
        setShowForm(false);
      }
    } catch (err) {
      console.error('Failed to create task:', err);
    }
  };

  const updateTaskStatus = async (id: number, status: string) => {
    try {
      await fetch('/api/command-center/tasks', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status })
      });
      setTasks(tasks.map(t => t.id === id ? { ...t, status } : t));
    } catch (err) {
      console.error('Failed to update task:', err);
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

  const getPriorityInfo = (level: number) => {
    return PRIORITY_LEVELS.find(p => p.value === level) || PRIORITY_LEVELS[2];
  };

  const getStatusInfo = (status: string) => {
    return TASK_STATUSES.find(s => s.value === status) || TASK_STATUSES[0];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <span>✅</span> Task Dashboard
          </h2>
          <p className="text-muted-foreground">Manage workflow tasks</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Task
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <select
          value={filterAgent}
          onChange={(e) => setFilterAgent(e.target.value)}
          className="bg-black/30 border border-purple-500/30 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-purple-500"
        >
          <option value="">All Agents</option>
          {CC_AGENT_LIST.map(agent => (
            <option key={agent.id} value={agent.id}>{agent.name}</option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="bg-black/30 border border-purple-500/30 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-purple-500"
        >
          <option value="">All Statuses</option>
          {TASK_STATUSES.map(status => (
            <option key={status.value} value={status.value}>{status.label}</option>
          ))}
        </select>
      </div>

      {/* Add Form */}
      {showForm && (
        <form onSubmit={createTask} className="bg-black/30 rounded-xl border border-purple-500/20 p-6 space-y-4">
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Task title..."
              required
              className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Task description..."
              rows={3}
              className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
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
            <div>
              <label className="block text-sm text-muted-foreground mb-2">Priority</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: Number(e.target.value) })}
                className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
              >
                {PRIORITY_LEVELS.map(level => (
                  <option key={level.value} value={level.value}>{level.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-6 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 rounded-lg transition-colors"
            >
              Create Task
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

      {/* Tasks List */}
      <div className="space-y-3">
        {tasks.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <span className="text-4xl block mb-2">📝</span>
            <p>No tasks found. Create one to get started.</p>
          </div>
        ) : (
          tasks.map(task => {
            const priorityInfo = getPriorityInfo(task.priority);
            const statusInfo = getStatusInfo(task.status);
            return (
              <div
                key={task.id}
                className={`bg-black/30 rounded-xl border border-purple-500/20 p-4 ${
                  task.status === 'completed' ? 'opacity-60' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 rounded text-xs ${statusInfo.color}`}>
                        {statusInfo.label}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-xs ${priorityInfo.color} bg-white/5`}>
                        P{task.priority}
                      </span>
                    </div>
                    <h3 className="font-semibold text-lg">{task.title}</h3>
                    {task.description && (
                      <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      {task.assigned_agents?.map(agentId => {
                        const agent = CC_AGENTS[agentId];
                        if (!agent) return null;
                        return (
                          <span
                            key={agentId}
                            className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${agent.bgColor} ${agent.color}`}
                          >
                            {agent.icon} {agent.name}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {task.status !== 'completed' && (
                      <button
                        onClick={() => updateTaskStatus(task.id, 'completed')}
                        className="p-2 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/50 rounded transition-colors"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
