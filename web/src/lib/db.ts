/* eslint-disable @typescript-eslint/no-explicit-any */
import { Pool } from 'pg';

let pool: Pool | null = null;

if (process.env.DATABASE_URL) {
  pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false
    }
  });
}

export const query = async (text: string, params?: any[]) => {
  if (!pool) {
    console.warn('Database not configured');
    return { rows: [] };
  }
  return pool.query(text, params);
};
