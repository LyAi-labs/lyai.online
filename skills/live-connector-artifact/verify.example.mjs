/**
 * verify.example.mjs — arnés de verificación para un live-connector-artifact.
 *
 * PLANTILLA. Cópiala junto a tu página, NO la publiques: este archivo inyecta
 * un `window.claude` FALSO. La página publicada nunca debe contener el mock.
 *
 * Qué hace:
 *   - Inyecta un window.claude mock ANTES de que cargue la página
 *     (page.addInitScript), imitando el contrato mcp 0.2.31: use() resuelve en
 *     un tick, callTool devuelve {payload}, watchTool entrega en un microtask y
 *     devuelve un unsubscribe SÍNCRONO.
 *   - Recorre escenarios: happy / vacío(null) / error-por-código.
 *   - Captura índice·detalle·búsqueda en claro + oscuro + móvil.
 *   - Afirma CERO pageerror.
 *
 * Uso:
 *   npm i -D playwright   (o usa el chromium del entorno)
 *   node verify.example.mjs
 *
 * Rellena SOLO las dos zonas marcadas [ADAPTAR]:
 *   1) PAGE_URL     → ruta a tu página bajo prueba.
 *   2) mockPayload  → la FORMA del payload que observaste (paso 2 de la skill),
 *                     con datos INVENTADOS de prueba. Nunca los valores reales.
 */

import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';

// ── [ADAPTAR 1] Página bajo prueba ────────────────────────────────────────────
const PAGE_URL = pathToFileURL(new URL('./page.under-test.html', import.meta.url).pathname).href;

// Config del entorno: en algunos sandboxes hay un chromium preinstalado.
const LAUNCH = { /* executablePath: '/opt/pw-browsers/chromium' */ };

// ── [ADAPTAR 2] Forma observada del payload (datos de prueba, NO reales) ──────
// Devuelve lo que tu conector devuelve en `result.payload` para cada (tool,input).
// Refleja la FORMA que observaste en vivo; inventa los valores.
function mockPayload(tool, input) {
  switch (tool) {
    case '<tool_1>': // p.ej. listar elementos
      return {
        items: Array.from({ length: 8 }, (_, i) => ({
          id: `demo-${i + 1}`,
          title: `Elemento de prueba ${i + 1}`,
          date: '2026-01-0' + ((i % 9) + 1),
        })),
      };
    case '<tool_2>': // p.ej. detalle de uno
      return {
        id: input?.id ?? 'demo-1',
        title: `Detalle de prueba ${input?.id ?? 'demo-1'}`,
        body: 'Cuerpo inventado para verificación. No son datos reales.',
      };
    default:
      return { ok: true };
  }
}

/**
 * Fábrica del mock de window.claude, serializada e inyectada en la página.
 * `scenario` controla el comportamiento:
 *   'happy'            → use('mcp') ok; callTool/watchTool devuelven payload.
 *   'no-connector'     → use('mcp') resuelve null (rama de ausencia).
 *   'err:<code>'       → callTool/watchTool fallan con ese McpErrorCode.
 */
function installClaudeMock(scenario, payloadFnSource) {
  // Nota: esta función se ejecuta DENTRO del navegador (addInitScript), así que
  // recibe el source de mockPayload como string y lo reconstruye ahí.
  const mockPayload = new Function('return (' + payloadFnSource + ')')();
  const CACHE_STAMP = 1767225600000; // epoch ms fijo → "actualizado" determinista

  function makeError(code) {
    const retryable = code === 'server_unavailable' || code === 'rate_limited';
    return { code, message: 'mock ' + code, ...(retryable ? { retryable: true } : {}) };
  }

  const mcp = {
    async callTool(server, tool, input) {
      if (scenario.startsWith('err:')) throw makeError(scenario.slice(4));
      return { content: [], payload: mockPayload(tool, input), cache: { storedAt: CACHE_STAMP, revalidating: false } };
    },
    watchTool(server, tool, input, handler) {
      // Unsubscribe SÍNCRONO; primera entrega en un microtask (como el contrato).
      let live = true;
      queueMicrotask(() => {
        if (!live) return;
        if (scenario.startsWith('err:')) handler({ type: 'error', error: makeError(scenario.slice(4)) });
        else handler({ type: 'data', result: { content: [], payload: mockPayload(tool, input), cache: { storedAt: CACHE_STAMP, revalidating: false } } });
      });
      return () => { live = false; };
    },
    async listTools() {
      if (scenario === 'no-connector') return { servers: [] };
      return { servers: [{ server: '<nombre exacto del conector>', authStatus: 'connected', tools: [{ name: '<tool_1>', description: '' }, { name: '<tool_2>', description: '' }] }] };
    },
    async invalidate() {},
  };

  const memo = new Map();
  window.claude = {
    use(name) {
      if (!memo.has(name)) {
        memo.set(name, new Promise((resolve) => {
          // Resuelve DESPUÉS del primer run síncrono, como el runtime real.
          setTimeout(() => resolve(name === 'mcp' && scenario !== 'no-connector' ? mcp : null), 0);
        }));
      }
      return memo.get(name);
    },
  };
}

const THEMES = ['light', 'dark'];
const VIEWPORTS = { desktop: { width: 1280, height: 900 }, mobile: { width: 390, height: 780 } };
// [ADAPTAR] Los escenarios que tu página debe superar. Añade un err:<code> por
// cada código con arreglo propio en tu UI.
const SCENARIOS = ['happy', 'no-connector', 'err:needs_reauth', 'err:server_unavailable'];

let failures = 0;

const browser = await chromium.launch(LAUNCH);
try {
  for (const scenario of SCENARIOS) {
    for (const theme of THEMES) {
      for (const [vpName, viewport] of Object.entries(VIEWPORTS)) {
        const ctx = await browser.newContext({ viewport, colorScheme: theme });
        const page = await ctx.newPage();
        const errors = [];
        page.on('pageerror', (e) => errors.push(String(e)));
        page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

        // Inyecta el window.claude mock ANTES de que corra el script de la página.
        // Serializamos el instalador y el source de mockPayload como string.
        await page.addInitScript(
          `(${installClaudeMock.toString()})(${JSON.stringify(scenario)}, ${JSON.stringify(mockPayload.toString())});`,
        );
        // Fuerza el tema por si la página usa data-theme además de prefers-color-scheme.
        // addInitScript corre antes del DOM: guarda hasta que exista documentElement.
        await page.addInitScript((t) => {
          const apply = () => { if (document.documentElement) document.documentElement.setAttribute('data-theme', t); };
          apply();
          document.addEventListener('DOMContentLoaded', apply);
        }, theme);

        await page.goto(PAGE_URL, { waitUntil: 'load' });
        await page.waitForTimeout(400); // deja resolver use()/watchTool

        const tag = `${scenario}·${theme}·${vpName}`;
        if (errors.length) {
          failures++;
          console.log(`✗ ${tag}  pageerror:\n   ${errors.join('\n   ')}`);
        } else {
          console.log(`✓ ${tag}`);
        }
        await page.screenshot({ path: `shot_${scenario.replace(/[:]/g, '-')}_${theme}_${vpName}.png` });
        await ctx.close();
      }
    }
  }
} finally {
  await browser.close();
}

console.log(failures ? `\nFALLÓ: ${failures} combinación(es) con pageerror.` : '\nOK: cero pageerror en todos los escenarios.');
process.exit(failures ? 1 : 0);
