import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const agent = searchParams.get('agent');
    const status = searchParams.get('status');

    let sql = 'SELECT * FROM cc_tasks';
    const params: string[] = [];
    const conditions: string[] = [];

    if (agent) {
      conditions.push(`assigned_agents @> $${params.length + 1}`);
      params.push(JSON.stringify([agent]));
    }
    if (status) {
      conditions.push(`status = $${params.length + 1}`);
      params.push(status);
    }

    if (conditions.length > 0) {
      sql += ' WHERE ' + conditions.join(' AND ');
    }
    sql += ' ORDER BY priority DESC, created_at DESC LIMIT 100';

    const result = await query(sql, params);
    return NextResponse.json({ tasks: result.rows });
  } catch (error) {
    console.error('Failed to fetch tasks:', error);
    return NextResponse.json({ tasks: [] });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { title, description, assignedAgents, priority } = await request.json();
    if (!title) {
      return NextResponse.json({ error: 'Missing title' }, { status: 400 });
    }
    const result = await query(
      'INSERT INTO cc_tasks (title, description, assigned_agents, priority, status) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [title, description || '', JSON.stringify(assignedAgents || []), priority || 3, 'backlog']
    );

    await query(
      'INSERT INTO cc_activity (action_type, description, agent_name) VALUES ($1, $2, $3)',
      ['task', `Task created: ${title}`, assignedAgents?.[0] || null]
    );

    return NextResponse.json({ task: result.rows[0] });
  } catch (error) {
    console.error('Failed to create task:', error);
    return NextResponse.json({ error: 'Failed to create task' }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const { id, status, title, description, assignedAgents, priority } = await request.json();
    if (!id) {
      return NextResponse.json({ error: 'Missing id' }, { status: 400 });
    }

    const updates: string[] = [];
    const params: (string | number)[] = [];
    let paramIndex = 1;

    if (status !== undefined) {
      updates.push(`status = $${paramIndex++}`);
      params.push(status);
    }
    if (title !== undefined) {
      updates.push(`title = $${paramIndex++}`);
      params.push(title);
    }
    if (description !== undefined) {
      updates.push(`description = $${paramIndex++}`);
      params.push(description);
    }
    if (assignedAgents !== undefined) {
      updates.push(`assigned_agents = $${paramIndex++}`);
      params.push(JSON.stringify(assignedAgents));
    }
    if (priority !== undefined) {
      updates.push(`priority = $${paramIndex++}`);
      params.push(priority);
    }

    if (updates.length === 0) {
      return NextResponse.json({ error: 'No fields to update' }, { status: 400 });
    }

    params.push(id);
    await query(`UPDATE cc_tasks SET ${updates.join(', ')} WHERE id = $${paramIndex}`, params);

    if (status) {
      await query(
        'INSERT INTO cc_activity (action_type, description) VALUES ($1, $2)',
        ['task', `Task status updated to: ${status}`]
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to update task:', error);
    return NextResponse.json({ error: 'Failed to update task' }, { status: 500 });
  }
}
