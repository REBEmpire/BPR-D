const fs = require('fs');
const path = require('path');

const agentsPath = path.join(process.cwd(), '../_agents');
console.log('Checking path:', agentsPath);

try {
  if (fs.existsSync(agentsPath)) {
    console.log('Agents dir exists');
    const files = fs.readdirSync(agentsPath);
    console.log('Files:', files);
  } else {
    console.log('Agents dir does NOT exist');
  }
} catch (e) {
  console.error('Error:', e);
}
