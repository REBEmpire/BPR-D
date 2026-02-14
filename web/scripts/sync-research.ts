/* eslint-disable @typescript-eslint/no-unused-vars */
import fs from 'fs/promises';
import path from 'path';

const RESEARCH_ROOT = path.join(process.cwd(), '../research');
const WEB_CONTENT_ROOT = path.join(process.cwd(), 'src/content/research');

async function copyResearch() {
  try {
    // Clean target directory
    await fs.rm(WEB_CONTENT_ROOT, { recursive: true, force: true });
    await fs.mkdir(WEB_CONTENT_ROOT, { recursive: true });

    // Read research directories
    const entries = await fs.readdir(RESEARCH_ROOT, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.startsWith('_') && !entry.name.startsWith('.')) {
        const category = entry.name;
        const briefsDir = path.join(RESEARCH_ROOT, category, 'briefs');

        try {
          // Check if briefs directory exists
          await fs.access(briefsDir);

          // Create category directory in web content
          const targetDir = path.join(WEB_CONTENT_ROOT, category);
          await fs.mkdir(targetDir, { recursive: true });

          // Copy markdown files
          const files = await fs.readdir(briefsDir);
          for (const file of files) {
            if (file.endsWith('.md')) {
              await fs.copyFile(
                path.join(briefsDir, file),
                path.join(targetDir, file)
              );
              console.log(`Copied ${category}/${file}`);
            }
          }
        } catch (_) {
          // Skip if briefs directory doesn't exist
          continue;
        }
      }
    }
    console.log('Research content sync complete.');
  } catch (error) {
    console.error('Error syncing research content:', error);
    process.exit(1);
  }
}

copyResearch();
