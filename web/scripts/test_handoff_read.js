const fs = require('fs');
const path = require('path');
const handoffPath = path.join(__dirname, '../../_agents/grok/handoff.md');
console.log('Checking:', handoffPath);
if (fs.existsSync(handoffPath)) {
    console.log('Found! Content length:', fs.readFileSync(handoffPath, 'utf8').length);
} else {
    console.log('Not found');
}
