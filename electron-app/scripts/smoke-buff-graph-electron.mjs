import { createServer } from 'node:http';
import { once } from 'node:events';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';

const require = createRequire(import.meta.url);
const electronPath = require('electron');

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(__dirname, '..');
const fixturePath = path.join(appRoot, 'tests', 'fixtures', 'buff-graph', 'ui-smoke-catalog.json');
const catalog = JSON.parse(await readFile(fixturePath, 'utf8'));

const apiPort = Number(process.env.ZSIM_BUFF_GRAPH_SMOKE_API_PORT ?? '8000');
const debugPort = Number(process.env.ZSIM_BUFF_GRAPH_SMOKE_DEBUG_PORT ?? '9223');
const runParityMatrix = process.argv.includes('--run-parity-matrix');
const graphStore = new Map();
const requestLog = [];
let matrixRunPayload;

const matrixContract = {
  status: 'not_available',
  reason: 'UI smoke matrix fixture is not the full campaign parity matrix.',
  required_command: 'cd electron-app; pnpm smoke:buff-graph:electron -- --run-parity-matrix',
  evidence_path:
    'scripts/buff_agents/evidence/buff-20260702-buffxlogic-react-flow-visual-authoring/ui-driven-full-simulation-matrix.json',
  command_status: 'runner_required',
  run_id: null,
  ui_driven: true,
  full_simulation_matrix: true,
  full_parity_verified: false,
  candidate_harness_id: 'alice-cinema6-api-candidate-harness',
  candidate_runtime_status: 'visual_graph_candidate',
  candidate_parity_passed: true,
  candidate_slice_evidence: {
    graph_id: 'alice-cinema6-candidate-parity',
    api_endpoint: '/api/buff-graphs/alice-cinema6-candidate-parity/parity',
    status: 'candidate_harness_passed',
    full_parity_verified: false,
  },
  candidate_wave_evidence: [
    {
      wave_id: 'pure-and-low-risk-stateless',
      candidate_harness_id: 'pure-low-risk-generated-spec-candidate-harness',
      status: 'candidate_harness_wave_available',
      case_ids: [
        'cordis-germina-crit-rate-bonus-candidate',
        'rainforest-gourmet-atk-bonus-candidate',
        'astra-yao-idyllic-cadenza-candidate',
      ],
      candidate_runtime_status: 'visual_graph_candidate',
      candidate_parity_passed: true,
      full_parity_verified: false,
      evidence_path:
        'scripts/buff_agents/evidence/buff-20260702-buffxlogic-react-flow-visual-authoring/oracle-graph-runtime-candidate-harness-pure-low-risk.json',
    },
    {
      wave_id: 'enemy-state-edge-triggers',
      candidate_harness_id: 'enemy-state-generated-spec-candidate-harness',
      status: 'candidate_harness_wave_available',
      case_ids: [
        'anomaly-debuff-exit-judge-candidate',
        'miyabi-core-skill-frost-burn-candidate',
        'branch-blade-song-crit-rate-bonus-candidate',
      ],
      candidate_runtime_status: 'visual_graph_candidate',
      candidate_parity_passed: true,
      full_parity_verified: false,
      evidence_path:
        'scripts/buff_agents/evidence/buff-20260702-buffxlogic-react-flow-visual-authoring/oracle-graph-runtime-candidate-harness-enemy-state.json',
    },
    {
      wave_id: 'dynamic-owner-equipper',
      candidate_harness_id: 'dynamic-owner-generated-spec-candidate-harness',
      status: 'candidate_harness_wave_available',
      case_ids: [
        'dynamic-owner-astral-voice-candidate',
        'dynamic-owner-hellfire-gears-sp-r-bonus-candidate',
        'dynamic-owner-ice-jade-teapot-extra-dmg-bonus-candidate',
        'dynamic-owner-zanshin-herb-case-candidate',
      ],
      candidate_runtime_status: 'visual_graph_candidate',
      candidate_parity_passed: true,
      full_parity_verified: false,
      evidence_path:
        'scripts/buff_agents/evidence/buff-20260702-buffxlogic-react-flow-visual-authoring/oracle-graph-runtime-candidate-harness-dynamic-owner.json',
    },
    {
      wave_id: 'runtime-command-scheduled-signal',
      candidate_harness_id: 'runtime-scheduled-generated-spec-candidate-harness',
      status: 'candidate_harness_wave_available',
      case_ids: [
        'runtime-scheduled-astra-yao-core-passive-atk-bonus-candidate',
        'runtime-scheduled-branch-blade-song-crit-damage-bonus-candidate',
        'runtime-scheduled-magnetic-storm-charlie-sp-recover-candidate',
      ],
      candidate_runtime_status: 'visual_graph_candidate',
      candidate_parity_passed: true,
      full_parity_verified: false,
      evidence_path:
        'scripts/buff_agents/evidence/buff-20260702-buffxlogic-react-flow-visual-authoring/oracle-graph-runtime-candidate-harness-runtime-scheduled.json',
    },
    {
      wave_id: 'character-manager-side-effects',
      candidate_harness_id: 'character-manager-generated-spec-candidate-harness',
      status: 'candidate_harness_wave_available',
      case_ids: [
        'character-manager-alice-cinema-6-trigger-candidate',
        'character-manager-vivian-coattack-trigger-candidate',
        'character-manager-yixuan-cinema-1-trigger-candidate',
      ],
      candidate_runtime_status: 'visual_graph_candidate',
      candidate_parity_passed: true,
      full_parity_verified: false,
      evidence_path:
        'scripts/buff_agents/evidence/buff-20260702-buffxlogic-react-flow-visual-authoring/oracle-graph-runtime-candidate-harness-character-manager.json',
    },
  ],
  matrix_scope: [
    'react-flow-ui-open-edit-save-validate',
    'react-flow-ui-initiated-parity',
    'all-runnable-apl-config-matrix',
    'gap-dedicated-trigger-scenarios',
    'legacy-python-xlogic-vs-graph-runtime',
  ],
};

