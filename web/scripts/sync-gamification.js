/* eslint-disable @typescript-eslint/no-require-imports */
const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

// Map "Persona Name" to "Agent Slug"
const AUTHOR_MAP = {
  'Jules': 'gemini',
  'Gemini': 'gemini',
  'Grok': 'grok',
  'Abacus': 'abacus',
  'Claude': 'claude',
  'Professor Claude': 'claude',
  'Deep Agent': 'abacus'
};

const RESEARCH_ROOT = path.join(__dirname, '../../research');

async function syncGamification() {
  if (!process.env.DATABASE_URL) {
    console.warn('DATABASE_URL not set. Skipping gamification sync.');
    return;
  }

  const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    console.log('Connected to database for gamification sync.');

    // 1. Ensure Agents exist in DB
    const agents = [
      { name: 'Gemini', slug: 'gemini', role: 'Lead Developer' },
      { name: 'Grok', slug: 'grok', role: 'Team Lead' },
      { name: 'Abacus', slug: 'abacus', role: 'Deep Researcher' },
      { name: 'Claude', slug: 'claude', role: 'Architect' }
    ];

    for (const agent of agents) {
      await client.query(
        'INSERT INTO agents (name, slug, role) VALUES ($1, $2, $3) ON CONFLICT (slug) DO UPDATE SET role = EXCLUDED.role',
        [agent.name, agent.slug, agent.role]
      );
    }

    // Add points column if missing (idempotent)
    await client.query('ALTER TABLE agents ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0');

    // 2. Scan Briefs
    let briefs = [];
    try {
      const entries = fs.readdirSync(RESEARCH_ROOT, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isDirectory() && !entry.name.startsWith('_') && !entry.name.startsWith('.')) {
          const category = entry.name;
          const briefsDir = path.join(RESEARCH_ROOT, category, 'briefs');

          if (fs.existsSync(briefsDir)) {
            const files = fs.readdirSync(briefsDir);
            for (const file of files) {
              if (file.endsWith('.md')) {
                const filePath = path.join(briefsDir, file);
                const content = fs.readFileSync(filePath, 'utf8');

                // Find Author
                let authorSlug = 'unknown';
                // Look for "X's Hot Take" or similar pattern
                const hotTakeMatch = content.match(/\*\*(.+?)'s Hot Take\*\*/);

                if (hotTakeMatch) {
                  const authorName = hotTakeMatch[1].trim();
                  authorSlug = AUTHOR_MAP[authorName] || 'unknown';
                }

                briefs.push({
                  slug: file.replace('.md', ''),
                  category,
                  authorSlug,
                  title: file
                });
              }
            }
          }
        }
      }
    } catch (err) {
      console.warn('Error reading research directory:', err);
    }

    // 3. Award Points
    for (const brief of briefs) {
      if (brief.authorSlug !== 'unknown') {
        // Find Agent ID
        const res = await client.query('SELECT id FROM agents WHERE slug = $1', [brief.authorSlug]);
        if (res.rows.length > 0) {
          const agentId = res.rows[0].id;
          const points = 10;
          const description = `Research Brief: ${brief.slug}`;

          // Check if already awarded (dedup by description + entity)
          const check = await client.query(
            'SELECT id FROM logs WHERE entity_id = $1 AND entity_type = $2 AND description = $3',
            [agentId, 'agent', description]
          );

          if (check.rows.length === 0) {
            await client.query(
              'INSERT INTO logs (entity_id, entity_type, points, description) VALUES ($1, $2, $3, $4)',
              [agentId, 'agent', points, description]
            );
            console.log(`Awarded ${points} points to ${brief.authorSlug} for ${brief.slug}`);
          }
        }
      }
    }

    // 4. Update Total Points
    // Using a subquery update
    await client.query(`
      UPDATE agents SET points = (
        SELECT COALESCE(SUM(points), 0) FROM logs
        WHERE logs.entity_id = agents.id AND logs.entity_type = 'agent'
      )
    `);
    console.log('Updated agent point totals.');

  } catch (err) {
    console.error('Gamification sync error:', err);
    // Don't fail build if DB is unreachable locally
    if (process.env.CI) {
        process.exit(1);
    }
  } finally {
    await client.end();
  }
}

syncGamification();
