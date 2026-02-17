/* eslint-disable @typescript-eslint/no-require-imports, @typescript-eslint/no-unused-vars */
const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const AGENTS_ROOT = path.join(__dirname, '../../_agents');
const PUBLIC_AGENTS_ROOT = path.join(__dirname, '../public/agents');
const CONTENT_OUTPUT = path.join(__dirname, '../src/content/agents.json');

// Ensure public agents directory exists
if (fs.existsSync(PUBLIC_AGENTS_ROOT)) {
  fs.rmSync(PUBLIC_AGENTS_ROOT, { recursive: true, force: true });
}
fs.mkdirSync(PUBLIC_AGENTS_ROOT, { recursive: true });

// Ensure content directory exists
const contentDir = path.dirname(CONTENT_OUTPUT);
if (!fs.existsSync(contentDir)) {
  fs.mkdirSync(contentDir, { recursive: true });
}

const agents = [];

try {
  const agentDirs = fs.readdirSync(AGENTS_ROOT, { withFileTypes: true });

  for (const dirent of agentDirs) {
    if (dirent.isDirectory() && !dirent.name.startsWith('_') && !dirent.name.startsWith('.')) {
      const agentName = dirent.name;
      const agentPath = path.join(AGENTS_ROOT, agentName);

      // Find profile.md
      const profilePath = path.join(agentPath, 'profile.md');
      let profileData = {};
      let bio = '';
      let role = '';
      let name = agentName; // fallback

      if (fs.existsSync(profilePath)) {
        const fileContent = fs.readFileSync(profilePath, 'utf8');
        const { data, content } = matter(fileContent);
        profileData = data;
        bio = content; // rough bio
        role = data.role || 'Agent';
        name = data.name || agentName;
      } else {
        // Fallback to README.md if profile.md missing?
        const readmePath = path.join(agentPath, 'README.md');
        if (fs.existsSync(readmePath)) {
             const fileContent = fs.readFileSync(readmePath, 'utf8');
             bio = fileContent;
        }
      }

      // Read Handoff
      let handoffContent = '';
      const handoffPath = path.join(agentPath, 'handoff.md');
      if (fs.existsSync(handoffPath)) {
        handoffContent = fs.readFileSync(handoffPath, 'utf8');
      }

      // Read Active Context
      let activeContent = '';
      const activePath = path.join(agentPath, 'context', 'active.md');
      if (fs.existsSync(activePath)) {
        activeContent = fs.readFileSync(activePath, 'utf8');
      }

      // Find MP4
      const files = fs.readdirSync(agentPath);
      const videoFile = files.find(file => file.endsWith('.mp4'));
      let videoUrl = null;

      if (videoFile) {
        const srcVideo = path.join(agentPath, videoFile);
        const destVideoName = `${agentName}.mp4`;
        const destVideo = path.join(PUBLIC_AGENTS_ROOT, destVideoName);
        fs.copyFileSync(srcVideo, destVideo);
        videoUrl = `/agents/${destVideoName}`;
        console.log(`Copied video for ${agentName}`);
      }

      agents.push({
        id: agentName,
        name: name,
        slug: agentName,
        role: role,
        bio: bio,
        videoUrl: videoUrl,
        handoffContent: handoffContent,
        activeContent: activeContent
      });
    }
  }

  fs.writeFileSync(CONTENT_OUTPUT, JSON.stringify(agents, null, 2));
  console.log('Agents sync complete.');

} catch (error) {
  console.error('Error syncing agents:', error);
  process.exit(1);
}
