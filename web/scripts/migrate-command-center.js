const { Client } = require('pg');

async function migrateCommandCenter() {
  if (!process.env.DATABASE_URL) {
    console.log('Skipping command-center migration: No DATABASE_URL');
    return;
  }

  const client = new Client({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } });
  await client.connect();
  console.log('Connected to database for command-center migration.');

  try {
    // Chat Sessions
    await client.query(`
      CREATE TABLE IF NOT EXISTS chat_sessions (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        participants JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('chat_sessions table ready.');

    // Chat Messages
    await client.query(`
      CREATE TABLE IF NOT EXISTS chat_messages (
        id SERIAL PRIMARY KEY,
        session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
        agent_name VARCHAR(50),
        content TEXT,
        role VARCHAR(20) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('chat_messages table ready.');

    // Agenda Items
    await client.query(`
      CREATE TABLE IF NOT EXISTS agenda_items (
        id SERIAL PRIMARY KEY,
        topic_type VARCHAR(50) NOT NULL,
        topic_name VARCHAR(255) NOT NULL,
        doc_references TEXT,
        priority INTEGER DEFAULT 3,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('agenda_items table ready.');

    // Command Center Tasks
    await client.query(`
      CREATE TABLE IF NOT EXISTS cc_tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        assigned_agents JSONB DEFAULT '[]'::jsonb,
        priority INTEGER DEFAULT 3,
        status VARCHAR(20) DEFAULT 'backlog',
        project_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('cc_tasks table ready.');

    // Command Center Projects
    await client.query(`
      CREATE TABLE IF NOT EXISTS cc_projects (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        status VARCHAR(30) DEFAULT 'planning',
        assigned_agents JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('cc_projects table ready.');

    // Command Center Activity Log
    await client.query(`
      CREATE TABLE IF NOT EXISTS cc_activity (
        id SERIAL PRIMARY KEY,
        action_type VARCHAR(50) NOT NULL,
        description TEXT,
        agent_name VARCHAR(50),
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('cc_activity table ready.');

    console.log('Command Center migration complete!');
  } catch (err) {
    console.error('Migration error:', err);
  } finally {
    await client.end();
  }
}

migrateCommandCenter();
