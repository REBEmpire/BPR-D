import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const result = await query(
      'SELECT * FROM chat_sessions ORDER BY created_at DESC LIMIT 50'
    );
    return NextResponse.json({ sessions: result.rows });
  } catch (error) {
    console.error('Failed to fetch sessions:', error);
    return NextResponse.json({ sessions: [] });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { participants, title } = await request.json();
    const sessionTitle = title || `Session ${new Date().toLocaleDateString()}`;
    const result = await query(
      'INSERT INTO chat_sessions (title, participants) VALUES ($1, $2) RETURNING *',
      [sessionTitle, JSON.stringify(participants || [])]
    );
    
    await query(
      'INSERT INTO cc_activity (action_type, description) VALUES ($1, $2)',
      ['chat', `New chat session created: ${sessionTitle}`]
    );

    return NextResponse.json({ session: result.rows[0] });
  } catch (error) {
    console.error('Failed to create session:', error);
    return NextResponse.json({ error: 'Failed to create session' }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    if (!id) {
      return NextResponse.json({ error: 'Missing id' }, { status: 400 });
    }
    await query('DELETE FROM chat_sessions WHERE id = $1', [id]);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to delete session:', error);
    return NextResponse.json({ error: 'Failed to delete session' }, { status: 500 });
  }
}
