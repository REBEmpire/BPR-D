/* eslint-disable @typescript-eslint/no-require-imports */
const { Client } = require('pg');

async function migrate() {
  if (!process.env.DATABASE_URL) {
    console.log('Skipping migration: No DATABASE_URL');
    return;
  }

  const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false
    }
  });

  const schema = `
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    video_url VARCHAR(255),
    bio TEXT,
    role VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    points INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS quests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    points_reward INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL,
    entity_type VARCHAR(20) NOT NULL,
    quest_id INTEGER,
    points INTEGER NOT NULL,
    description VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
`;

  try {
    await client.connect();
    console.log('Connected to database');
    await client.query(schema);
    console.log('Schema migration completed successfully');
  } catch (err) {
    console.warn('Migration failed (non-fatal):', err.message);
  } finally {
    await client.end();
  }
}

migrate();
