// ESM-compatible bridge script so Python can trigger the Magi-Zone escape/merge pipeline.
// Usage:
// node run_escape_pipeline.js '<voicePhrasesJson>' '<optionsJson>'
// Where optionsJson: { origin3D: [x,y,z], movementVector: [dx,dy,dz], inDanger?: boolean, defaultTier?: number }

import { runCastingPipeline } from './dist/index.js';

const voicePhrasesJson = process.argv[2];
const optionsJson = process.argv[3];

if (!voicePhrasesJson || !optionsJson) {
  console.error('Missing args. Expected: <voicePhrasesJson> <optionsJson>');
  process.exit(2);
}

let voicePhrases;
let options;
try {
  voicePhrases = JSON.parse(voicePhrasesJson);
  options = JSON.parse(optionsJson);
} catch (e) {
  console.error('Failed to parse args JSON:', e && e.stack ? e.stack : e);
  process.exit(3);
}

const result = runCastingPipeline(voicePhrases, options);

// Output only the parts Python needs.
const first = (result && result.results && result.results[0]) ? result.results[0] : null;
const payload = {
  waveState: result.waveState,
  upscale: first?.upscale ?? null,
  enforceResult: first?.enforceResult ?? null,
  zoneMap3D: first?.zoneMap3D ?? null,
  tier: first?.tier ?? null,
  permitted: first?.permitted ?? null,
  executed: first?.executed ?? null,
};

process.stdout.write(JSON.stringify(payload));


