/* eslint-disable @typescript-eslint/no-require-imports, @typescript-eslint/no-unused-vars */
const fs = require('fs');
const path = require('path');

const RESEARCH_ROOT = path.join(__dirname, '../../research');
const WEB_CONTENT_ROOT = path.join(__dirname, '../src/content/research');

// Ensure the target directory exists
if (fs.existsSync(WEB_CONTENT_ROOT)) {
  fs.rmSync(WEB_CONTENT_ROOT, { recursive: true, force: true });
}
fs.mkdirSync(WEB_CONTENT_ROOT, { recursive: true });

// Read research directories
try {
  const entries = fs.readdirSync(RESEARCH_ROOT, { withFileTypes: true });

  for (const entry of entries) {
    if (entry.isDirectory() && !entry.name.startsWith('_') && !entry.name.startsWith('.')) {
      const category = entry.name;
      const briefsDir = path.join(RESEARCH_ROOT, category, 'briefs');

      try {
        // Check if briefs directory exists
        fs.accessSync(briefsDir);

        // Create category directory in web content
        const targetDir = path.join(WEB_CONTENT_ROOT, category);
        fs.mkdirSync(targetDir, { recursive: true });

        // Copy markdown files
        const files = fs.readdirSync(briefsDir);
        for (const file of files) {
          if (file.endsWith('.md')) {
            fs.copyFileSync(
              path.join(briefsDir, file),
              path.join(targetDir, file)
            );
            console.log(`Copied ${category}/${file}`);
          }
        }
      } catch (err) {
        // Skip if briefs directory doesn't exist
        continue;
      }
    }
  }
  console.log('Research content sync complete.');
} catch (error) {
  console.warn('Warning: Could not read research directory. Using empty research content.');
  console.warn('  Path attempted:', RESEARCH_ROOT);
  console.warn('  Error:', error.message);
  console.log('Research content sync complete (empty - source directory unavailable).');
}
