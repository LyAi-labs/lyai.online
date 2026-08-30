---
name: live-connector-artifact
description: >-
  Construir y publicar un Artifact de claude.ai que consulta EN VIVO un conector
  MCP del visor en tiempo de ejecución (capacidad `mcp` del runtime de Artifacts),
  en lugar de incrustar un volcado estático. Dispara cuando alguien pide una
  web / dashboard / hemeroteca / navegador / catálogo / panel sobre datos que
  viven en un conector (Gmail, Calendar, Drive, un MCP propio, etc.) y quiere que
  reflejen el estado ACTUAL cada vez que se abre la página — no una foto fija.
  Palabras gatillo: "que se actualice solo", "datos en vivo", "en tiempo real",
  "que lea de mi conector/MCP al abrir", "dashboard de <conector>". NO usar si
  los datos no están en un conector de claude.ai (solo MCP local sin puente, o
  una API con CORS/CSP cerrado): ahí la capacidad `mcp` no llega — incrustar un
  snapshot y decírselo al usuario.
---

# live-connector-artifact

Publica una página de Artifact que, **al abrirse en claude.ai**, llama a los
conectores MCP del visor con SUS credenciales y renderiza datos actuales. La
página no trae los datos dentro: los pide en cada apertura. Genérica y
parametrizada por conector — nunca incrustes nombres, tools ni datos de un
conector concreto en esta skill; usa placeholders (`<nombre exacto del
conector>`, `<tool_1>`, …).

## Cuándo aplica y cuándo no

Aplica cuando **los datos viven en un conector que el visor tiene añadido en
claude.ai** y la página debe reflejar su estado actual en cada apertura.

No aplica —y hay que incrustar un snapshot y decirlo— cuando:
- Los datos solo están en un MCP **local** sin puente `host:` en la superficie
  que abrirá la página (fuera de la app de Claude, `host:` siempre falla).
- La fuente es una API con CORS/CSP cerrado (el CSP del Artifact bloquea `fetch`
  a cualquier host; no hay forma de esquivarlo desde la página).
- El visor no tiene —ni tendrá— ese conector conectado.

La capacidad `mcp` **bloquea el compartir público**: un Artifact que la declara
queda *owner-only*. Dilo al entregar.

## Procedimiento

### 1. Verificar el conector en vivo — live gana sobre asunción
Ejecuta `ListConnectors` (o revisa las tools `mcp__<conector>__<tool>` de la
sesión). Captura:
- El **`name` EXACTO** del conector tal y como aparece en claude.ai. Es el valor
  literal que irá en `server`. Ojo a **espacios dobles** y a mayúsculas —
  `callTool` compara carácter a carácter y un solo espacio de más da
  `server_not_connected`. Los guiones bajos del prefijo de tool
  (`mcp__Google_Calendar__…`) se leen como espacios en el display name
  (`Google Calendar`).
- `connected: true`. Si no está conectado, no sigas: no podrás observar la forma
  real (paso 2) y estarías adivinando.

Para un MCP local del dispositivo, el `server` es `host:<nombre>` (solo dentro de
la app de Claude; el `<nombre>` con todo lo que no sea `[A-Za-z0-9_-]` a `_`).

### 2. Observar UNA petición/respuesta real por cada tool que usará la página
Llama de verdad, una vez, a cada tool que la página vaya a invocar y **aprende la
forma del `payload`** (nombres de campos, anidamiento, tipos). No adivines los
argumentos ni el encoding del resultado — el contrato define el sobre
(`result.payload`), no la forma interna de cada conector.

Dos reglas duras:
- **No incrustes los valores observados** en la página publicada: son datos
  reales del usuario. Aprendes la *forma*, no los *valores*.
- Si no puedes observar con seguridad (conector sin autenticar aquí, o la tool
  tiene efectos secundarios), **no publiques una forma adivinada**: díselo al
  usuario en tu respuesta al entregar.

### 3. Cargar el contrato de la capacidad `mcp`
Carga la skill `artifact-capabilities`. Confirma que `mcp` está en el roster del
usuario y **lee `claude.d.ts` + `mcp.d.ts` del contrato vigente** antes de
escribir una sola línea que llame a `mcp`. Esos tipos mandan sobre cualquier API
que recuerdes. De ahí salen, como mínimo:
- `const mcp = await claude.use("mcp")` → `null` si esta vista no puede
  ejecutar la capacidad (no servida, no concedida o módulo caído; indistinguibles
  por diseño). Resuelve **más tarde**, nunca en la primera ejecución síncrona de
  tu script, y `null` a los ~10 s si ningún visor responde.
- `callTool(server, tool, input?, opts?)` → `Promise<CallToolResult>`; lee
  `result.payload`. Una tool que falla **rechaza** con `code: "tool_error"`.
- `watchTool(server, tool, input, handler, opts?)` → `Unsubscribe` **síncrono**;
  eventos `{type:"data", result}` | `{type:"error", error}`. Solo lecturas.
- `result.cache?.storedAt` para la frescura (nunca `Date.now()`).

### 4. Construir la página autocontenida (carga `artifact-design`)
Carga `artifact-design` y aplica su criterio visual. Sobre esa base, el patrón de
runtime:

- **Esqueleto primero.** Renderiza la estructura y estados vacíos sin datos.
  Luego `const mcp = await claude.use("mcp"); if (!mcp) return renderSinConector();`
  — trata `null` como **estado de primera clase**: la página se ve y se explica
  sin conector, sin datos de relleno falsos. No leas `window.claude.mcp`: el
  único miembro prometido es `use`.
