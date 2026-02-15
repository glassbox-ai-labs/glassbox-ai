const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const ASSETS_DIR = path.join(__dirname, 'assets');

// Physical sizes in cm → pixels at given DPI
// Front patch: ~12 × 16 cm
// Back patch:  ~14 × 18 cm
function cmToPixels(cm, dpi) {
  return Math.round(cm * dpi / 2.54);
}

const PATCHES = [
  {
    name: 'front-patch',
    widthCm: 12,
    heightCm: 16,
    html: () => getFrontPatchHTML(),
  },
  {
    name: 'back-patch',
    widthCm: 14,
    heightCm: 18,
    html: () => getBackPatchHTML(),
  },
];

const DPIS = [300, 400, 500];

function getFrontPatchHTML() {
  return `<!DOCTYPE html>
<html><head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0a0a0a;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }
  .front-patch {
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .glassbox-icon { margin-bottom: 5%; }
  .f-brand { text-align: center; margin-bottom: 3%; }
  .f-brand-text {
    font-family: 'Inter', sans-serif;
    font-size: 7vw;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }
  .f-brand-text .green { color: #4ade80; }
  .f-brand-text .white { color: #ffffff; }
  .f-not {
    font-family: 'Inter', sans-serif;
    font-size: 2.8vw;
    color: rgba(255,255,255,0.6);
    letter-spacing: 0.4em;
    text-transform: lowercase;
    margin-bottom: 2%;
    text-align: center;
  }
  .f-black {
    font-family: 'Inter', sans-serif;
    font-size: 5vw;
    font-weight: 400;
    color: #f87171;
    letter-spacing: 0.12em;
    text-decoration: line-through;
    text-decoration-thickness: 2px;
    opacity: 0.8;
    text-align: center;
  }
</style>
</head>
<body>
<div class="front-patch">
  <div class="glassbox-icon">
    <svg width="45vw" height="45vw" viewBox="0 0 150 150" fill="none">
      <!-- ALL SOLID COLORS - zero opacity, zero rgba - DTG print safe -->
      <!-- Body (central axis) -->
      <line x1="75" y1="24" x2="75" y2="125" stroke="#4ade80" stroke-width="8"/>
      <!-- Antennae -->
      <path d="M75 30 Q56 14 48 6" fill="none" stroke="#4ade80" stroke-width="4"/>
      <circle cx="48" cy="6" r="7" fill="#4ade80"/>
      <path d="M75 30 Q94 14 102 6" fill="none" stroke="#4ade80" stroke-width="4"/>
      <circle cx="102" cy="6" r="7" fill="#4ade80"/>
      <!-- Left upper wing -->
      <path d="M75 36 Q24 28 14 60 Q10 80 46 88 Q66 90 75 74 Z" fill="#143d28" stroke="#4ade80" stroke-width="4"/>
      <!-- Right upper wing -->
      <path d="M75 36 Q126 28 136 60 Q140 80 104 88 Q84 90 75 74 Z" fill="#143d28" stroke="#4ade80" stroke-width="4"/>
      <!-- Left lower wing -->
      <path d="M75 78 Q36 84 24 106 Q28 120 54 114 Q70 110 75 96 Z" fill="#122e20" stroke="#4ade80" stroke-width="3.5"/>
      <!-- Right lower wing -->
      <path d="M75 78 Q114 84 126 106 Q122 120 96 114 Q80 110 75 96 Z" fill="#122e20" stroke="#4ade80" stroke-width="3.5"/>
      <!-- Wing veins -->
      <path d="M75 36 Q48 50 26 70" fill="none" stroke="#2d8a56" stroke-width="3"/>
      <path d="M75 36 Q42 56 18 76" fill="none" stroke="#2d8a56" stroke-width="2.5"/>
      <path d="M75 36 Q102 50 124 70" fill="none" stroke="#2d8a56" stroke-width="3"/>
      <path d="M75 36 Q108 56 132 76" fill="none" stroke="#2d8a56" stroke-width="2.5"/>
      <!-- Agent nodes (LARGE, SOLID) -->
      <circle cx="46" cy="58" r="18" fill="#1a5c38"/>
      <circle cx="46" cy="58" r="14" fill="#4ade80"/>
      <circle cx="104" cy="58" r="18" fill="#1a5c38"/>
      <circle cx="104" cy="58" r="14" fill="#4ade80"/>
      <circle cx="75" cy="100" r="18" fill="#1a5c38"/>
      <circle cx="75" cy="100" r="14" fill="#4ade80"/>
      <!-- Agent connections -->
      <path d="M46 58 Q75 46 104 58" fill="none" stroke="#2d8a56" stroke-width="3.5"/>
      <path d="M46 58 Q58 80 75 100" fill="none" stroke="#2d8a56" stroke-width="3.5"/>
      <path d="M104 58 Q92 80 75 100" fill="none" stroke="#2d8a56" stroke-width="3.5"/>
    </svg>
  </div>
  <div class="f-brand">
    <span class="f-brand-text"><span class="green">Glass</span><span class="white">Box AI</span></span>
  </div>
  <div class="f-not">-- not --</div>
  <div class="f-black">BlackBox AI</div>
</div>
</body></html>`;
}

