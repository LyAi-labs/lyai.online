# RAW SESSION LOG - 2026-03-24 - Gemini 3 Flash (Preview)

Este documento contiene el volcado técnico bruto de la sesión, incluyendo diagnósticos, comandos fallidos, soluciones de emergencia y el código corregido.

## 1. Diagnóstico de Red y Puertos (Conflictos en Hetzner)

### Error Detectado: Bind for 0.0.0.0:6379 / 5432 failed
Al intentar levantar el stack con `docker-compose.master.yml`, el sistema falló debido a que los puertos estándar ya estaban ocupados por servicios del host o contenedores huérfanos.

**Contexto del Error:**
```bash
$ docker compose up -d
[+] Running 0/2
 ⠋ Container master_postgres  Error
 ⠋ Container master_redis     Error
Error response from daemon: driver failed programming external connectivity on endpoint master_redis (543db...): Error starting userland proxy: listen tcp4 0.0.0.0:6379: bind: address already in use
```

**Análisis Técnico:**
- **Puerto 5432**: Ocupado por una instancia de PostgreSQL nativa del servidor (posiblemente la BD principal de LyAi enviando logs o para servicios críticos).
- **Puerto 6379**: Ocupado por Redis, bloqueando el arranque del contenedor de n8n que depende de su propia instancia de Redis para el modo queue/cache.

### Solución Propuesta (Workaround): --no-deps
Se intentó arrancar n8n ignorando las dependencias que fallaban (BD/Redis) para validar si el binario era funcional, aunque esto causara errores de conexión internos en n8n:
```bash
docker compose up -d n8n --no-deps
```

## 2. Nueva API Key (Gemini)
Se actualizó la clave en el archivo `.env` para resolver errores de cuota/expiración.

**Clave Nueva:** `[REDACTED-GOOGLE]`

**Ubicación:** [/.env](/.env#L66)
```env
# GOOGLE APIs
GEMINI_API_KEY=[REDACTED-GOOGLE]
```

## 3. Workflow n8n Corregido (JSON Bruto)
Se detectaron fallos de sintaxis en el nodo de PostgreSQL (n8n v1.x+) donde `queryReplacement` ahora exige estrictamente un array `{{ [] }}`.

**Archivo Generado:** [/lyai-core/n8n/workflows/lyai-concierge-rag-v2.json](/home/aipa/projects/lyai-core/n8n/workflows/lyai-concierge-rag-v2.json)

### Piezas Clave del JSON Corregido:

**Nodo Postgres Search (Fix de Sintaxis):**
```json
{
  "parameters": {
    "operation": "executeQuery",
    "query": "SELECT ... FROM lyai.embeddings em JOIN ... WHERE ... LIMIT $2;",
    "options": {
      "queryReplacement": "={{ [$json.idioma, $json.top_k] }}"
    }
  },
  "name": "Postgres Search",
  "type": "n8n-nodes-base.postgres",
  "typeVersion": 2.6
}
```

**Fix Agentic Fallback (Linux compatibility):**
Se modificó para manejar fallos silenciosos cuando `host.docker.internal` no es resoluble en el entorno Linux de producción:
```javascript
// FIX: Agentic Fallback — solo inyecta si hay datos válidos (falla silent en Linux)
let fallbackItems = [];
try {
  fallbackItems = $('Agentic Fallback Search').all().filter(i => i.json && i.json.descripcion);
} catch (e) {}
if (fallbackItems && fallbackItems.length > 0) {
    let fb = fallbackItems[0].json;
    if (fb.descripcion && fb.entidad_id !== null) {
        dbContext += "\\n\\n[RESULTADOS EN VIVO - AGENTIC FALLBACK]:\\n" + fb.descripcion;
    }
}
```

## 4. Estado de la Infraestructura al cierre

| Servicio | Estado | Puerto Conflictivo | Nota |
|---|---|---|---|
| PostgreSQL | Bloqueado | 5432 | Puerto en uso por el Host (Ignacio) |
| Redis | Bloqueado | 6379 | Puerto en uso por el Host |
| n8n | Caído (502) | 5678 | Nginx no llega al contenedor |

**Próximo paso sugerido para Claude:**
Reconfigurar `docker-compose.master.yml` para mapear puertos alternativos (e.g., `5433:5432`) o usar `network_mode: "host"` para que n8n hable directamente con los servicios del servidor Hetzner sin intentar levantarlos en Docker.