const json = (res, status, payload) => {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET,POST,PUT,OPTIONS',
    'access-control-allow-headers': 'content-type',
    'content-type': 'application/json',
    'content-length': Buffer.byteLength(body),
  });
  res.end(body);
};

const readBody = async req => {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const text = Buffer.concat(chunks).toString('utf8');
  return text ? JSON.parse(text) : undefined;
};

const hasForbiddenCodeNode = spec =>
  Array.isArray(spec?.nodes) &&
  spec.nodes.some(node =>
    /(?:python|script|code|eval|exec)/i.test(
      `${node.block_id ?? ''} ${node.adapter_id ?? ''} ${node.family ?? ''}`,
    ),
  );

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? '/', `http://127.0.0.1:${apiPort}`);
    requestLog.push(`${req.method} ${url.pathname}`);

    if (req.method === 'OPTIONS') {
      json(res, 204, {});
      return;
    }

    if (req.method === 'GET' && url.pathname === '/health') {
      json(res, 200, { message: 'buff graph smoke api ready' });
      return;
    }

    if (req.method === 'GET' && url.pathname === '/api/buff-graphs') {
      json(res, 200, { data: { graphs: [...graphStore.values()] } });
      return;
    }

    if (req.method === 'GET' && url.pathname === '/api/buff-graphs/migration/catalog') {
      json(res, 200, { data: catalog });
      return;
    }

    if (req.method === 'GET' && url.pathname === '/api/buff-graphs/parity/matrix') {
      json(res, 200, {
        data: matrixContract,
      });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/api/buff-graphs/parity/matrix/run') {
      matrixRunPayload = {
        ...matrixContract,
        status: 'run_requested',
        reason:
          'UI smoke matrix run request accepted by fixture backend; this is not full parity evidence.',
        command_status: 'request_recorded',
        run_id:
          'buff-20260702-buffxlogic-react-flow-visual-authoring:ui-driven-full-simulation-matrix',
      };
      json(res, 200, { data: matrixRunPayload });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/api/buff-graphs') {
      const body = await readBody(req);
      const spec = body?.spec;
      if (!spec?.graph_id) {
        json(res, 400, { detail: 'missing spec.graph_id' });
        return;
      }
      if (hasForbiddenCodeNode(spec)) {
        json(res, 400, { detail: 'custom code nodes are forbidden' });
        return;
      }
      graphStore.set(spec.graph_id, spec);
      json(res, 200, { data: spec });
      return;
    }

    const graphMatch = url.pathname.match(/^\/api\/buff-graphs\/([^/]+)(?:\/([^/]+))?$/);
    if (graphMatch) {
      const [, graphId, action] = graphMatch;
      if (req.method === 'PUT' && !action) {
        const body = await readBody(req);
        const spec = body?.spec;
        if (!spec?.graph_id || spec.graph_id !== graphId) {
          json(res, 400, { detail: 'graph id mismatch' });
          return;
        }
        if (hasForbiddenCodeNode(spec)) {
          json(res, 400, { detail: 'custom code nodes are forbidden' });
          return;
        }
        graphStore.set(graphId, spec);
        json(res, 200, { data: spec });
        return;
      }

      if (req.method === 'POST' && action === 'validate') {
        json(res, 200, { data: { valid: graphStore.has(graphId), errors: [] } });
        return;
      }

      if (req.method === 'POST' && action === 'compile') {
        const spec = graphStore.get(graphId);
        json(res, 200, {
          data: {
            compiled: Boolean(spec),
            errors: [],
            execution_order: Array.isArray(spec?.nodes) ? spec.nodes.map(node => node.node_id) : [],
          },
        });
        return;
      }

      if (req.method === 'POST' && action === 'parity') {
      json(res, 200, {
          data: {
            status:
              graphId === 'alice-cinema6-candidate-parity'
                ? 'candidate_harness_passed'
                : 'ready_for_oracle',
            graph_id: graphId,
            reason: 'UI smoke parity request accepted by fixture backend.',
            candidate_harness_id:
              graphId === 'alice-cinema6-candidate-parity'
                ? 'alice-cinema6-api-candidate-harness'
                : null,
            candidate_runtime_status:
              graphId === 'alice-cinema6-candidate-parity'
                ? 'visual_graph_candidate'
                : null,
            candidate_parity_passed: graphId === 'alice-cinema6-candidate-parity',
            full_parity_verified: false,
          },
        });
        return;
      }
    }

    json(res, 404, { detail: `No smoke route for ${req.method} ${url.pathname}` });
  } catch (error) {
    json(res, 500, { detail: error instanceof Error ? error.message : String(error) });
  }
});

