// Scans traces/ and writes traces/traces.json, which the app reads to show an
// "Added" category in the trace picker.
//
//   node tools/build-traces.mjs
//
// Drop PNG or JPG line art into traces/ first. Filenames become the labels:
// "space-cat.png" shows up as "Space cat".

import { readdirSync, statSync, writeFileSync } from 'node:fs';
import { join, extname, basename } from 'node:path';

const DIR = 'traces';
const OK = new Set(['.png', '.jpg', '.jpeg', '.webp', '.gif']);
const MAX_MB = 2;

function label(file) {
  const stem = basename(file, extname(file))
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  return stem.charAt(0).toUpperCase() + stem.slice(1);
}

const entries = [];
const skipped = [];

for (const file of readdirSync(DIR).sort()) {
  if (!OK.has(extname(file).toLowerCase())) continue;
  const mb = statSync(join(DIR, file)).size / 1048576;
  if (mb > MAX_MB) {
    skipped.push(`${file} (${mb.toFixed(1)} MB - over the ${MAX_MB} MB limit)`);
    continue;
  }
  entries.push({ file, name: label(file) });
}

writeFileSync(join(DIR, 'traces.json'), JSON.stringify(entries, null, 2) + '\n');

console.log(`traces.json written with ${entries.length} trace${entries.length === 1 ? '' : 's'}`);
for (const e of entries) console.log(`  - ${e.name}  (${e.file})`);
if (skipped.length) {
  console.log('\nskipped:');
  for (const s of skipped) console.log(`  ! ${s}`);
}
if (!entries.length) {
  console.log('\nNothing found. Put .png or .jpg files in traces/ and run this again.');
}
