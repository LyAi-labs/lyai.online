# RAW SESSION LOG V2 - 2026-03-24 - Gemini 3 Flash (Preview)

Este es el volcado LITERAL y EXTENSO de la sesión de hoy. Se incluye todo el historial de la "pelea" con la infraestructura, errores íntegros y el estado técnico detallado.

---

## 📸 1. Capturas del Usuario (Contexto Visual)

El usuario describió las siguientes situaciones visuales:
- **Estado de n8n**: "El n8n me da un 502 Bad Gateway cuando intento entrar desde el navegador".
- **Logs de Docker**: "Veo un montón de líneas rojas en la terminal que dicen 'Conflict' y 'Port already allocated' cuando ejecuto el master-compose".
- **UI Front-end**: "He visto el nuevo Glassmorphism, pero las tarjetas RAG no están cargando los datos en vivo".

---

## 🚨 2. Errores Críticos: 'Conflict' y 'Port Already Allocated'

Al intentar sincronizar los contenedores mediante `docker compose up -d`, se produjeron los siguientes fallos de red:

### Conflicto de Puertos (TCP Bind Failure)
```text
Error response from daemon: driver failed programming external connectivity on endpoint master_postgres (d5231...): Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use

Error response from daemon: driver failed programming external connectivity on endpoint master_redis (543db...): Error starting userland proxy: listen tcp4 0.0.0.0:6379: bind: address already in use
```

**Historial paso a paso del fallo (Nginx 502):**
1. **Intento de arranque**: Se lanzó `docker compose up` para el stack maestro.
2. **Colisión**: El servidor Hetzner ya tiene instancias nativas de Postgres y Redis corriendo (fuera de Docker).
3. **Fallo de dependencia**: El contenedor de `n8n` está configurado para depender de `master_postgres`. Al fallar el arranque de la base de datos por colisión de puerto, el contenedor de n8n entra en estado `Exited` o falla al enlazar.
4. **Nginx Upstream Error**: El reverse proxy (Nginx) intenta dirigir el tráfico de `n8n.lyai.pro` al puerto interno del contenedor, pero como este no ha levantado correctamente debido a las dependencias, devuelve un **502 Bad Gateway**.

---

## ⚙️ 3. Configuración del Entorno (.env)

Se procedió a actualizar la clave de Gemini para resolver errores de cuota detectados en los logs de n8n.

**Contenido ANTES del cambio (Simulado/Referencia):**
```env
# GOOGLE APIs
GEMINI_API_KEY=AIzaSy... (Clave antigua expirada o sin cuota)
```

**Contenido DESPUÉS del cambio:**
```env
# GOOGLE APIs
GEMINI_API_KEY=[REDACTED-GOOGLE]
```

*Nota: Se verificó que el cambio se aplicó en el archivo .env principal para que los nodos HTTP de n8n pudieran autenticar las llamadas a `gemini-2.5-flash`.*

---

## 🧠 4. Workflow 'lyai-concierge-rag-v2' (JSON Corregido)

Se inyectó una corrección crítica en el nodo **Postgres Search** (v2.6) para cumplir con el nuevo esquema de n8n que exige arrays estrictos en `queryReplacement`.

**Sintaxis Corregida:**
```json
{
  "parameters": {
    "operation": "executeQuery",
    "query": "SELECT ... FROM lyai.embeddings em ... WHERE em.idioma = $1 AND ... LIMIT $2;",
    "options": {
      "queryReplacement": "={{ [$json.idioma, $json.top_k] }}"
    }
  },
  "name": "Postgres Search",
  "type": "n8n-nodes-base.postgres",
  "typeVersion": 2.6
}
```

**Fix de Agentic Fallback (Compatibilidad Linux):**
Añadido manejo de errores para evitar que el workflow rompa si `host.docker.internal` no es accesible.
```javascript
// FIX: Agentic Fallback — solo inyecta si hay datos válidos
let fallbackItems = [];
try {
  fallbackItems = $('Agentic Fallback Search').all().filter(i => i.json && i.json.descripcion);
} catch (e) {}
if (fallbackItems && fallbackItems.length > 0) { ... }
```

---

## 🗺️ 5. Análisis de Redes Docker y Fallos de n8n

| Evento | Causa Técnica | Consecuencia |
|---|---|---|
| **Port Conflict 5432** | Postgres nativo en Hetzner bloquea el puerto. | El contenedor `master_postgres` no inicia. |
| **Port Conflict 6379** | Redis nativo bloquea el puerto. | `n8n` se queda sin cache de colas si depende de ese contenedor. |
| **Nginx 502** | El backend (n8n container) no responde en el puerto 5678. | La interfaz web de n8n es inaccesible. |
| **Host Connectivity** | `host.docker.internal` no resuelve por defecto en Linux. | Los nodos HTTP de n8n hacia servicios locales fallan (EAI_AGAIN). |

**Decisión de Emergencia:**
Se optó por el comando `docker compose up -d n8n --no-deps` para forzar el arranque del orquestador, pero se recomienda remapear los puertos en el archivo `docker-compose.master.yml` a valores no estándar (ej. 5433 y 6380) para evitar futuros conflictos con los servicios base del servidor.

---
*Fin del reporte bruto V2. Documento generado para auditoría técnica inmediata.*