server.listen(apiPort, '127.0.0.1');
await once(server, 'listening');

let electronProcess;
let websocket;
let smokeMainDir;
const pending = new Map();
let nextMessageId = 1;

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

const waitFor = async (label, probe, timeoutMs = 15000) => {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const result = await probe();
      if (result) return result;
    } catch (error) {
      lastError = error;
    }
    await sleep(120);
  }
  throw new Error(`Timed out waiting for ${label}${lastError ? `: ${lastError.message}` : ''}`);
};

const cdpSend = (method, params = {}) => {
  const id = nextMessageId++;
  websocket.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject, method });
  });
};

const evaluate = async expression => {
  const response = await cdpSend('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (response.exceptionDetails) {
    throw new Error(response.exceptionDetails.text ?? `Runtime.evaluate failed for ${expression}`);
  }
  return response.result?.value;
};

const connectToRenderer = async () => {
  const target = await waitFor('Electron CDP page target', async () => {
    const response = await fetch(`http://127.0.0.1:${debugPort}/json/list`);
    const targets = await response.json();
    return targets.find(item => item.type === 'page' && item.webSocketDebuggerUrl);
  });

  websocket = new WebSocket(target.webSocketDebuggerUrl);
  websocket.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (!message.id) return;
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) {
      waiter.reject(new Error(`${waiter.method} failed: ${message.error.message}`));
    } else {
      waiter.resolve(message.result ?? {});
    }
  });
  await once(websocket, 'open');
  await cdpSend('Runtime.enable');
  await cdpSend('Page.enable');
};