- **Lecturas que deben mantenerse frescas → `watchTool`.** Guarda el
  `Unsubscribe` ANTES de que pueda llegar el primer evento (llega en un
  microtask). Refresco periódico solo con `refetchInterval` (suelo ~30 s).
- **Acciones (o una carga puntual) → `callTool` una vez**, lee `result.payload`.
  Nunca `watchTool` para acciones; las tools con `readOnlyHint:false` lo rechazan.
- **Ramifica el UX de error por `McpError.code`, nunca por texto** ni con un único
  banner genérico. Cada código con arreglo propio necesita copy y acción
  distintos:
  - `needs_reauth` → "Reconecta <server> en claude.ai → Ajustes → Conectores".
  - `server_not_connected` → "Añade <server> en claude.ai → Ajustes → Conectores"
    (o, para `host:`, fallback "sin puente local").
  - `selection_required` → misma vista degradada que `server_not_connected`
    (el visor tiene varios conectores con ese nombre y no ha elegido).
  - `blocked_by_policy` / `approval_required` → estado "requiere aprobación",
    sin reintentar.
  - `tool_error` → muestra el mensaje reportado en la sección afectada; reintentar
    con los mismos args casi nunca ayuda.
  - `not_granted` / `capability_disabled` / `capability_removed` → experiencia
    sin-MCP (como `mcp === null`).
  - Un `default` con copy genérica está bien **solo** para los códigos que no
    tratas uno a uno; el anti-patrón es colapsar en ese banner los que sí tienen
    arreglo.
  - **Reintenta solo los `retryable: true`** (hoy `server_unavailable`, y
    `rate_limited` si llegara), **una sola vez** por refresco visible, tras un
    retardo corto aleatorizado, respetando `retryAfterMs`, y **solo lecturas**.
    Una escritura que rechaza con `server_unavailable` es ambigua (pudo ejecutarse):
    no la repitas sin un gesto nuevo del usuario.
- **DOM con `textContent`** para TODO lo que venga del conector — nunca `innerHTML`
  con datos del payload (evita inyección). Construye nodos, no plantillas de string.
- **Frescura visible**: si muestras "actualizado hace…", léelo de
  `result.cache.storedAt`, nunca de `Date.now()`.
- **Temas claro/oscuro por tokens** y contenido contenido en móvil (sin scroll
  horizontal del body; tablas/anchos con su propio `overflow-x:auto`).
- En dashboards multi-sección: **contén cada fallo en su sección**, mantén el
  último dato bueno con indicador de obsolescencia, y sube a condición de página
  solo cuando todas fallan con el mismo código.

### 5. Verificar con un arnés Playwright que SIMULA el conector
Archivo de prueba **aparte** — nunca el que se publica. El arnés inyecta un
`window.claude` mock (vía `addInitScript`, antes de que cargue la página) cuyo
`use("mcp")` devuelve un mock de `mcp`; su `callTool`/`watchTool` resuelven
`payload`s **con la forma observada en el paso 2** (forma, no valores reales).
Comprueba:
- Índice / detalle / búsqueda renderizan con datos.
- La rama `mcp === null` (mock que devuelve `null`) se ve y se explica.
- Al menos un código de error produce su copy y acción propias.
- Capturas en **claro + oscuro + móvil**.
- **Cero `pageerror`** (aserción dura).

Ver `verify.example.mjs` en esta carpeta como plantilla del arnés + mock.

### 6. Publicar con la herramienta Artifact
```
capabilities: { mcp: { servers: [ { server: '<nombre exacto>', tools: ['<tool_1>', '<tool_2>'] } ] } }
```
- Cada `servers[]` necesita `tools` **no vacío** (una lista vacía se rechaza y
  NO significa "todas"). Manifiesto mínimo: solo los tools que la página llama.
- El `server` debe coincidir **carácter a carácter** con el `name` de
  `ListConnectors` (paso 1).
- Al entregar, di explícitamente que la capacidad `mcp` deja el Artifact
  **owner-only** (no compartible en público).

## Checklist de verificación (antes de dar por hecho)

- [ ] La página se renderiza **sin conector** (rama `mcp === null`), con sentido.
- [ ] Cada `McpErrorCode` que tratas tiene **copy y acción distintas**; el resto
      cae en un `default` honesto.
- [ ] **Ningún valor observado** incrustado como muestra/placeholder.
- [ ] Todo dato del conector va al DOM por `textContent`.
- [ ] Solo se reintentan errores `retryable`, una vez, y solo lecturas.
- [ ] Frescura desde `result.cache.storedAt`, no `Date.now()`.
- [ ] Capturas limpias en **claro + oscuro + móvil**, con **cero `pageerror`**.
- [ ] El `server` del manifiesto coincide carácter a carácter con `ListConnectors`
      (¡espacios dobles!), y cada `servers[].tools` es no vacío.
- [ ] Entregado avisando de que `mcp` bloquea el compartir público (owner-only).

## Anti-patrones

- Incrustar un volcado estático y llamarlo "en vivo".
- Un único banner "error de conector" para todos los códigos.
- Leer `window.claude.mcp` en vez de `await claude.use("mcp")`.
- Reintentar `needs_reauth` / `server_not_connected` en bucle (nunca succederá solo).
- Publicar una forma de `payload` adivinada sin haber observado una respuesta real.
- Meter el arnés de test o el mock de `window.claude` en la página publicada.
