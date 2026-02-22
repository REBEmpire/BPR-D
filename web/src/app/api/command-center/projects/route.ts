import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const result = await query(
      'SELECT * FROM cc_projects ORDER BY created_at DESC LIMIT 50'
    );
    return NextResponse.json({ projects: result.rows });
  } catch (error) {
    console.error('Failed to fetch projects:', error);
    return NextResponse.json({ projects: [] });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { name, description, assignedAgents } = await request.json();
    if (!name) {
      return NextResponse.json({ error: 'Missing name' }, { status: 400 });
    }
    const result = await query(
      'INSERT INTO cc_projects (name, description, assigned_agents, status) VALUES ($1, $2, $3, $4) RETURNING *',
      [name, description || '', JSON.stringify(assignedAgents || []), 'planning']
    );

    await query(
      'INSERT INTO cc_activity (action_type, description) VALUES ($1, $2)',
      ['project', `Project created: ${name}`]
    );

    return NextResponse.json({ project: result.rows[0] });
  } catch (error) {
    console.error('Failed to create project:', error);
    return NextResponse.json({ error: 'Failed to create project' }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const { id, status, name, description, assignedAgents } = await request.json();
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
    if (name !== undefined) {
      updates.push(`name = $${paramIndex++}`);
      params.push(name);
    }
    if (description !== undefined) {
      updates.push(`description = $${paramIndex++}`);
      params.push(description);
    }
    if (assignedAgents !== undefined) {
      updates.push(`assigned_agents = $${paramIndex++}`);
      params.push(JSON.stringify(assignedAgents));
    }

    if (updates.length === 0) {
      return NextResponse.json({ error: 'No fields to update' }, { status: 400 });
    }

    params.push(id);
    await query(`UPDATE cc_projects SET ${updates.join(', ')} WHERE id = $${paramIndex}`, params);

    if (status) {
      await query(
        'INSERT INTO cc_activity (action_type, description) VALUES ($1, $2)',
        ['project', `Project status updated to: ${status}`]
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to update project:', error);
    return NextResponse.json({ error: 'Failed to update project' }, { status: 500 });
  }
}
