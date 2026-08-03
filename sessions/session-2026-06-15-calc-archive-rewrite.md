# Session Archive — 2026-06-15 · calc-archive-rewrite

**Date**: Monday, 15 June 2026  
**Session**: calc-archive-rewrite  
**Session ID**: b5c3615a-b89d-492a-889b-fdc565c3b18c  
**Turns**: 48 (8 user · 40 assistant)  
**Project**: lyai-ski  

---

### **You** `13:01`

¡buenos dias Claude!

mira la captura, la barrita horizontal que pusimos para poder tirar del desplegable hacia abajo no es clickeable

---

### **Claude** `13:01`

¡Buenos días Ignacio! Recibido — la barrita (grabber) del calc no responde al arrastre para bajar el desplegable. Es un **bug de interacción** (el grabber existe pero no captura el gesto). Investigo cómo está montado el swipe-down + el grabber:

---

### **Claude** `13:01`

El PanResponder vive en map.tsx (72-78) y se pasa como `sheetDragHandlers` (map.tsx:989). El grabber se pinta en RouteCalcInner:506. Veo si los `sheetDragHandlers` están realmente **enganchados** al grabber:

---

### **Claude** `13:02`

Los `sheetDragHandlers` SÍ están en el contenedor del grabber (504). Así que el problema está en el PanResponder o en cómo se aplica el transform. Leo el PanResponder + cómo se monta el sheet animado en map.tsx:

---

### **Claude** `13:02`

PanResponder correcto. Veo el render del Modal/sheet (cómo se aplica `calcTranslateY` + dónde van los handlers):

---

### **Claude** `13:04`

El cableado es correcto (PanResponder bien creado, transform aplicado, handlers en el grabber). El problema es típico de **RN-Web**: el PanResponder solo tiene `onMoveShouldSetPanResponder` → con ratón (viewer web) el responder no se reclama al pulsar, y la zona de arrastre es muy fina (~19px). Verifico que los archivos estén libres y te propongo el fix:

---

### **Claude** `13:04`

Diagnóstico confirmado, ambos archivos libres y sin lock. 