function getBackPatchHTML() {
  return `<!DOCTYPE html>
<html><head>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0a0a0a;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    font-family: 'JetBrains Mono', monospace;
  }
  .back-patch {
    width: 88vw;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .diff-header {
    width: 100%;
    padding: 2.2vh 3vw;
    background: #161b22;
    border: 3px solid #4a5568;
    border-bottom: none;
    border-radius: 1.8vw 1.8vw 0 0;
    font-size: 2.8vw;
    color: #8b949e;
    display: flex;
    align-items: center;
    gap: 1.5vw;
  }
  .diff-icon { width: 3vw; height: 3vw; }
  .diff-repo { color: #58a6ff; }
  .diff-body {
    width: 100%;
    background: #0d1117;
    border: 3px solid #4a5568;
    border-radius: 0 0 1.8vw 1.8vw;
    padding: 3vh 0;
    font-size: 3.2vw;
    line-height: 2.6;
  }
  .diff-line { padding: 0 3vw; white-space: nowrap; }
  .diff-line.del { background: rgba(248,113,113,0.1); color: #ffa198; }
  .diff-line.add { background: rgba(74,222,128,0.1); color: #7ee787; }
  .diff-line.blank { color: transparent; user-select: none; line-height: 0.8; font-size: 1vw; }
  .var { color: #ffa657; }
  .op  { color: #79c0ff; }
  .fn  { color: #d2a8ff; }
  .str { color: #a5d6ff; }
  .back-tagline {
    margin-top: 5vh;
    text-align: center;
  }
  .tagline-main {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3vw;
    font-weight: 400;
    color: #7ee787;
    letter-spacing: 0.1em;
  }
</style>
</head>
<body>
<div class="back-patch">
  <div class="diff-header">
    <svg class="diff-icon" viewBox="0 0 16 16" fill="#8b949e">
      <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
    </svg>
    <span class="diff-repo">agentic-trust-labs/glassbox-ai</span>
  </div>
  <div class="diff-body">
    <div class="diff-line del">- <span class="var">decisions</span> <span class="op">=</span> <span class="fn">blackbox</span>(<span class="var">model</span>)</div>
    <div class="diff-line del">- <span class="var">trust</span>     <span class="op">=</span> <span class="str">"assumed"</span></div>
    <div class="diff-line del">- <span class="var">oversight</span>  <span class="op">=</span> <span class="str">None</span></div>
    <div class="diff-line blank">.</div>
    <div class="diff-line" style="padding: 1vh 3vw;"><span style="display:block; border-top: 3px solid #4a5568;"></span></div>
    <div class="diff-line blank">.</div>
    <div class="diff-line add">+ <span class="var">agents</span>    <span class="op">=</span> <span class="fn">debate</span>(<span class="var">decisions</span>)</div>
    <div class="diff-line add">+ <span class="var">trust</span>     <span class="op">=</span> <span class="fn">earned</span>(<span class="var">verified</span>)</div>
    <div class="diff-line add">+ <span class="var">oversight</span>  <span class="op">=</span> <span class="fn">transparent</span>(<span class="var">always</span>)</div>
  </div>
  <div class="back-tagline">
    <div class="tagline-main">trustable agents for scalable solutions</div>
  </div>
</div>
</body></html>`;
}

async function exportPatches() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  for (const patch of PATCHES) {
    for (const dpi of DPIS) {
      const widthPx = cmToPixels(patch.widthCm, dpi);
      const heightPx = cmToPixels(patch.heightCm, dpi);

      // Use a base viewport and scale factor
      // Base at 96 DPI equivalent, scale up
      const scaleFactor = dpi / 96;
      const baseW = Math.round(widthPx / scaleFactor);
      const baseH = Math.round(heightPx / scaleFactor);

      const page = await browser.newPage();
      await page.setViewport({
        width: baseW,
        height: baseH,
        deviceScaleFactor: scaleFactor,
      });

      const html = patch.html();
      await page.setContent(html, { waitUntil: 'networkidle0' });

      // Wait for fonts to load
      await page.evaluate(() => document.fonts.ready);
      await new Promise(r => setTimeout(r, 1500));

      const filename = `${patch.name}-${dpi}dpi.png`;
      const filepath = path.join(ASSETS_DIR, filename);

      await page.screenshot({
        path: filepath,
        omitBackground: false, // SOLID BLACK background for print
        type: 'png',
      });

      const stats = fs.statSync(filepath);
      console.log(`✓ ${filename} — ${widthPx}×${heightPx}px (${(stats.size / 1024).toFixed(0)} KB)`);

      await page.close();
    }
  }

  await browser.close();
  console.log(`\nAll PNGs saved to: ${ASSETS_DIR}`);
}

exportPatches().catch(console.error);
