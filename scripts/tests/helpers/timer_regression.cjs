#!/usr/bin/env node
'use strict';

/**
 * Regression for the game-engine fixture's pause/resume lifecycle contract.
 *
 * Run with --root <game-engine project> --mode owner|integration.
 * The source under --root is read and transpiled in memory; nothing is written.
 * Owner assertions: elapsed time and frame count survive pause/resume, paused
 * wall time is excluded, the next delta is local to resume, and a new session
 * starts from zero. For pre-fix Timer implementations, stop/start is the legacy
 * pause/resume path: exercise it before checking the new methods so the original
 * code fails for its actual timing reset, rather than a missing-method error.
 * Integration assertions run real GameEngine.start/pause/resume/stop methods,
 * DefaultGameLoop and PerformanceTimer with a deterministic clock/RAF queue.
 *
 * Limits: this is an isolated regression harness, not a type checker or module
 * resolution test. Imports are removed only for these known fixture modules;
 * TypeScript's private fields are injected after transpilation to avoid DOM
 * initialization. Rendering and scene dependencies are controlled substitutes.
 * Browser initialization, input/audio providers and real scheduling are untested.
 */

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { stripTypeScriptTypes } = require('node:module');

function options(argv) {
  const result = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i];
    if (!['--root', '--mode'].includes(key) || !argv[i + 1] || result[key]) {
      throw new Error('Usage: timer_regression.cjs --root PATH --mode owner|integration');
    }
    result[key] = argv[i + 1];
  }
  assert.ok(result['--root'], '--root is required');
  assert.ok(['owner', 'integration'].includes(result['--mode']), '--mode must be owner or integration');
  return { root: path.resolve(result['--root']), mode: result['--mode'] };
}

function close(actual, expected, label) {
  assert.ok(Number.isFinite(actual) && Math.abs(actual - expected) < 1e-9,
    `${label}: expected ${expected}, got ${actual}`);
}

function load(root, mode) {
  const files = mode === 'owner'
    ? ['src/services/impl/timer/timer.ts']
    : ['src/models/engine.ts', 'src/services/impl/timer/timer.ts',
      'src/pipelines/gameloop/fixed.timestep.ts',
      'src/pipelines/gameloop/game.loop.ts', 'src/interface/engine.ts'];
  let now = 1000;
  let sequence = 0;
  const frames = new Map();
  const errors = [];
  const context = vm.createContext({
    performance: { now: () => now },
    console: { error: (...args) => errors.push(args.map(String).join(' ')) },
    requestAnimationFrame: callback => {
      frames.set(++sequence, callback);
      return sequence;
    },
    cancelAnimationFrame: id => frames.delete(id),
  });
  for (const file of files) {
    const source = fs.readFileSync(path.join(root, file), 'utf8')
      .replace(/^import\s[\s\S]*?\bfrom\s+['"][^'"]+['"];?\s*/gm, '');
    const javascript = stripTypeScriptTypes(source, { mode: 'transform' })
      .replace(/\bexport\s+/g, '');
    vm.runInContext(javascript, context, { filename: file });
  }
  return {
    context,
    errors,
    frames,
    at(value) { now = value; },
    frame(value) {
      now = value;
      assert.equal(frames.size, 1, 'exactly one animation frame must be scheduled');
      const [id, callback] = frames.entries().next().value;
      frames.delete(id);
      callback(value);
      assert.equal(errors.length, 0, `frame error: ${errors.join('; ')}`);
    },
  };
}

function owner(root) {
  const clock = load(root, 'owner');
  const timer = vm.runInContext('new PerformanceTimer()', clock.context);
  timer.start();
  clock.at(1100);
  close(timer.tick(), 0.1, 'first active delta');
  close(timer.getElapsedTime(), 0.1, 'elapsed before pause');
  assert.equal(timer.getFrameCount(), 1, 'frames before pause');

  const explicit = typeof timer.pause === 'function' && typeof timer.resume === 'function';
  if (explicit) timer.pause(); else timer.stop();
  clock.at(5100);
  close(timer.getElapsedTime(), 0.1, 'elapsed is frozen throughout pause');
  assert.equal(timer.tick(), 0, 'paused timer must not advance');
  if (explicit) timer.resume(); else timer.start();
  clock.at(5200);
  close(timer.tick(), 0.1, 'resumed delta excludes paused wall time');
  close(timer.getElapsedTime(), 0.2, 'elapsed continuity across pause/resume');
  assert.equal(timer.getFrameCount(), 2, 'frame continuity across pause/resume');
  assert.ok(explicit, 'revised Timer contract provides explicit pause() and resume()');

  timer.stop();
  clock.at(7000);
  timer.start();
  close(timer.getElapsedTime(), 0, 'new session elapsed resets');
  assert.equal(timer.getFrameCount(), 0, 'new session frame count resets');
  clock.at(7100);
  close(timer.tick(), 0.1, 'new session delta');
  close(timer.getElapsedTime(), 0.1, 'new session elapsed');
  assert.equal(timer.getFrameCount(), 1, 'new session first frame');
}

function integration(root) {
  const clock = load(root, 'integration');
  const objects = vm.runInContext(`(() => {
    const config = { canvasId: 'test', width: 1, height: 1, fixedTimestep: 0.05 };
    const timer = new PerformanceTimer();
    const loop = new DefaultGameLoop(config, timer, new FixedTimestep(0.05));
    const engine = new GameEngine(config);
    const observed = { updates: 0, renders: 0 };
    engine.initialized = true;
    engine.gameLoop = loop;
    engine.sceneManager = { update() { observed.updates += 1; } };
    engine.renderPipeline = {
      beginFrame() { observed.renders += 1; }, endFrame() {}
    };
    return { engine, timer, observed, states: EngineState };
  })()`, clock.context);
  const { engine, timer, observed, states } = objects;
  engine.start();
  assert.equal(engine.getState(), states.Running);
  clock.frame(1100);
  assert.equal(observed.renders, 1);
  assert.equal(timer.getFrameCount(), 1);
  engine.pause();
  assert.equal(engine.getState(), states.Paused);
  assert.equal(clock.frames.size, 0, 'Engine.pause cancels the scheduled frame');
  clock.at(5100);
  close(timer.getElapsedTime(), 0.1, 'Engine pause preserves elapsed time');
  engine.resume();
  assert.equal(engine.getState(), states.Running);
  clock.frame(5200);
  close(timer.getDeltaTime(), 0.1, 'Engine resumed delta excludes pause');
  close(timer.getElapsedTime(), 0.2, 'Engine pause/resume elapsed continuity');
  assert.equal(timer.getFrameCount(), 2, 'Engine pause/resume frame continuity');
  assert.equal(observed.renders, 2, 'one render per active frame');
  assert.equal(observed.updates, 4, 'paused interval adds no fixed updates');
  engine.stop();
  assert.equal(engine.getState(), states.Stopped);
  assert.equal(clock.frames.size, 0);
  clock.at(7000);
  engine.start();
  close(timer.getElapsedTime(), 0, 'Engine restart creates a fresh timing session');
  assert.equal(timer.getFrameCount(), 0);
  clock.frame(7100);
  assert.equal(timer.getFrameCount(), 1);
  engine.stop();
}

try {
  const { root, mode } = options(process.argv.slice(2));
  ({ owner, integration })[mode](root);
  console.log(`PASS timer regression: ${mode}`);
} catch (error) {
  console.error(`FAIL timer regression: ${error.message}`);
  process.exitCode = 1;
}
