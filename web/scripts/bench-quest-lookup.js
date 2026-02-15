/* eslint-disable @typescript-eslint/no-require-imports */
const { performance } = require('perf_hooks');

function generateQuests(count) {
  return Array.from({ length: count }, (_, i) => ({ id: `q${i}`, title: `Quest ${i}` }));
}

function generateCompleted(count, subsetSize) {
  // Simple subset: first N items
  const ids = Array.from({ length: subsetSize }, (_, i) => `q${i}`);
  return ids;
}

function runScenario(questCount, completedCount) {
  console.log(`\n--- Scenario: ${questCount} Quests, ${completedCount} Completed ---`);

  const quests = generateQuests(questCount);
  const completed = generateCompleted(questCount, completedCount);
  const completedSet = new Set(completed);

  // Adjust iterations based on complexity to keep runtime reasonable
  // complexity is roughly questCount * completedCount for Array
  const complexity = questCount * completedCount;
  let iterations = 100000;
  if (complexity > 1000) iterations = 10000;
  if (complexity > 100000) iterations = 1000;
  if (complexity > 10000000) iterations = 100;

  console.log(`Running ${iterations} iterations...`);

  const startArr = performance.now();
  for (let i = 0; i < iterations; i++) {
    for (let j = 0; j < quests.length; j++) {
      completed.includes(quests[j].id);
    }
  }
  const endArr = performance.now();
  const timeArr = endArr - startArr;
  console.log(`Array.includes: ${timeArr.toFixed(2)}ms (Avg: ${(timeArr/iterations).toFixed(4)}ms)`);

  const startSet = performance.now();
  for (let i = 0; i < iterations; i++) {
    for (let j = 0; j < quests.length; j++) {
      completedSet.has(quests[j].id);
    }
  }
  const endSet = performance.now();
  const timeSet = endSet - startSet;
  console.log(`Set.has:       ${timeSet.toFixed(2)}ms (Avg: ${(timeSet/iterations).toFixed(4)}ms)`);

  if (timeArr > 0 && timeSet > 0) {
    console.log(`Improvement: ${(timeArr / timeSet).toFixed(2)}x faster`);
  }
}

// Scenarios
runScenario(4, 2);       // Current App State
runScenario(100, 50);    // Medium
runScenario(1000, 500);  // Large
runScenario(10000, 5000); // Huge
