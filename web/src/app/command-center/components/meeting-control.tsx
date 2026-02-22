'use client';

import { useState, useEffect } from 'react';
import { Plus, Check, Clock, AlertCircle } from 'lucide-react';
import { TOPIC_TYPES, PRIORITY_LEVELS } from '@/lib/command-center-agents';

interface AgendaItem {
  id: number;
  topic_type: string;
  topic_name: string;
  doc_references: string;
  priority: number;
  status: 'pending' | 'addressed' | 'completed';
  created_at: string;
}

export function MeetingControl() {
  const [agendaItems, setAgendaItems] = useState<AgendaItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    topicType: 'research',
    topicName: '',
    docReferences: '',
    priority: 3
  });

  useEffect(() => {
    fetchAgendaItems();
  }, []);

  const fetchAgendaItems = async () => {
    try {
      const res = await fetch('/api/command-center/agenda');
      const data = await res.json();
      setAgendaItems(data.items || []);
    } catch (err) {
      console.error('Failed to fetch agenda items:', err);
    }
  };

  const submitAgendaItem = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/command-center/agenda', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (data.item) {
        setAgendaItems([data.item, ...agendaItems]);
        setFormData({ topicType: 'research', topicName: '', docReferences: '', priority: 3 });
        setShowForm(false);
      }
    } catch (err) {
      console.error('Failed to create agenda item:', err);
    }
  };

  const updateItemStatus = async (id: number, status: string) => {
    try {
      await fetch('/api/command-center/agenda', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status })
      });
      setAgendaItems(agendaItems.map(item =>
        item.id === id ? { ...item, status: status as AgendaItem['status'] } : item
      ));
    } catch (err) {
      console.error('Failed to update item:', err);
    }
  };

  const getPriorityInfo = (level: number) => {
    return PRIORITY_LEVELS.find(p => p.value === level) || PRIORITY_LEVELS[2];
  };

  const getTopicInfo = (type: string) => {
    return TOPIC_TYPES.find(t => t.value === type) || TOPIC_TYPES[0];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <span>📅</span> Meeting Control
          </h2>
          <p className="text-muted-foreground">Inject topics into agent meetings</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Agenda Item
        </button>
      </div>

      {/* Add Form */}
      {showForm && (
        <form onSubmit={submitAgendaItem} className="bg-black/30 rounded-xl border border-amber-500/20 p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-muted-foreground mb-2">Topic Type</label>
              <select
                value={formData.topicType}
                onChange={(e) => setFormData({ ...formData, topicType: e.target.value })}
                className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
              >
                {TOPIC_TYPES.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
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
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Topic Name</label>
            <input
              type="text"
              value={formData.topicName}
              onChange={(e) => setFormData({ ...formData, topicName: e.target.value })}
              placeholder="Enter topic name..."
              required
              className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Document References</label>
            <textarea
              value={formData.docReferences}
              onChange={(e) => setFormData({ ...formData, docReferences: e.target.value })}
              placeholder="Links, file paths, or notes..."
              rows={3}
              className="w-full bg-black/30 border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-6 py-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 rounded-lg transition-colors"
            >
              Add to Agenda
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

      {/* Agenda Items */}
      <div className="space-y-3">
        {agendaItems.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <span className="text-4xl block mb-2">📋</span>
            <p>No agenda items yet. Add one to get started.</p>
          </div>
        ) : (
          agendaItems.map(item => {
            const priorityInfo = getPriorityInfo(item.priority);
            const topicInfo = getTopicInfo(item.topic_type);
            return (
              <div
                key={item.id}
                className={`bg-black/30 rounded-xl border p-4 ${
                  item.status === 'completed'
                    ? 'border-emerald-500/30 opacity-60'
                    : item.status === 'addressed'
                      ? 'border-amber-500/30'
                      : 'border-purple-500/20'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 rounded text-xs ${topicInfo.color} bg-white/5`}>
                        {topicInfo.label}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-xs ${priorityInfo.color} bg-white/5`}>
                        P{item.priority}
                      </span>
                      {item.status === 'pending' && (
                        <span className="flex items-center gap-1 text-xs text-amber-400">
                          <Clock className="w-3 h-3" /> Pending
                        </span>
                      )}
                      {item.status === 'addressed' && (
                        <span className="flex items-center gap-1 text-xs text-cyan-400">
                          <AlertCircle className="w-3 h-3" /> Addressed
                        </span>
                      )}
                      {item.status === 'completed' && (
                        <span className="flex items-center gap-1 text-xs text-emerald-400">
                          <Check className="w-3 h-3" /> Completed
                        </span>
                      )}
                    </div>
                    <h3 className="font-semibold text-lg">{item.topic_name}</h3>
                    {item.doc_references && (
                      <p className="text-sm text-muted-foreground mt-1">{item.doc_references}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {item.status === 'pending' && (
                      <button
                        onClick={() => updateItemStatus(item.id, 'addressed')}
                        className="px-3 py-1 text-sm bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 rounded transition-colors"
                      >
                        Mark Addressed
                      </button>
                    )}
                    {item.status !== 'completed' && (
                      <button
                        onClick={() => updateItemStatus(item.id, 'completed')}
                        className="px-3 py-1 text-sm bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/50 rounded transition-colors"
                      >
                        Complete
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