const runUiSmoke = async () => {
  const electronEnv = { ...process.env };
  delete electronEnv.ELECTRON_RUN_AS_NODE;

  smokeMainDir = await mkdtemp(path.join(appRoot, '.tmp-buff-graph-smoke-'));
  const smokeMainPath = path.join(smokeMainDir, 'main.cjs');
  await writeFile(
    smokeMainPath,
    `
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');

const appRoot = process.env.ZSIM_BUFF_GRAPH_SMOKE_APP_ROOT;
const debugPort = process.env.ZSIM_BUFF_GRAPH_SMOKE_DEBUG_PORT;
const apiPort = Number(process.env.ZSIM_BUFF_GRAPH_SMOKE_API_PORT || '8000');
app.commandLine.appendSwitch('remote-debugging-port', debugPort);

let win;
app.whenReady().then(async () => {
  ipcMain.handle('get-ipc-config', async () => ({
    mode: 'http',
    port: apiPort,
    udsPath: '/tmp/zsim_api.sock',
  }));

  win = new BrowserWindow({
    width: 1440,
    height: 800,
    minWidth: 900,
    minHeight: 500,
    show: false,
    webPreferences: {
      preload: path.join(appRoot, 'dist-electron', 'preload.cjs'),
      sandbox: false,
      nodeIntegration: false,
      contextIsolation: true,
    },
  });
  win.setMenu(null);
  win.once('ready-to-show', () => win.show());
  await win.loadFile(path.join(appRoot, 'dist', 'index.html'));
});

app.on('window-all-closed', () => app.quit());
`,
    'utf8',
  );

  electronProcess = spawn(electronPath, [smokeMainPath], {
    cwd: appRoot,
    env: {
      ...electronEnv,
      NODE_ENV: 'production',
      ELECTRON_DISABLE_SECURITY_WARNINGS: 'true',
      ZSIM_BUFF_GRAPH_SMOKE_APP_ROOT: appRoot,
      ZSIM_BUFF_GRAPH_SMOKE_DEBUG_PORT: String(debugPort),
      ZSIM_BUFF_GRAPH_SMOKE_API_PORT: String(apiPort),
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  electronProcess.stdout.on('data', data => process.stdout.write(`[electron] ${data}`));
  electronProcess.stderr.on('data', data => process.stderr.write(`[electron] ${data}`));

  await connectToRenderer();
  await evaluate(`window.location.hash = '#buff-graph'; true`);
  await waitFor('BuffGraph workbench root', () =>
    evaluate(`Boolean(document.querySelector('[data-buff-graph-workbench]'))`),
  );
  await waitFor('BuffGraph template wizard', () =>
    evaluate(`Boolean(document.querySelector('.buff-graph-template-wizard'))`),
  );

  await evaluate(`
    (() => {
      const setValue = (input, value) => {
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        setter.call(input, value);
        input.dispatchEvent(new Event('input', { bubbles: true }));
      };
      const inputs = [...document.querySelectorAll('.buff-graph-template-wizard input')];
      if (inputs.length < 4) throw new Error('Template wizard inputs missing');
      setValue(inputs[0], 'ui-smoke-graph');
      setValue(inputs[1], 'UI Smoke Graph');
      setValue(inputs[2], 'Smoke Owner');
      setValue(inputs[3], 'Buff-Smoke-001');
      const generate = [...document.querySelectorAll('button')].find(button =>
        /Generate Graph/.test(button.textContent || ''),
      );
      if (!generate) throw new Error('Generate Graph button missing');
      generate.click();
      return true;
    })()
  `);

  await waitFor('generated React Flow nodes', () =>
    evaluate(`document.querySelectorAll('.react-flow__node').length >= 2`),
  );

  for (const label of ['Save', 'Validate', 'Parity']) {
    await evaluate(`
      (() => {
        const button = [...document.querySelectorAll('button')].find(item =>
          (item.textContent || '').trim() === '${label}',
        );
        if (!button) throw new Error('${label} button missing');
        button.click();
        return true;
      })()
    `);
    await sleep(250);
  }

  await waitFor('validation and parity result text', () =>
    evaluate(`
      (() => {
        const text = document.body.innerText || '';
        return text.includes('Schema: valid') &&
          text.includes('Compile: compiled') &&
          text.includes('ready_for_oracle');
      })()
    `),
  );

  const overflow = await evaluate(`
    (() => {
      const root = document.documentElement;
      const workbench = document.querySelector('[data-buff-graph-workbench]');
      return {
        documentScrollWidth: root.scrollWidth,
        documentClientWidth: root.clientWidth,
        workbenchScrollWidth: workbench ? workbench.scrollWidth : 0,
        workbenchClientWidth: workbench ? workbench.clientWidth : 0
      };
    })()
  `);

  assert.ok(
    overflow.documentScrollWidth <= overflow.documentClientWidth + 1,
    `document has horizontal overflow: ${JSON.stringify(overflow)}`,
  );
  assert.ok(
    overflow.workbenchScrollWidth <= overflow.workbenchClientWidth + 1,
    `workbench has horizontal overflow: ${JSON.stringify(overflow)}`,
  );

  const saved = graphStore.get('ui-smoke-graph');
  assert.ok(saved, 'UI did not save ui-smoke-graph through the backend API');
  assert.equal(saved.parity_metadata?.template_generated, true);
  assert.equal(hasForbiddenCodeNode(saved), false);
  assert.ok(requestLog.includes('POST /api/buff-graphs/ui-smoke-graph/parity'));

  if (runParityMatrix) {
    await evaluate(`window.location.hash = '#buff-graph:matrix'; true`);
    await waitFor('BuffGraph matrix view', () =>
      evaluate(`Boolean(document.querySelector('[data-buff-graph-view="parity-matrix"]'))`),
    );

    await evaluate(`
      (() => {
        const button = [...document.querySelectorAll('button')].find(item =>
          (item.textContent || '').trim() === 'Run Matrix',
        );
        if (!button) throw new Error('Run Matrix button missing');
        button.click();
        return true;
      })()
    `);

    await waitFor('matrix run request result', () =>
      evaluate(`
        (() => {
          const text = document.body.innerText || '';
          return text.includes('run_requested') &&
            text.includes('ui-driven-full-simulation-matrix') &&
            text.includes('alice-cinema6-api-candidate-harness') &&
            text.includes('candidate_harness_passed') &&
            text.includes('pure-and-low-risk-stateless') &&
            text.includes('rainforest-gourmet-atk-bonus-candidate') &&
            text.includes('enemy-state-edge-triggers') &&
            text.includes('miyabi-core-skill-frost-burn-candidate') &&
            text.includes('dynamic-owner-equipper') &&
            text.includes('dynamic-owner-zanshin-herb-case-candidate') &&
            text.includes('runtime-command-scheduled-signal') &&
            text.includes('runtime-scheduled-astra-yao-core-passive-atk-bonus-candidate') &&
            text.includes('character-manager-side-effects') &&
            text.includes('character-manager-alice-cinema-6-trigger-candidate') &&
            text.includes('full_parity_verified: false');
        })()
      `),
    );

    assert.ok(requestLog.includes('POST /api/buff-graphs/parity/matrix/run'));
    assert.equal(matrixRunPayload?.status, 'run_requested');
    assert.equal(matrixRunPayload?.candidate_harness_id, 'alice-cinema6-api-candidate-harness');
    assert.equal(matrixRunPayload?.candidate_parity_passed, true);
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[0]?.wave_id, 'pure-and-low-risk-stateless');
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[0]?.candidate_parity_passed, true);
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[1]?.wave_id, 'enemy-state-edge-triggers');
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[1]?.candidate_parity_passed, true);
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[2]?.wave_id, 'dynamic-owner-equipper');
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[2]?.candidate_parity_passed, true);
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[3]?.wave_id, 'runtime-command-scheduled-signal');
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[3]?.candidate_parity_passed, true);
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[4]?.wave_id, 'character-manager-side-effects');
    assert.equal(matrixRunPayload?.candidate_wave_evidence?.[4]?.candidate_parity_passed, true);
    assert.equal(matrixRunPayload?.full_parity_verified, false);
  }

  console.log(runParityMatrix ? '[buff-graph-smoke] matrix request passed' : '[buff-graph-smoke] passed');
};

try {
  await runUiSmoke();
} finally {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.close();
  }
  if (electronProcess && !electronProcess.killed) {
    electronProcess.kill();
  }
  if (smokeMainDir) {
    await rm(smokeMainDir, { recursive: true, force: true });
  }
  server.close();
}
