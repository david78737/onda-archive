// build_ondanile.js — seeds ondanile/sessions.json from all archive sources
// Usage: node build_ondanile.js

const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, 'ondanile', 'sessions.json');

// ── Source 1: Elevate Summit (onda-archive/sessions.json) ─────────────────────
const elevate = JSON.parse(fs.readFileSync(path.join(__dirname, 'sessions.json'), 'utf8'));

// ── Source 2: PCA events (pca-archive/sessions.json) ──────────────────────────
const pcaPath = path.join(__dirname, '..', 'pca-archive', 'sessions.json');
const pca = JSON.parse(fs.readFileSync(pcaPath, 'utf8'));

// ── Transform ─────────────────────────────────────────────────────────────────
let id = 1;

function orgFor(event) {
  if (!event) return 'Other';
  if (event.startsWith('PCA')) return 'ProductCamp Austin';
  if (event.toLowerCase().includes('elevate')) return 'Elevate Summit';
  return event;
}

function fromElevate(s) {
  const event = s.event || 'Elevate Summit 2026';
  const tags = [...(s.tags || [])];
  if (!tags.includes(event)) tags.push(event);
  return {
    id: id++,
    title: s.title,
    presenter: s.presenter,
    org: orgFor(event),
    source: event,
    tags,
    synopsis: s.synopsis || '',
    takeaways: s.takeaways || [],
    who: s.who || '',
    brief: s.brief || '',
    youtube: s.youtube || null,
    photo: s.photo ? `../${s.photo}` : null,
    onda_url: s.onda_url || null,
  };
}

function fromPca(s) {
  const event = s.event || 'PCA';
  const tags = [...(s.tags || [])];
  if (!tags.includes(event)) tags.push(event);
  return {
    id: id++,
    title: s.title,
    presenter: s.presenter,
    org: orgFor(event),
    source: event,
    tags,
    synopsis: s.synopsis || '',
    takeaways: s.takeaways || [],
    who: s.who || '',
    brief: s.brief || '',
    youtube: s.youtube || null,
    photo: null,
    onda_url: s.onda_url || null,
  };
}

const all = [
  ...elevate.map(fromElevate),
  ...pca.map(fromPca),
];

fs.writeFileSync(OUT, JSON.stringify(all, null, 2), 'utf8');
console.log(`[OK] Wrote ${all.length} sessions to ondanile/sessions.json`);

// Summary by source
const orgs = {};
all.forEach(s => { orgs[s.org] = (orgs[s.org] || 0) + 1; });
Object.entries(orgs).sort().forEach(([org, n]) => console.log(`  ${org}: ${n} sessions`));
