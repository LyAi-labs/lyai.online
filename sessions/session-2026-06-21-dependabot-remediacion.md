# Session Archive — 2026-06-21 · dependabot-remediacion

**Date**: Sunday, 21 June 2026  
**Session**: dependabot-remediacion  
**Session ID**: 89132b20-e1c7-4cc7-944d-85f79624b31b  
**Turns**: 7 (3 user · 4 assistant)  
**Project**: lyai-ski  

---

### **You** `12:17`

Continue from where you left off.

---

### **Claude** `12:17`

No response requested.

---

### **You** `16:08`

Pendiente solo accepted risk: starlette (bloqueado upstream) + 7 npm build-only.

explicame bien estas vulv, que implican no resolverlas, y que implica no resolverlas

---

### **Claude** `16:09`

Te lo explico una por una: **qué es**, **cómo se explotaría**, **nuestra exposición real** y **qué implica dejarla sin resolver**. (Solo explicación, no toco nada.)

---

## A) starlette 0.49.1 — 4 advisories, bloqueadas upstream

**Por qué no se pueden arreglar:** `starlette` está pineado por DOS dependencias que exigen `<1.0.0`: `fastapi 0.130.0` y `prometheus-fastapi-instrumentator 7.1.0`. El fix de todas vive en `starlette ≥1.1.0/1.3.1`. Bumpear starlette solo = rompería fastapi y el instrumentator. Solución real = subir los **tres a la vez** cuando el instrumentator publique soporte starlette 1.x (hoy no existe).

### 1. GHSA-82w8 · HIGH · DoS de form urlencoded
- **Qué es:** `request.form()` acepta límites (`max_fields`) para no parsear cuerpos abusivos. Starlette los aplica a `multipart/form-data` pero **los ignora en `application/x-www-form-urlencoded`**. Un atacante manda un cuerpo urlencoded con millones de campos (`a=1&a=1&…`) → la CPU se dispara parseándolos.
- **Exposición:** real, en `/api/dev-feedback` (usa `request.form()`).
- **Estado:** **MITIGADA** — el guard que metí (commit `8cda0cf`) rechaza con 413 los cuerpos urlencoded >64KB *antes* de parsear → acota el nº de campos. Verificado (70KB→413). El riesgo práctico queda neutralizado aunque la alerta siga "abierta".
- **Dejarla sin "resolver" (bump):** ninguna consecuencia real mientras el guard esté; cuando suba starlette 1.3.1 se puede quitar el guard.

### 2. GHSA-wqp7 · HIGH · SSRF/robo NTLM vía UNC en StaticFiles
- **Qué es:** servir ficheros con `StaticFiles` en **Windows** permite que una ruta `\\host\share` (UNC) haga que el servidor se conecte a un SMB remoto → SSRF + filtración de credenciales NTLM.
- **Exposición:** **N/A**. Usamos `StaticFiles` (`/api/uploads`), pero el vector UNC es **exclusivo de Windows** y corremos **Linux**. No explotable.
- **Dejarla sin resolver:** cero impacto. Es un falso "high" para nuestro entorno.

### 3. GHSA-86qp (MED) + PYSEC-2026-161 · path-poisoning vía Host header
- **Qué es:** starlette reconstruye `request.url.path` usando el header `Host` sin validar. Si la app usa ese `path` para decisiones de seguridad/auth, se puede falsear para saltarse chequeos por ruta.
- **Exposición:** **no expuesta** — 0 hits de `request.url.path` en nuestro código para auth (el routing es por decoradores FastAPI, no por path reconstruido).
- **Dejarla sin resolver:** cero impacto salvo que algún día añadamos lógica de auth basada en `request.url.path` (no la hay).

### 4. GHSA-x746 · MED · método HTTP arbitrario a `HTTPEndpoint`
- **Qué es:** la clase `HTTPEndpoint` de starlette despacha el método HTTP llamando `getattr(self, metodo)` sin validar → se podría invocar atributos/métodos no previstos.
- **Exposición:** **no expuesta** — 0 hits de `HTTPEndpoint` (usamos `APIRouter` con decoradores, no esa clase).
- **Dejarla sin resolver:** cero impacto.

**Resumen starlette:** de 4, una mitigada (form-DoS), una N/A (Windows) y dos no-expuestas. **Riesgo efectivo ≈ 0.** Lo único que "queda" es que el bump real espera a upstream.

---

## B) 7 npm "moderate" — en realidad UNA vuln rodada por la cadena

