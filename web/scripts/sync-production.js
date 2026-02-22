const fs = require('fs');
const path = require('path');
let matter;
try {
  matter = require('gray-matter');
} catch (e) {
  // Simple fallback if gray-matter is missing
  matter = (content) => {
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (match) {
      const data = {};
      match[1].split('\n').forEach(line => {
        const [key, ...val] = line.split(':');
        if (key && val) data[key.trim()] = val.join(':').trim().replace(/^['"]|['"]$/g, '');
      });
      return { data };
    }
    return { data: {} };
  };
}

// Paths
const ROOT_DIR = path.join(__dirname, '../..');
const SESSIONS_DIR = path.join(ROOT_DIR, 'meetings/logs');
const HANDOFFS_DIR = path.join(ROOT_DIR, '_agents/_handoffs');
const TEAM_STATE_FILE = path.join(ROOT_DIR, '_agents/team_state.md');
const ANALYSIS_LOG_FILE = path.join(ROOT_DIR, 'research/corruption-investigation/briefs/epstein-doj-analysis/ANALYSIS_LOG.md');
const RESEARCH_DIR = path.join(ROOT_DIR, 'research');
const OUTPUT_FILE = path.join(__dirname, '../src/content/production.json');

console.log('🔄 Syncing production data...\n');

// Parse all meeting session files
function parseMeetings() {
  const meetings = [];

  if (!fs.existsSync(SESSIONS_DIR)) {
    console.log('⚠️  No meetings/logs directory found at', SESSIONS_DIR);
    return meetings;
  }

  const files = fs.readdirSync(SESSIONS_DIR).filter(f => f.endsWith('.md'));
  console.log(`📄 Found ${files.length} session file(s)`);

  files.forEach(file => {
    const filePath = path.join(SESSIONS_DIR, file);
    const content = fs.readFileSync(filePath, 'utf-8');
    const { data: frontmatter } = matter(content);

    // 1. Try to extract JSON block (new format)
    // Find ALL JSON blocks and pick the one with meeting report data
    const jsonMatches = content.matchAll(/\`\`\`json\s*([\s\S]*?)\s*\`\`\`/g);
    let jsonData = null;

    for (const match of jsonMatches) {
        try {
            const parsed = JSON.parse(match[1]);
            if (parsed.meeting_notes || parsed.action_items || parsed.handoffs || parsed.key_decisions) {
                jsonData = parsed;
                break;
            }
        } catch (e) {
            // Ignore invalid blocks
        }
    }

    // Extract metadata
    // Priority: Frontmatter -> Regex -> Filename
    let date = frontmatter.date;
    if (!date) {
        const dateMatch = content.match(/\*\*Date:\*\*\s*(.+)/); // Old format
        if (dateMatch) date = dateMatch[1].trim();
    }
    if (!date) {
        // New header format: # Daily Briefing — 2026-02-21
        const headerDateMatch = content.match(/# .*? — (\d{4}-\d{2}-\d{2})/);
        if (headerDateMatch) date = headerDateMatch[1];
    }
    if (!date) {
        const fileMatch = file.match(/\d{4}-\d{2}-\d{2}/);
        date = fileMatch ? fileMatch[0] : 'Unknown';
    }

    // Type
    let type = "Meeting";
    const headerMatch = content.match(/# (.+?) —/);
    if (headerMatch) type = headerMatch[1].trim();
    else {
        const typeMatch = content.match(/\*\*Type:\*\*\s*(.+)/);
        if (typeMatch) type = typeMatch[1].trim();
    }

    // Facilitator
    let facilitator = null;
    const facMatch = content.match(/\|\s*(.+?)\s*Facilitating/); // From header
    if (facMatch) facilitator = facMatch[1].trim();

    if (!facilitator && jsonData && jsonData.author) {
        if (jsonData.author.includes("Grok")) facilitator = "Grok";
        else facilitator = jsonData.author;
    }
    if (!facilitator) {
        const oldFacMatch = content.match(/\*\*Facilitator:\*\*\s*(.+)/);
        if (oldFacMatch) facilitator = oldFacMatch[1].trim();
    }

    // Participants
    const participants = [];
    const introMatches = content.matchAll(/### (Grok|Claude|Gemini|Deep Agent|Jules|ChatLLM|Abacus)/g);
    for (const match of introMatches) {
      if (!participants.includes(match[1])) {
        participants.push(match[1]);
      }
    }

    // Insights
    const insights = [];
    if (jsonData) {
        const notes = jsonData.meeting_notes || "";

        // Try extracting "Decisions Snapshot"
        const decisionsMatch = notes.match(/## Decisions Snapshot([\s\S]*?)(?=##|$)/);
        if (decisionsMatch) {
            const bullets = decisionsMatch[1].match(/^- (.+)$/gm);
            if (bullets) {
                insights.push(...bullets.map(b => b.replace(/^- /, '').trim()));
            }
        }

        // If no decisions, try Key Quotes
        if (insights.length === 0) {
             const quotesMatch = notes.match(/### Key Quotes([\s\S]*?)(?=##|$)/);
             if (quotesMatch) {
                 const bullets = quotesMatch[1].match(/^- (.+)$/gm);
                 if (bullets) {
                     insights.push(...bullets.map(b => b.replace(/^- /, '').trim()));
                 }
             }
        }
        // Try "Arc of Discussion" if still empty
        if (insights.length === 0) {
             const arcMatch = notes.match(/## Arc of Discussion([\s\S]*?)(?=##|$)/);
             if (arcMatch) {
                 const summaries = arcMatch[1].match(/\*\*(.+?):\*\* (.+)/g);
                 if (summaries) {
                     insights.push(...summaries.slice(0, 5).map(s => s.replace(/\*\*/g, '').trim()));
                 }
             }
        }
    } else {
        const insightsSection = content.match(/## Meeting Notes([\s\S]*?)(?=##|$)/);
        if (insightsSection) {
          const bulletPoints = insightsSection[1].match(/^- .+$/gm);
          if (bulletPoints) {
            insights.push(...bulletPoints.map(b => b.replace(/^- /, '').trim()));
          }
        }
    }

    // Action Items
    const actionItems = [];
    if (jsonData && jsonData.action_items) {
        jsonData.action_items.forEach(item => {
            actionItems.push({
                assignee: item.assigned_to || "Team",
                task: item.task || "Unknown Task",
                priority: item.priority || "Medium"
            });
        });
    } else {
        const actionSection = content.match(/## Action Items([\s\S]*?)(?=##|$)/);
        if (actionSection) {
          const tableRows = actionSection[1].match(/\|([^|]+)\|([^|]+)\|([^|]+)\|/g);
          if (tableRows) {
            tableRows.forEach((row, idx) => {
              if (idx === 0) return; // Skip header
              const cells = row.split('|').map(s => s.trim()).filter(s => s && !s.match(/^-+$/));
              if (cells.length >= 3) {
                actionItems.push({
                  assignee: cells[0],
                  task: cells[1],
                  priority: cells[2]
                });
              }
            });
          }
        }
    }

    // Handoffs
    const handoffs = [];
    if (jsonData && jsonData.handoffs) {
        jsonData.handoffs.forEach(item => {
            handoffs.push({
                to: item.assigned_to || "Unknown",
                task: item.title || "Unknown Task"
            });
        });
    } else {
        const handoffMatches = content.matchAll(/handoff to (\w+)(?::\s*(.+?)(?=\n|$))?/gi);
        for (const match of handoffMatches) {
          handoffs.push({
            to: match[1],
            task: match[2] || 'See meeting notes'
          });
        }
    }

    meetings.push({
      fileName: file,
      date: date,
      type: type,
      facilitator: facilitator,
      attendees: participants.join(', '),
      participants,
      insightsCount: insights.length,
      insights: insights.slice(0, 5), // Top 5 insights
      actionItemsCount: actionItems.length,
      actionItems,
      handoffsCount: handoffs.length,
      handoffs
    });
  });

  console.log(`✅ Parsed ${meetings.length} meeting(s)\n`);
  return meetings.sort((a, b) => b.date.localeCompare(a.date));
}

// Parse team state
function parseTeamState() {
  if (!fs.existsSync(TEAM_STATE_FILE)) {
    console.log('⚠️  No team_state.md found');
    return { activeProjects: [], agentStatus: [] };
  }

  const content = fs.readFileSync(TEAM_STATE_FILE, 'utf-8');

  // Extract active projects
  const activeProjects = [];
  const projectSection = content.match(/## 🎯 Active Projects([\s\S]*?)(?=##|$)/);
  if (projectSection) {
    const projectMatches = projectSection[1].matchAll(/### \d+\.\s*(.+?)\s*\(Priority:\s*(.+?)\)[\s\S]*?- \*\*Status:\*\*\s*(.+?)(?=\n|$)/g);
    for (const match of projectMatches) {
      activeProjects.push({
        name: match[1].trim(),
        priority: match[2].trim(),
        status: match[3].trim()
      });
    }
  }

  // Extract agent status
  const agentStatus = [];
  const rosterSection = content.match(/## 👥 Team Roster[\s\S]*?(?=##|$)/);
  if (rosterSection) {
    const agentMatches = rosterSection[0].matchAll(/- \*\*(\w+):\*\*[\s\S]*?Model:\s*(.+?)[\s\S]*?Status:\s*(.+?)(?=\n|$)/g);
    for (const match of agentMatches) {
      agentStatus.push({
        name: match[1].trim(),
        model: match[2].trim(),
        status: match[3].trim()
      });
    }
  }

  console.log(`✅ Parsed team state: ${activeProjects.length} projects, ${agentStatus.length} agents\n`);
  return { activeProjects, agentStatus };
}

// Parse investigation metrics
function parseInvestigationMetrics() {
  if (!fs.existsSync(ANALYSIS_LOG_FILE)) {
    console.log('⚠️  No ANALYSIS_LOG.md found');
    return { phases: [], successCriteria: [], overallProgress: 0 };
  }

  const content = fs.readFileSync(ANALYSIS_LOG_FILE, 'utf-8');

  // Extract phases
  const phases = [];
  const phaseMatches = content.matchAll(/## Phase (\d+):\s*(.+?)\s*-\s*(COMPLETE|IN PROGRESS|NOT STARTED)/gi);
  for (const match of phaseMatches) {
    phases.push({
      number: parseInt(match[1]),
      name: match[2].trim(),
      status: match[3].trim()
    });
  }

  // Extract components from each phase
  let totalComponents = 0;
  let completedComponents = 0;

  const componentSections = content.matchAll(/### Components Implemented([\s\S]*?)(?=###|##|---)/g);
  for (const section of componentSections) {
    const checkboxes = section[1].matchAll(/^- (✅|⬜) (.+)$/gm);
    for (const checkbox of checkboxes) {
      totalComponents++;
      if (checkbox[1] === '✅') completedComponents++;
    }
  }

  // Extract investigation progress metrics
  const successCriteria = [];
  const criteriaSection = content.match(/### Code Breaking([\s\S]*?)### Player Mapping/);
  if (criteriaSection) {
    const codeTermsMatch = criteriaSection[1].match(/Code Terms Identified:\*\*\s*(\d+)\s*\/\s*(\d+)/);
    if (codeTermsMatch) {
      successCriteria.push({
        name: 'Code Terms Identified',
        current: parseInt(codeTermsMatch[1]),
        target: codeTermsMatch[2],
        complete: parseInt(codeTermsMatch[1]) >= 100
      });
    }
  }

  const playerSection = content.match(/### Player Mapping([\s\S]*?)### Timeline/);
  if (playerSection) {
    const entitiesMatch = playerSection[1].match(/Total Entities:\*\*\s*(\d+)\s*\/\s*(\d+)/);
    if (entitiesMatch) {
      successCriteria.push({
        name: 'Total Entities Mapped',
        current: parseInt(entitiesMatch[1]),
        target: entitiesMatch[2],
        complete: parseInt(entitiesMatch[1]) >= 500
      });
    }
  }

  const overallProgress = totalComponents > 0 ? Math.round((completedComponents / totalComponents) * 100) : 0;

  console.log(`✅ Parsed investigation: ${phases.length} phases, ${completedComponents}/${totalComponents} components complete (${overallProgress}%)\n`);
  return {
    phases,
    componentsComplete: completedComponents,
    totalComponents,
    successCriteria,
    overallProgress
  };
}

// Count research briefs
function countResearchBriefs() {
  if (!fs.existsSync(RESEARCH_DIR)) {
    console.log('⚠️  No research directory found');
    return { totalBriefs: 0, categoryCounts: {}, recentBriefs: [] };
  }

  const categories = fs.readdirSync(RESEARCH_DIR).filter(f => {
    const stat = fs.statSync(path.join(RESEARCH_DIR, f));
    return stat.isDirectory() && !f.startsWith('.');
  });

  let totalBriefs = 0;
  const categoryCounts = {};
  const recentBriefs = [];

  categories.forEach(category => {
    const briefsDir = path.join(RESEARCH_DIR, category, 'briefs');
    if (fs.existsSync(briefsDir)) {
      const briefs = fs.readdirSync(briefsDir).filter(f => {
        const stat = fs.statSync(path.join(briefsDir, f));
        return stat.isDirectory();
      });

      categoryCounts[category] = briefs.length;
      totalBriefs += briefs.length;

      // Get recent briefs from this category
      briefs.slice(0, 2).forEach(brief => {
        const readmePath = path.join(briefsDir, brief, 'README.md');
        if (fs.existsSync(readmePath)) {
          const content = fs.readFileSync(readmePath, 'utf-8');
          const titleMatch = content.match(/^#\s+(.+)$/m);
          const dateMatch = content.match(/\*\*Date:\*\*\s*(.+)/);

          recentBriefs.push({
            title: titleMatch ? titleMatch[1] : brief,
            category,
            date: dateMatch ? dateMatch[1].trim() : 'Unknown',
            slug: brief
          });
        }
      });
    }
  });

  // Sort recent briefs by date and take top 10
  recentBriefs.sort((a, b) => b.date.localeCompare(a.date));
  const topRecent = recentBriefs.slice(0, 10);

  console.log(`✅ Found ${totalBriefs} research briefs across ${categories.length} categories\n`);
  return { totalBriefs, categoryCounts, recentBriefs: topRecent };
}

// Main sync function
function syncProduction() {
  const productionData = {
    lastUpdated: new Date().toISOString(),
    meetings: parseMeetings(),
    teamState: parseTeamState(),
    investigationMetrics: parseInvestigationMetrics(),
    researchMetrics: countResearchBriefs()
  };

  // Ensure output directory exists
  const outputDir = path.dirname(OUTPUT_FILE);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Write output
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(productionData, null, 2));
  console.log(`✅ Production data synced to: ${OUTPUT_FILE}`);
  console.log(`\n📊 Summary:`);
  console.log(`   - Meetings: ${productionData.meetings.length}`);
  console.log(`   - Research Briefs: ${productionData.researchMetrics.totalBriefs}`);
  console.log(`   - Active Projects: ${productionData.teamState.activeProjects.length}`);
  console.log(`   - Investigation Progress: ${productionData.investigationMetrics.overallProgress}%`);
}

// Run sync
syncProduction();
