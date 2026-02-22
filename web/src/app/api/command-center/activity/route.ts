import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const result = await query(
      'SELECT * FROM cc_activity ORDER BY created_at DESC LIMIT 50'
    );
    return NextResponse.json({ activities: result.rows });
  } catch (error) {
    console.error('Failed to fetch activities:', error);
    return NextResponse.json({ activities: [] });
  }
}
