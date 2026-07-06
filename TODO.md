# TODO

## Step 1: Add safety controller to Python consciousness loop
- [x] Inspect `bow-of-Achilles/consciousness_loop.py` for iteration flow and log structure
- [x] Implement risk scoring based on entropy/coherence/density_boost/brain_energy

- [ ] Add throttle/hold-off policy: when risk is high, skip modification or reduce density_boost
- [ ] Bias target selection toward safer metrics when possible
- [ ] Record `safety_events` into `ITERATION_LOG`


## Step 2: Smoke test
- [ ] Run `python bow-of-Achilles/consciousness_loop.py --max-iterations 5`
- [ ] Verify `data/mana_ciel/stack/consciousness_iteration_log.json` includes `safety_events`

## Step 3 (optional): Wire to JS monitor
- [ ] If desired, expose safety status to `unified-consciousness-render` via a JSON status file
