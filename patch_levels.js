#!/usr/bin/env node
// patch_levels.js — fixes level casing in archive.db in-place
const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

const DB_FILE = path.join(__dirname, 'archive.db');

initSqlJs().then(SQL => {
  const fileBuffer = fs.readFileSync(DB_FILE);
  const db = new SQL.Database(fileBuffer);

  const before = db.exec("SELECT COUNT(*) FROM sessions WHERE level != '' AND level = lower(level)")[0].values[0][0];
  console.log(`Rows with lowercase level: ${before}`);

  db.run(`UPDATE sessions SET level = 'Essentials'   WHERE level = 'essentials'`);
  db.run(`UPDATE sessions SET level = 'Advanced'     WHERE level = 'advanced'`);
  db.run(`UPDATE sessions SET level = 'Entrepreneurs' WHERE level = 'entrepreneurs'`);

  const after = db.exec("SELECT COUNT(*) FROM sessions WHERE level != '' AND level = lower(level)")[0].values[0][0];
  console.log(`Rows with lowercase level after fix: ${after}`);

  const byLevel = db.exec("SELECT level, COUNT(*) FROM sessions GROUP BY level ORDER BY level");
  console.log('\nLevel distribution:');
  byLevel[0].values.forEach(([lv, n]) => console.log(`  "${lv}": ${n}`));

  const data = db.export();
  fs.writeFileSync(DB_FILE, Buffer.from(data));
  console.log('\narchive.db patched and saved.');
});
