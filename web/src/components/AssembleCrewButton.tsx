'use client';

import { useState } from 'react';
import { assembleTheCrew } from '@/app/actions/assemble';

export default function AssembleCrewButton() {
  const [task, setTask] = useState('');
  const [criteria, setCriteria] = useState('');
  const [status, setStatus] = useState('');

  const handleSubmit = async (formData: FormData) => {
    setStatus('Assembling crew...');
    const result = await assembleTheCrew(formData);
    setStatus(result.success ? '✅ Crew assembled! (check console for now)' : '❌ Failed');
  };

  return (
    <form action={handleSubmit} className="space-y-4 p-6 border rounded-xl bg-card">
      <div>
        <label className="block text-sm font-medium mb-1">Task</label>
        <input
          type="text"
          name="task"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          required
          className="w-full p-3 border rounded-lg bg-background"
          placeholder="Describe the task..."
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Success Criteria</label>
        <textarea
          name="successCriteria"
          value={criteria}
          onChange={(e) => setCriteria(e.target.value)}
          required
          className="w-full p-3 border rounded-lg h-24 bg-background"
          placeholder="What does success look like?"
        />
      </div>
      <button
        type="submit"
        className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-semibold hover:opacity-90 transition shadow-lg"
      >
        Assemble the Crew (Grok + Harper + Benjamin + Lucas)
      </button>
      {status && <p className="text-center font-medium mt-2">{status}</p>}
    </form>
  );
}