## Causa
El grabber no arrastra en **web (viewer)** por dos cosas:
1. El PanResponder solo reclama el gesto en `onMoveShouldSetPanResponder` ([map.tsx:76](frontend/app/map.tsx#L76)) — con **ratón**, RN-Web no lo agarra bien si no se reclama al **pulsar**.
2. La zona de arrastre es una franja finísima (~19px) → difícil de agarrar.

## Propuesta del diff (espero "aplica")

**1. [map.tsx:75-86](frontend/app/map.tsx#L75)** — añadir `onStartShouldSetPanResponder: () => true` al PanResponder (reclama el gesto al pulsar → arrastre con ratón funciona; un tap sin mover = no-op, vuelve arriba).

**2. [RouteCalcInner.tsx:504-510](frontend/src/components/RouteCalcInner.tsx#L504)** — mover los `sheetDragHandlers` del contenedor entero a una **zona de arrastre dedicada y más grande** (centrada, ~120×21px, con la barrita dentro), y dejar el botón **×** **fuera** de esa zona (para que su tap siga cerrando, no lo intercepte el pan). La barrita visible sigue igual (40×5, turquesa, latiendo).

**Efectos colaterales:** ninguno — el botón × se separa del pan (sigue funcionando), zona de agarre mayor, arrastre OK en web y móvil. La apariencia no cambia.

**dev-xplain: skip · sin cambio visual de diseño** — es un fix de interacción (arrastre), el grabber se ve idéntico.

¿**aplica**?

---

### **You** `13:15`

aplica

---

### **Claude** `13:15`

Aplico. Edit 1 — PanResponder reclama al pulsar:

---

### **Claude** `13:15`

Edit 2 — grabber: zona de arrastre dedicada y mayor, botón × separado:

---

### **Claude** `13:16`

`RouteCalcInner.tsx` cambió desde que lo leí. Releo la zona del grabber + verifico que no haya otra sesión editándolo:

---

### **Claude** `13:16`

Limpio, grabber igual. Releo el bloque exacto para editar:

---

### **Claude** `13:16`

Build + deploy + commit scoped (`map.tsx` + `RouteCalcInner.tsx`):

---

### **Claude** `13:16`

Build OK (y `route_calc.py` ya lo commiteó la otra sesión). Deploy + commit scoped:

---

### **Claude** `13:17`

✅ **Live y committeado** (`e3d2827`, entry `d223119`):

La barrita del calc ahora **se puede arrastrar hacia abajo** para plegar el sheet:
- El PanResponder reclama el gesto al **pulsar** (no solo al mover) → funciona con ratón en el viewer web.
- **Zona de agarre amplia** (~120×21px alrededor de la barrita) con `cursor: grab` en web — fácil de agarrar.
- El botón **×** queda separado de la zona de arrastre → su tap sigue cerrando normal.

**Verifica en viewer** (Ctrl+Shift+R): abre el calc → agarra la barrita turquesa y **arrástrala hacia abajo** → el sheet baja y se pliega (si sueltas a medias, vuelve arriba). Soltar pasado ~110px o con velocidad lo cierra.

¿Lo pruebas? Si en el móvil real también fallaba, este fix cubre ambos (touch + ratón).

---

### **You** `13:18`

mira la captura. cuando obtenemos la ruta, hemos de hacer scroll hacia abajo, por tanto dejamos de ver el origen y destino seleccionados. no obstante lo podemos volver a mostrar al lado de la distancia y encima del mapa, en la posicion en la que te indico en la segunda captura.

---

### **Claude** `13:18`

Recibido: tras calcular, al hacer scroll se pierde el origen/destino seleccionados → quieres mostrarlos de nuevo **junto a la distancia (33.8 min), encima del mapa** (el recuadro verde de la 2ª captura). Es cambio visual → mockup HTML primero. Leo el render del resultado para ubicarlo y ver los datos disponibles:

---

### **Claude** `13:19`

El header del resultado: "33.8 min" (885) + meta (886-889) + mapa. Quieres el origen→destino en el hueco a la derecha del tiempo. Datos disponibles: `origin3.label` / `dest3.label`. Monto el mockup. Hora:

---

### **Claude** `13:20`

✅ **dev-xplain live:**
**https://dev.lyai.pro/dev-xplain/2026-06-15-1319-calc-route-summary-origen-destino/**

BEFORE (hueco vacío a la derecha del tiempo) → AFTER (origen 📍 azul + destino 🏁 rojo, compactos, con su estación, en ese hueco).

### Propuesta del diff (espero "aplica")

**`RouteCalcInner.tsx` — header del resultado ([:885-889](frontend/src/components/RouteCalcInner.tsx#L885)):**
- Envolver el **tiempo + meta** en una columna izquierda y añadir a la **derecha** un resumen compacto **origen→destino**, en una fila `space-between`:
  - 📍 (azul) `origin3.label` + estación derivada (`sectorName(origin3.stationId)`) debajo.
  - 🏁 (rojo) `dest3.label` + su estación debajo.
  - Cada nombre a 1 línea (truncado), `maxWidth ~150`.
- Datos ya disponibles: `origin3`/`dest3` (state) + el helper `sectorName` que ya existe en el componente. Sin tocar backend ni datos.
- Acorto el meta a "… · 6 aristas" (sin "ski/lift") para que quepa la fila.

**Efectos colaterales:** ninguno — es display aditivo del estado ya seleccionado; mapa y lista ROUTE PRO sin cambios. Si no hay origen/destino (no debería tras calcular), simplemente no se muestra.

¿**aplica**?

---

### **You** `13:21`

mira la capura, este tramo que te muestro dentro de el circulo es un tramo en linea gris discontinua imposible de apreciar.

la segunda captura muestra la linea recta que no es correcta, como ya vimos anteriormente.

---

### **Claude** `13:21`

Cambio de tema (ojo: el route-summary anterior quedó **sin tu "aplica"** — lo retomo al final). Dos problemas del trazo en el mapa:
1. Un tramo en **gris discontinuo casi invisible** (el del círculo).
2. La **línea recta incorrecta** (el problema conocido de los transfers rectos).

Investigo cómo dibuja `RouteMap3D` los segmentos (estilo gris/dash + geometría recta):

---

### **Claude** `13:22`

Veo la causa de ambos en `RouteMap3D` ([:16-17, :53](frontend/src/components/RouteMap3D.tsx#L53)):
- **Issue 1**: el segmento **walk** se dibuja gris `#94A3B8`, dash fino, **sin casing blanco** ([:53](frontend/src/components/RouteMap3D.tsx#L53)) → invisible sobre satélite.
- **Issue 2**: si un segmento **no trae `edge_geom`** real, se dibuja **recta** entre nodos ([:17](frontend/src/components/RouteMap3D.tsx#L17)) — el problema conocido.

Reproduzco la ruta de tu captura (Châtel→Morgins) para ver **qué segmento es la recta** (modo + si tiene geom):

---

### **Claude** `13:24`

Reproducción reveladora. Diagnóstico **preciso** de los dos:

- **Issue 1 (gris discontinuo invisible):** son segmentos **walk** (conectores de snap). Se dibujan gris `#94A3B8`, dash fino y **sin casing blanco** → invisibles sobre satélite.
- **Issue 2 (recta incorrecta):** es **`ski` con `source_type='transfer'` "Morgins-Foilleuse" · geom=0** → es un **transfer fantasma** (enlace Châtel↔Morgins sin geometría real) dibujado como recta y con color de pista. Es el gap de liaison conocido (Châtel/Super-Châtel↔Morgins, el L6 que quedó pendiente). **No se arregla con estilo — necesita geometría real de liaison.**

Monto el dev-xplain del trazo (issue 1 + cómo se vería el transfer honesto). Hora:

---

### **Claude** `13:24`

Perfecto — gracias por el puntero. Reutilizo el diseño que ya validamos en ese dev-xplain (paleta difColor + casing blanco). El walk debe llevar el **mismo tratamiento de casing blanco** que ski/lift/navette (por eso es invisible: es el único sin casing). Leo tu dev-xplain anterior para mantener el mismo estilo y ser consistente:

---

### **Claude** `13:24`

Tengo el estilo exacto de tu dev-xplain anterior (casing blanco + núcleo de color, SVG, phone-frame). Lo extiendo en el **mismo estilo**: el walk debe llevar **casing blanco** como ski/lift/navette (es el único sin él → por eso es invisible). Monto el dev-xplain consistente (hora 13:24):

---

### **Claude** `13:26`

✅ **dev-xplain live** (mismo estilo que el tuyo de 2026-06-12):
**https://dev.lyai.pro/dev-xplain/2026-06-15-1324-route3d-walk-visible-transfer/**

Leo el builder del GeoJSON para proponer el diff exacto:

---

### **Claude** `13:26`

Diagnóstico y mockup listos. Aquí el diff propuesto sobre `RouteMap3D.tsx · SETUP_JS`, consistente con tu diseño de casing:

### Issue 1 — walk visible (estilo · lo arreglo ya)
**BEFORE** [:53](frontend/src/components/RouteMap3D.tsx#L53): `walk` = `#94A3B8`, width 3, dash [1,1.6], **sin casing** → invisible.
**AFTER**:
- Nueva capa `walk-cas` (casing blanco, width 6) **antes** del walk — mismo patrón que ski/lift/navette.
- `walk` → color `#64748B` (más sólido), width 4, dash [2,2.4] (más grueso).

### Issue 2 — transfer recto (NO es estilo; mitigación honesta opcional)
El edge `source_type='transfer'` (sin `edge_geom`) se pinta como **pista azul recta** ([builder :18](frontend/src/components/RouteMap3D.tsx#L18) le da `kind='ski'`). 
- **Mitigación (opcional):** en el builder, `source_type==='transfer' && !real` → `kind='transfer'`; nueva capa `transfer` en **ámbar dash + casing** → se lee como "enlace aproximado", no como pista precisa. **No lo hace correcto**, solo honesto.
- **Arreglo real (deep, aparte):** geometría de liaison Châtel↔Morgins (como L6/navette · trabajo de datos).

**Efectos colaterales:** ninguno — solo capas/estilos del SETUP_JS; el desglose y la lógica no cambian.

¿**aplica** Issue 1 solo, o **1 + mitigación 2**? (El arreglo real de la recta lo dejamos como tarea de datos.)

PD: quedó pendiente tu "aplica" del **route-summary** (origen→destino junto a la distancia) de antes — ¿lo retomo después?

---

### **You** `13:41`

Claude vamos a empezar el calculador de ruta desde cero, guarda el calculador de ruta con lo que tenemos hasta hoy en un directorio aparte en el servidor, sacalo de produccion porque vamos a empezar de cero. Asumimos que dentro de la Seccion Carte, el calculador está en proceso de fabricacion, por tanto dame el brief/prompt para una sesion nueva donde solo y exclusivamente vamos a crear un calculador de ruta desde cero basandonos en la unica informacion oficial que tenemos, que es el mapa interactivo, que por cierto nosotros ofrecemos como mapa "invierno" en carte. la url es la siguiente:  https://www.portesdusoleil.com/en-hiver/plan-des-pistes/

que lo unico que vamos a seguir utilizando es el mapa 3D que utilizamos actualmente.
el procedimiento va a ser el siguiente, yo voy a ir haciendo zoom y filtrando por remontes en el mapa interactivo, paso las capturas y vamos creando estancion por estacion, una a una, los datos oficiales que vamos a usar en nuestro calculador, por tanto me imagino los datos y tablas que estamos usando hasta ahora provenientes de la base de datos postgres, de momento no los vamos a usar y empezamos de cero, si tienes alguna duda, preguntame. este trabajo en la nueva sesion.

---

### **Claude** `13:43`

Gran pivote, y tiene mucho sentido — el calc actual arrastra datos OSM inflados (×3.7), transfers rectos fantasma, contaminación non-PdS y fragmentación. Empezar de cero con la fuente **oficial** (el mapa interactivo PdS) es lo correcto.

Antes de ejecutar (archivar + sacar de prod) tengo **dudas reales** que afectan cómo lo hago. Primero escribo el brief (es independiente de las dudas), luego te pregunto lo crítico.

---

### **Claude** `13:44`

Brief escrito → [docs/briefs/brief-route-calc-from-scratch-2026-06-15.md](docs/briefs/brief-route-calc-from-scratch-2026-06-15.md). Ahora las dudas que necesito para ejecutar bien el archivado/salida-de-prod y para arrancar la sesión nueva:

---

### **Claude** `13:49`

Recibido, todo claro:
- **Out-of-prod**: NO tocamos la gema ni la UI — solo **archivamos el código actual** (queda congelado como v1) y la sesión nueva lo recodifica desde cero. El app sigue funcionando mientras tanto.
- **Archivado**: **Todo** (código + dump BD + tools + docs).
- **Geo-referencia**: investigar Intermaps (tarea de arranque de la sesión nueva — lo dejo anotado en el brief).

Ejecuto el archivado (no destructivo: copias + dump + tag git). Primero recon de dónde puedo escribir + pg_dump vía container:

---

### **Claude** `13:50`

`/opt/lyai/archive` necesita sudo (lo creo) y **pg_dump funciona en `lyai_postgres`**. Ejecuto el archivado completo (código + tools + docs + dump BD + tag git):

---

### **Claude** `13:50`

Archivo completo ✅:
- **frontend** 6 · **backend** 3 · **tools** 2 dirs · **docs** 5 · **db** 5 dumps (routing_edges 7.6M, route_nodes 540K, pistes, remontes, pistas_canonicas).
- **git tag** `route-calc-v1-2026-06-15` → `c151e6c` (snapshot exacto en historial).

Escribo el README del archivo (qué hay + cómo restaurar) y luego te paso el brief aquí para copiar:

---

### **Claude** `13:51`

Archivo cerrado (README incluido). Aquí tienes el **brief listo para copiar/pegar** como primer mensaje de la sesión nueva:

---

```
Vamos a construir el CALCULADOR DE RUTA de lyai-ski DESDE CERO, en una sesión dedicada
exclusivamente a esto. El calc anterior queda archivado y congelado (NO reabrirlo ni
parchearlo). Brief canónico: docs/briefs/brief-route-calc-from-scratch-2026-06-15.md
Archivo del v1: /opt/lyai/archive/route-calc-v1-2026-06-15/ (código+BD+tools+docs · git tag route-calc-v1-2026-06-15).

OBJETIVO
Un calc de ruta nuevo, alimentado SOLO por la fuente oficial: el mapa interactivo de
Portes du Soleil (invierno) — https://www.portesdusoleil.com/en-hiver/plan-des-pistes/ —
el mismo widget Intermaps que la app ofrece como mapa "invierno" en Carte.

NO USAR (archivado, intacto, frágil): las tablas Postgres del calc viejo (routing_edges,
route_nodes, pistes, remontes, pistas_canonicas) ni los datos OSM. Empezamos de cero.
Razones del descarte: OSM inflado ×3.7, pistes sin nombre/fragmentadas, transfers fantasma
rectos, grafo en ~50 componentes (staleness). Ver memorias project_route_graph_fragmentation_2026-06-14
y project_route_graph_staleness_and_stale_build_sql_2026-06-14.

SE REUTILIZA SOLO
- El mapa 3D: frontend/src/components/RouteMap3D.tsx (RouteMapSwitch, MapLibre satélite+terreno) para el trazo.
- El lenguaje visual del trazo ya validado: paleta difColor (verde #719D7C / azul #3C6EA1 /
  roja #CC4B37 / negra #0A0A0A · lift/navette azul) + casing blanco + walk con casing
  (dev-xplains 2026-06-12-2130-route3d-trace-legend-colors y 2026-06-15-1324-route3d-walk-visible-transfer).
- La gema/entrada en Carte se queda como está (no se toca la UI). v2 reemplaza al calc viejo cuando esté listo.

PROCEDIMIENTO (humano-en-el-loop · estación por estación)
Ignacio hace zoom y filtra por REMONTES en el mapa oficial y manda capturas. Por estación
se extrae, validado por él: remontes (nombre, tipo, base→cima), pistas (nombre, dificultad/color,
de qué cima salen y a qué base/cruce llegan), y conexiones (topología real). Se construye un
grafo oficial LIMPIO (nodos base/cima/cruce + aristas pista/remonte). UNA estación a la vez,
validar y dibujar en el 3D antes de seguir. Enlaces inter-estación = explícitos (pista esquiable
o navette de navettes.json) con geometría real — NUNCA una recta fantasma.

PRIMERA TAREA (crítica, define todo)
Investigar si el mapa Intermaps oficial expone features/geojson/tiles con coords y geometría
reales de remontes y pistas (decisión de Ignacio: "investigar Intermaps"). Sin coords no hay
trazo 3D. Luego: acordar modelo de datos fresco (JSON por estación backend/data/calc2/<station>.json
o tablas nuevas lyai.calc2_*) y empezar por 1 estación piloto.

MOTOR
Grafo dirigido (pista=descenso filtrable por dificultad/skill + remonte=subida) + Dijkstra
multi-criterio (tiempo/fácil/escénica). Se puede reusar la LÓGICA de scoring del route_calc.py
archivado, pero alimentada solo por el grafo oficial limpio. Sin transfers fantasma.

REGLAS (no negociables)
- dev-xplain = MOCKUP HTML (Tailwind+Lucide+Inter, phone-frame, BEFORE/AFTER) antes de cada
  cambio visual. (La norma "usar app real/iframe" fue revertida el 2026-06-14.)
- Coordinación multi-sesión: leer COORDINACION.md · 1 sesión edita a la vez · NUNCA git add -A · build+deploy en serie.
- Gating: "aplica" (reversible) / "EJECUTA" (destructivo). Proponer antes de aplicar.
- NO tocar las tablas viejas (archivadas).
- Build/deploy: cd frontend && npm run build:web && sudo cp -r dist/. /var/www/dev.lyai.pro/app/ · verificar entry-*.js.

Empieza leyendo el brief canónico y CLAUDE.md (TIER 2), confirma el plan, y pregúntame
cualquier duda antes de tocar código.
```

---

**Estado tras esta sesión:**
- v1 **archivado** en `/opt/lyai/archive/route-calc-v1-2026-06-15/` + tag `route-calc-v1-2026-06-15` (`c151e6c`).
- App **sin cambios** (gema y calc viejo siguen funcionando hasta que v2 los reemplace).
- Brief en repo + el bloque de arriba para arrancar.

¿Quieres que deje algo más preparado (p.ej. una rama `route-calc-v2` para la sesión nueva), o lo dejamos aquí?

---

### **You** `14:06`

tengo dudas de si el route-calc.py lo podemos reutilizar. guardalo y empezamos de cero

---

### **Claude** `14:06`

route_calc.py ya quedó **guardado** (en el archivo `/opt/lyai/archive/route-calc-v1-2026-06-15/backend/route_calc.py` + tag `route-calc-v1-2026-06-15`). Recibido: el **motor también desde cero** — no asumimos reutilizar route_calc.py. Corrijo el brief para quitar esa suposición:

---

### **Claude** `14:07`

Brief actualizado. Aquí el **bloque corregido para copiar/pegar** (cambia solo el MOTOR — todo lo demás igual):

---

```
Vamos a construir el CALCULADOR DE RUTA de lyai-ski DESDE CERO, en una sesión dedicada
exclusivamente a esto. El calc anterior queda archivado y congelado (NO reabrirlo ni
parchearlo). Brief canónico: docs/briefs/brief-route-calc-from-scratch-2026-06-15.md
Archivo del v1: /opt/lyai/archive/route-calc-v1-2026-06-15/ (código+BD+tools+docs · git tag route-calc-v1-2026-06-15).

OBJETIVO
Un calc de ruta nuevo, alimentado SOLO por la fuente oficial: el mapa interactivo de
Portes du Soleil (invierno) — https://www.portesdusoleil.com/en-hiver/plan-des-pistes/ —
el mismo widget Intermaps que la app ofrece como mapa "invierno" en Carte.

NO USAR (archivado, intacto, frágil): las tablas Postgres del calc viejo (routing_edges,
route_nodes, pistes, remontes, pistas_canonicas) ni los datos OSM. Empezamos de cero.
Razones del descarte: OSM inflado ×3.7, pistes sin nombre/fragmentadas, transfers fantasma
rectos, grafo en ~50 componentes (staleness). Ver memorias project_route_graph_fragmentation_2026-06-14
y project_route_graph_staleness_and_stale_build_sql_2026-06-14.

SE REUTILIZA SOLO
- El mapa 3D: frontend/src/components/RouteMap3D.tsx (RouteMapSwitch, MapLibre satélite+terreno) para el trazo.
- El lenguaje visual del trazo ya validado: paleta difColor (verde #719D7C / azul #3C6EA1 /
  roja #CC4B37 / negra #0A0A0A · lift/navette azul) + casing blanco + walk con casing
  (dev-xplains 2026-06-12-2130-route3d-trace-legend-colors y 2026-06-15-1324-route3d-walk-visible-transfer).
- La gema/entrada en Carte se queda como está (no se toca la UI). v2 reemplaza al calc viejo cuando esté listo.

PROCEDIMIENTO (humano-en-el-loop · estación por estación)
Ignacio hace zoom y filtra por REMONTES en el mapa oficial y manda capturas. Por estación
se extrae, validado por él: remontes (nombre, tipo, base→cima), pistas (nombre, dificultad/color,
de qué cima salen y a qué base/cruce llegan), y conexiones (topología real). Se construye un
grafo oficial LIMPIO (nodos base/cima/cruce + aristas pista/remonte). UNA estación a la vez,
validar y dibujar en el 3D antes de seguir. Enlaces inter-estación = explícitos (pista esquiable
o navette de navettes.json) con geometría real — NUNCA una recta fantasma.

PRIMERA TAREA (crítica, define todo)
Investigar si el mapa Intermaps oficial expone features/geojson/tiles con coords y geometría
reales de remontes y pistas (decisión de Ignacio: "investigar Intermaps"). Sin coords no hay
trazo 3D. Luego: acordar modelo de datos fresco (JSON por estación backend/data/calc2/<station>.json
o tablas nuevas lyai.calc2_*) y empezar por 1 estación piloto.

MOTOR (también desde cero)
Grafo dirigido (pista=descenso filtrable por dificultad/skill + remonte=subida) + Dijkstra
multi-criterio (tiempo/fácil/escénica) = CÓDIGO NUEVO. NO se asume reutilizar route_calc.py
(queda archivado solo como referencia; si alguna pieza concreta resulta útil se evalúa entonces).
Sin transfers fantasma: inter-sector = aristas reales con geometría.

REGLAS (no negociables)
- dev-xplain = MOCKUP HTML (Tailwind+Lucide+Inter, phone-frame, BEFORE/AFTER) antes de cada
  cambio visual. (La norma "usar app real/iframe" fue revertida el 2026-06-14.)
- Coordinación multi-sesión: leer COORDINACION.md · 1 sesión edita a la vez · NUNCA git add -A · build+deploy en serie.
- Gating: "aplica" (reversible) / "EJECUTA" (destructivo). Proponer antes de aplicar.
- NO tocar las tablas viejas (archivadas).
- Build/deploy: cd frontend && npm run build:web && sudo cp -r dist/. /var/www/dev.lyai.pro/app/ · verificar entry-*.js.

Empieza leyendo el brief canónico y CLAUDE.md (TIER 2), confirma el plan, y pregúntame
cualquier duda antes de tocar código.
```

---

route_calc.py está a salvo (archivo + tag), el brief ya refleja "motor desde cero, sin asumir su reutilización". Todo listo para arrancar la sesión nueva. ¿Algo más antes de cerrar esta?

---

### **You** `14:10`

cerramos sesion

---

### **Claude** `14:10`

Cerramos. Uso el protocolo canónico de cierre del server:

---

### **You** `14:10`

You are now executing the **session closure protocol** for a Claude Code CLI instance running on the lyai-prod server.

Reference: `/home/lyai/.claude/RULES-SESSIONS-SERVER.md`

## Step 1 · Analyze the conversation

Review the entire conversation history of this session. Identify:

1. **Lessons** — non-obvious gotchas, bugs solved that took more than one attempt, sysadmin tricks
2. **Decisions** — architectural choices where you compared options and picked one, with stated reasons
3. **Protocols** — reproducible sequences of commands for tasks that may repeat
4. **User feedback** — rules / preferences / corrections the user gave you (especially "no haces X", "prefiero Y", "siempre Z")
5. **Project facts** — deadlines, scope decisions, ownership / who-does-what info not in CLAUDE.md
6. **References** — pointers to external systems (URLs, Linear projects, Grafana dashboards, etc.) the user mentioned

Skip anything trivial (typo fixes, cosmetic adjustments, single-line edits without conceptual content).

## Step 2 · Persist to each layer

### 2.1 Wiki (`/opt/lyai/wiki/pages/`)

For each lesson / decision / protocol identified, create the appropriate file:

```bash
# Lesson example
LESSON_PATH="/opt/lyai/wiki/pages/lessons/lesson-$(date +%Y-%m-%d)-<short-slug>.md"
```

File format:
```markdown
# Título corto

**Fecha**: YYYY-MM-DD
**Contexto**: 1-2 líneas del problema/situación
**Hallazgo/Decisión**: lo concreto
**Detalle técnico**: paths, comandos, queries, line refs
**Implicaciones**: qué cambia para futuro
**Origen**: tarea / commit / agent que lo descubrió
```

**Index update mandatory**: append one line to `/opt/lyai/wiki/pages/INDEX.md`:
```
- [Title](lessons/lesson-YYYY-MM-DD-slug.md) — one-line hook
```

### 2.2 Project memory (`~/.claude/projects/<project-slug>/memory/`)

For each user feedback / project fact / reference identified, create a memory file. Determine the project slug from `pwd` — Claude Code derives it as `-` + path with `/` replaced by `-`. For lyai-ski it's `-opt-lyai-app-lyai-ski`.

```bash
MEM_DIR="/home/lyai/.claude/projects/$(pwd | sed 's|/|-|g')/memory"
```

File format (frontmatter mandatory):
```markdown
---
name: Título corto
description: one-line para que futuras instancias decidan relevancia
type: feedback|project|reference|user
---

Contenido conciso.

**Why:** razón histórica
**How to apply:** cuándo aplicar la regla
```

**Index update mandatory**: append to `${MEM_DIR}/MEMORY.md`:
```
- [Title](file.md) — one-line hook
```

### 2.3 Aurelius channel (`/opt/lyai/app/channels/Aurelius.jsonl`)

If the work touched **security, architecture, an invariant that Aurelius must monitor**, or generated an `audit_request`-worthy event:

```bash
cat >> /opt/lyai/app/channels/Aurelius.jsonl <<EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","from":"<claude-instance-id>","to":"aurelius","msg_type":"audit_request|info|alert","subject":"…","content":"…","flag_id":"<TAG>","priority":"low|high"}
EOF
```

Skip if the session was routine UI/code work without security/arch implications.

### 2.4 Mirror Protocol — capítulo de la sesión (CADA cierre)

Generate the session's Mirror Protocol episode (Claude ↔ Aurelius dialogue) and inject it into lyai.online:

```bash
cd /opt/lyai/app/lyai.online && ./generate-daily-episode.sh $(date +%Y-%m-%d)
```

- Text only — Gemini 2.5-flash (free tier). **Do NOT** run `make-episode-audio.py` / `make-episode-video.py` (TTS/video = cost, separate, explicit order only).
- No server access (claude.ai web) → register intent in the Aurelius channel for server/builder to materialize.

## Step 3 · Constraints (HARD)

- ❌ Do NOT write to `/tmp/` (gets wiped on reboot)
- ❌ Do NOT auto-commit to wiki git repo — only write files; Ignacio commits manually
- ❌ Do NOT duplicate content already in CLAUDE.md / RULES-*.md TIER 1
- ❌ Do NOT escribir reflexiones/notas en Postgres (use wiki/memory)
- ❌ Do NOT modify existing memory files just to "update timestamp" — only edit if content changes
- ❌ Do NOT write trivial lessons (typo fixes, single-line cosmetic adjustments)

## Step 4 · Print final report (≤200 words)

Format:
```
═══════════════════════════════════════════
SESSION CLOSURE · {hostname} · {ISO timestamp}
═══════════════════════════════════════════

CODE CHANGES
- file:line — brief description
- ...

PERSISTED
- Wiki: /opt/lyai/wiki/pages/lessons/lesson-...md (+1 INDEX entry)
- Memory: ~/.claude/projects/<slug>/memory/<file>.md (+1 MEMORY entry)
- Aurelius: 1 msg appended (flag_id=X) | none
- DB: <N rows in lyai.X> | none

OPEN QUESTIONS
- ...

VALIDATION COMMANDS
- curl ... | grep "..."
- docker exec ... psql -c "..."
═══════════════════════════════════════════
```

## Step 5 · DO NOT exit

After printing the report, **stop** and wait for the user. Don't take further actions.

---

### **Claude** `14:11`

Ejecuto el cierre. Analizo la sesión y persisto en cada capa. Primero las memorias de proyecto (calc rewrite + dev-xplain + LAL):

---

### **Claude** `14:12`

Wiki lessons (gotchas no obvios):

---

### **Claude** `14:13`

Actualizo índices (wiki INDEX + MEMORY.md). Leo el final del INDEX wiki:

---

### **Claude** `14:13`

Añado las 3 lessons al INDEX wiki:

---

### **Claude** `14:15`

Añado las 3 memorias al índice MEMORY.md (sección nueva 2026-06-15). Leo la cabecera:

---

### **Claude** `14:17`

MEMORY.md cambió (sesión paralela escribiendo). Releo y reintento:

---

### **Claude** `14:18`

La sesión v2 **ya arrancó** y resolvió Intermaps (feed `/portes_du_soleil/data`). Añado mis 3 punteros bajo la sección de hoy:

---

### **Claude** `14:18`

Mensaje al canal Aurelius (decisión de arquitectura + preservación de datos):

---

