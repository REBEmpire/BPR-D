import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const result = await query(
      'SELECT * FROM agenda_items ORDER BY priority DESC, created_at DESC LIMIT 100'
    );
    return NextResponse.json({ items: result.rows });
  } catch (error) {
    console.error('Failed to fetch agenda items:', error);
    return NextResponse.json({ items: [] });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { topicType, topicName, docReferences, priority } = await request.json();
    if (!topicType || !topicName) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }
    const result = await query(
      'INSERT INTO agenda_items (topic_type, topic_name, doc_references, priority) VALUES ($1, $2, $3, $4) RETURNING *',
      [topicType, topicName, docReferences || '', priority || 3]
    );

    await query(
      'INSERT INTO cc_activity (action_type, description) VALUES ($1, $2)',
      ['meeting', `Agenda item added: ${topicName}`]
    );

    return NextResponse.json({ item: result.rows[0] });
  } catch (error) {
    console.error('Failed to create agenda item:', error);
    return NextResponse.json({ error: 'Failed to create agenda item' }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const { id, status } = await request.json();
    if (!id || !status) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }
    await query('UPDATE agenda_items SET status = $1 WHERE id = $2', [status, id]);

    await query(
      'INSERT INTO cc_activity (action_type, description) VALUES ($1, $2)',
      ['meeting', `Agenda item status updated to: ${status}`]
    );

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to update agenda item:', error);
    return NextResponse.json({ error: 'Failed to update agenda item' }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    if (!id) {
      return NextResponse.json({ error: 'Missing id' }, { status: 400 });
    }
    await query('DELETE FROM agenda_items WHERE id = $1', [id]);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to delete agenda item:', error);
    return NextResponse.json({ error: 'Failed to delete agenda item' }, { status: 500 });
  }
}
