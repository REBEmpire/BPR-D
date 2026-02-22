import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('sessionId');
    if (!sessionId) {
      return NextResponse.json({ messages: [] });
    }
    const result = await query(
      'SELECT * FROM chat_messages WHERE session_id = $1 ORDER BY created_at ASC',
      [sessionId]
    );
    return NextResponse.json({ messages: result.rows });
  } catch (error) {
    console.error('Failed to fetch messages:', error);
    return NextResponse.json({ messages: [] });
  }
}
