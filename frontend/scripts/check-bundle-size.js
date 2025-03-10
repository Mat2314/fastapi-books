#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

// Function to format file size
function formatSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Check if stats.json exists
const statsPath = path.join(__dirname, '../dist/fabooks/stats.json');
if (!fs.existsSync(statsPath)) {
  console.error(chalk.red('Error: stats.json not found. Run "ng build --stats-json" first.'));
  process.exit(1);
}

// Read and parse stats.json
const stats = JSON.parse(fs.readFileSync(statsPath, 'utf8'));

// Extract asset information
const assets = stats.assets || [];
const initialAssets = assets.filter(asset => 
  asset.name.endsWith('.js') || 
  asset.name.endsWith('.css')
);

// Sort assets by size
initialAssets.sort((a, b) => b.size - a.size);

// Calculate total size
const totalSize = initialAssets.reduce((sum, asset) => sum + asset.size, 0);

// Print report
console.log(chalk.bold('\nBundle Size Analysis:'));
console.log(chalk.bold('===================\n'));

console.log(chalk.bold('Initial Bundle Size:'), chalk.blue(formatSize(totalSize)));
console.log(chalk.bold('\nLargest Files:'));

initialAssets.slice(0, 10).forEach(asset => {
  const size = formatSize(asset.size);
  const percentage = ((asset.size / totalSize) * 100).toFixed(2) + '%';
  
  let color = chalk.green;
  if (asset.size > 500 * 1024) {
    color = chalk.red;
  } else if (asset.size > 200 * 1024) {
    color = chalk.yellow;
  }
  
  console.log(`${color(size.padEnd(10))} (${percentage.padStart(6)}) - ${asset.name}`);
});

// Check against budget
const budgetLimit = 1.5 * 1024 * 1024; // 1.5MB
if (totalSize > budgetLimit) {
  console.log(chalk.red(`\n⚠️ Bundle size (${formatSize(totalSize)}) exceeds budget limit (${formatSize(budgetLimit)})`));
  console.log(chalk.yellow('Consider optimizing your application further:'));
  console.log('- Use lazy loading for routes');
  console.log('- Remove unused dependencies');
  console.log('- Optimize component styles');
  console.log('- Use tree-shaking more effectively');
  process.exit(1);
} else {
  console.log(chalk.green(`\n✅ Bundle size (${formatSize(totalSize)}) is within budget limit (${formatSize(budgetLimit)})`));
  process.exit(0);
} 