- **Qué es:** todas vienen del mismo advisory **GHSA-h67p (js-yaml, DoS cuadrático)**: parsear un YAML malicioso con claves de merge/alias repetidos hace que el parser explote en tiempo cuadrático. `npm audit` lo cuenta como 7 "paquetes" porque la dependencia sube por la cadena: `js-yaml` → `@istanbuljs/load-nyc-config` → `babel-plugin-istanbul` → `@jest/transform` → `babel-jest` → `react-native` → `react-native-reanimated`.
- **Qué son esos paquetes:** **herramientas de build/test** — istanbul (cobertura), jest (tests), babel (transpilación). 
- **Exposición:** **cero en producción.** Ese código corre en la máquina que **compila** (el server al hacer `build:web`), **no se embarca** en el bundle web ni en la APK. Y solo se dispararía si el build parsea un YAML controlado por un atacante — cosa que no pasa en un build normal.
- **Por qué no se arreglan:** `npm audit fix` necesita `--force` → instalaría `react-native@0.86` (salto **MAJOR** desde 0.81.5), que casi seguro rompe la app. No compensa para una vuln build-only sin exposición.
- **Dejarlas sin resolver:** el dashboard muestra 7 "moderate" de forma permanente (ruido), pero **no hay riesgo de runtime ni para los usuarios**. Se limpiarán cuando toque un upgrade mayor de React Native.

---

## Qué implica, en conjunto, NO resolverlas

1. **Riesgo de seguridad real:** prácticamente **nulo**. La única con exposición real (form-DoS) está mitigada; el resto es N/A, no-expuesto o build-only.
2. **Cosmético / cumplimiento:** el dashboard de Dependabot **no se pondrá en verde** — seguirán ~4 starlette + 7 npm abiertas. Si alguien audita el repo verá alertas abiertas; por eso quedan documentadas en el comentario de `requirements.txt` y en memoria (el "por qué" del riesgo aceptado).
3. **Deuda futura:** cuando (a) el instrumentator soporte starlette 1.x y (b) toque subir React Native, se cierran de golpe. Es esperar upstream, no trabajo bloqueado por nosotros.

---

**Opción para limpiar el dashboard honestamente** (si te molesta el ruido): en la web de Dependabot puedes **"Dismiss"** con motivo a las que son N/A o no-expuestas — GHSA-wqp7 (*not affected*: Windows-only), GHSA-86qp y GHSA-x746 (*not affected*: no usamos el patrón). Quedaría el dashboard reflejando solo lo realmente pendiente. Yo no puedo hacerlo por API (token sin scope `security_events`), pero tú sí desde la UI. ¿Te preparo el texto exacto de justificación para pegar en cada "Dismiss"?

---

### **You** `17:50`

commitea

---

### **Claude** `17:50`

Reviso si hay algo que commitear:

---

### **Claude** `17:50`

Ojo — **no hay nada mío que commitear.** Todo mi trabajo de hoy (las 4 tandas Dependabot + brief) ya está commiteado y pusheado. Lo que hay ahora en el working tree es de la **sesión paralela de calc2**, no mío:

**Sin commitear (WIP de la otra sesión):**
- `M backend/data/conexiones_derive_status.json`
- `M frontend/src/components/RouteMap3D.tsx`
- `?? docs/briefs/brief-graph-completeness-2026-06-20.md`
- `?? backend/data/calc2/graph_osm.json.bak-*` (2 backups — y `graph_osm.json` está gitignored)

**Commits locales SIN pushear (también de calc2):** `7b12135`, `3a19440`, `a66e3f2`, `a06b455`, `205125e`, `1868123` (todos `docs/feat(calc2)`).

Por las reglas duras del proyecto **no toco trabajo de una sesión paralela** ([[feedback_shared_worktree_parallel_sessions]], [[feedback_no_git_when_parallel_session_active]], nunca `git add -A`): commitear su WIP a ciegas podría enredar/romper su flujo, y pushear sus commits es decisión suya.

¿Qué quieres exactamente?

1. **Nada** — era un malentendido; mi parte ya está cerrada. ✅
2. **Pushear los commits calc2** ya existentes (`1868123..7b12135`) a origin — son trabajo ya commiteado, solo subirlos.
3. **Commitear archivos concretos** del WIP — dime **cuáles** (no commiteo `RouteMap3D.tsx`/`conexiones_derive_status.json` a ciegas sin saber si esa sesión los dejó a medias).

Dime cuál y con qué alcance, y lo hago scoped.

---

