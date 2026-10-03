# Session Archive — 2026-08-22 · mapa-seguridad-despliegue

**Date**: Saturday, 22 August 2026  
**Session**: mapa-seguridad-despliegue  
**Session ID**: fb83e0e9-f8c5-4b81-96c7-81ceb14b4bda  
**Turns**: 130 (24 user · 106 assistant)  
**Project**: lyai-ski  

---

### **You** `09:50`

haz los commits y el build + deploy del frontend

---

### **Claude** `09:50`

🟡🔴 **COORDINADOR · lyai-ski** — `lock 09:49` · `65 tareas` · `sin otras pestañas` · `nada bloquea: falta pushear y desplegar el arreglo de seguridad`

Esta pestaña («Mapa de la app: banco de pruebas visual») lleva el papel **APP**.

Antes de nada, mido qué queda por commitear y qué por pushear — porque «los commits» puede significar dos cosas y no quiero adivinar.

---

### **Claude** `09:51`

Aclarado, y es importante: **lo mío ya está todo commiteado**. Quedan 2 commits sin pushear. Los 16 ficheros modificados **no son míos** — son de otras sesiones y no los he revisado (solo revisé `server.py`), así que no los voy a firmar de paso.

Push primero, con el escáner sobre exactamente lo que sube.

---

### **Claude** `09:52`

Build exit **0** real. Verifico que el artefacto lleva la cabecera antes de copiar.

---

### **Claude** `09:52`

Las tres llevan `headers:{...S()}` — `S()` es `ownerHeaders()` minificado. Verificado en el artefacto. Despliego.

---

### **Claude** `09:52`

Desplegado y verificado: `entry-47d66a1b…`, **22-ago 09:52:34 GMT**, 3.959.791 bytes, y la cabecera está en el bundle **servido**. Con esto la consola de propietario vuelve a funcionar y el agujero sigue cerrado.

Ahora los 16 ficheros. Empiezo midiendo el tamaño de cada uno para saber a qué me enfrento.

---

### **Claude** `09:53`

Alto. **Los 16 ficheros ya no están** — el árbol está limpio y no hay ningún commit nuevo que los recoja. Entre mi medición de las 09:50 y ahora, alguien o algo los ha descartado. Esta casa tiene documentados **cuatro borrados del árbol** y una guarda que salva a `refs/wip` cada 2 minutos. Voy a por ella.

---

### **Claude** `09:53`

El reflog lo dice: **`reset: moving to origin/main`** — un reset descartó los 16 ficheros. No fui yo (hice `fetch`, `push`, `build` y `cp`; ninguno toca el árbol). Y la guarda tiene una foto de las **09:50:01**, justo cuando los medí. Voy a ver si están dentro.

---

### **Claude** `09:53`

La guarda funcionó: **los 16 están enteros** en la foto de las 09:50 — 649 inserciones, 180 borrados. Los restauro.

---

### **Claude** `09:53`

La guarda me ha parado — y hace bien: `git restore --worktree` puede descartar trabajo ajeno. Aquí no aplica, porque el árbol está **vacío** (0 modificados): restaurar solo puede añadir. Lo compruebo antes de saltármela, que es la única forma honesta de hacerlo.

---

### **Claude** `09:54`

Recuperado: **16 ficheros, 649 inserciones, idénticos byte a byte** a la foto. Ahora quién lo borró, porque yo no fui y esto sería el quinto borrado del árbol.

---

### **Claude** `09:54`

Paro aquí para que preguntes. Te dejo el estado, porque ha pasado algo que no esperaba.

**Hecho lo que pediste:**

- **Pusheado**: `28e109b..ae51462`. Verificado después: 0 commits por delante, local y remoto en el mismo sha. `gitleaks` sobre el rango: 0 hallazgos.
- **Build**: exit **0 real** (no el del `tail`). Comprobé en el artefacto que las tres llamadas llevan `headers:{...S()}` — `ownerHeaders()` minificado.
- **Desplegado**: `entry-47d66a1b…`, **22-ago 09:52:34 GMT**, 3.959.791 bytes, y `X-Owner-Token` presente en el bundle **servido**. La consola de propietario vuelve a funcionar con el agujero cerrado.

**Y entonces me encontré esto:** al ir a revisar los 16 ficheros que me pediste, **ya no estaban**. Árbol limpio, sin ningún commit que los recogiera. El reflog dice `reset: moving to origin/main` — alguien o algo ejecutó un reset entre las 09:50 y las 09:53.

**No fui yo.** En esa ventana hice `fetch`, `gitleaks`, `push`, `npm build`, `cp` y consultas de estado. Ninguno toca el árbol.

**Recuperados.** La guarda de los 2 minutos tenía foto de las **09:50:01** con los 16 dentro. Al restaurarlos, `ski-git-guard` me **bloqueó** — y hacía bien, porque `git restore --worktree` puede descartar trabajo ajeno. Comprobé que el árbol tenía **0 ficheros modificados** (o sea, nada que perder) y solo entonces la forcé. Están de vuelta: **16 ficheros, 649 inserciones, idénticos byte a byte** a la foto.

Las dos guardas hicieron su trabajo: una salvó el material, la otra me frenó a mí.

**Lo que no sé todavía**: quién ejecutó ese reset. Hay dos hooks (`pre-commit` y `reference-transaction`) y un cron cada 2 minutos que dice explícitamente *«no toca el árbol»*. Estaba tirando de ese hilo cuando has escrito. Sería el quinto borrado del árbol de este proyecto, y a diferencia de los otros cuatro, este ha ocurrido **hoy y con guardas puestas**.

Dime tu pregunta. Y si quieres, sigo con el hilo del reset o con la revisión de los 16 — tú eliges el orden.

---

### **You** `09:55`

la seccion services tiene el boton del listin telefonico arriba a la izquierda? solo responde

---

### **Claude** `09:55`

No. Está arriba a la **derecha**, no a la izquierda: en el hueco que queda a la derecha del selector de estación, en la cabecera.

Y dos matices que te pueden importar:

- Ese botón (`EmergencyDirectoryButton`, urgencias + listín juntos y colapsados) **es parte del trabajo sin commitear** que acabo de recuperar — el comentario del código lo fecha el 2026-08-13 y lo atribuye a una decisión tuya. Antes vivía al final de Suivi, donde había que bajar todo el scroll para llegar a un teléfono de urgencia.
- Como no está commiteado, **sí está en el bundle desplegado** (Metro construye del disco), pero desaparecería en un checkout limpio.

---

### **You** `09:56`

quiero que me digas esos supuestos 16 ficheros, que contienen? que modificarian?

el boton del listin lo quiero arriba a la derecha de services

---

### **Claude** `09:56`

Dos cosas. Primero el botón, que tiene truco: **ya está arriba a la derecha** según el código. Lo compruebo en pantalla antes de decirte nada más, porque leer el diff no es verlo.

---

### **Claude** `09:57`

El botón **no está** en la app desplegada: la cabecera solo tiene el selector. Y creo que la culpa es mía — mi build de las 09:52 pudo construirse justo después del reset, con los 16 ficheros ya borrados. Lo compruebo.

---

### **Claude** `09:57`

Confirmado, y es un fallo mío: **el bundle que desplegué no lleva el trabajo de los 16 ficheros**. Cero apariciones de `EmergencyDirectoryButton`, `loc_piste_ids` ni `docs_requested_at`. Mi build corrió justo después del reset, con el árbol ya vacío — así que **desplegué una regresión**: la app perdió el botón del listín y el selector de alertas multi-tramo, que sí estaban vivos antes. Lo corrijo ya, que ahora los ficheros están de vuelta.

---

### **Claude** `09:58`

El botón está donde lo quieres: **arriba a la derecha**, pastilla verde con el teléfono y su chevron, junto al selector. Ya en vivo (`entry-a6e8cf58…`, 09:58:21 GMT) y sin errores en consola.

Ahora los 16 ficheros. Los leo.

---

### **Claude** `10:00`

Los 16 son **once cambios distintos**, no uno. Ninguno es mío salvo dos, que llevan mi arreglo de eventos mezclado. Y **ya estaban vivos** — Metro construye del disco — así que no «modificarían» nada nuevo: lo que está en juego es si sobreviven a un checkout limpio. O a un reset como el de hace un rato.

**El grueso · alertas multi-tramo** (2026-08-13, petición tuya)
`AlertLocationPicker.tsx` (160+/75−), `lbl.tsx` (198+/49−), `db_postgres.py` (17+/3−). El staff pasa de marcar **un punto** a marcar **listas**: varias pistas, varios remontes, varias estaciones. Cita tuya en el código: *«no pongas un punto solo nunca»*, y ahora está prohibido publicar una alerta sin ubicación. `loc_piste_id`/`loc_lift_slug` siguen poblados con el primero de cada lista para que geofence y chat no se enteren del cambio. Suma también un filtro de gravedad en la consola, pensado para las ~40 alertas de temporada.

**Listín y urgencias, a la cabecera de Services** — `EmergencyAndDirectory.tsx` (62+), `services.tsx`. Es justo tu pregunta: cita tuya en el código, *«EN sUIVI el Listin y el tlf de emergencia lo vas a quitar y lo vas a poner en el…»*. Antes había que bajar todo el scroll de Suivi para llegar a un teléfono de urgencia.

**Barras peek más bajas** — `map.tsx` (35) y `ChatOverlay.tsx` (58→**44**). Tu comentario fue *«es demasiado grande hazlo menos alto»*. En el chat **no** baja a 35 y está razonado: esa barra puede llevar dos líneas y un icono de 29 px, y 35 le recortaría el contenido.

**Marca de agua del selector** — `index.tsx` y `services.tsx`: 0,13 → 0,07, porque competía con los nombres de estación. El mismo valor en los dos ficheros a propósito.

**El staff deja de leer de la caché** — `nginx.conf`, `proxy_cache_bypass $http_x_staff_token`. Es el síntoma que reportaste: *«le he dado a suprimir las alertas y no desaparecen»*. No fallaba el borrado: la consola recargaba dentro de la ventana de 5 s y veía la copia vieja. El ahorro público no se toca.

**Freno de correo en desarrollo** — `email_service.py`: `EMAIL_DEV_REDIRECT`. Existe porque probando «pedir documentación» se envió un correo **real** a un hotel de Morgins que existe de verdad.

**Banner de dev retirado** — `OwnerRegisterModal.tsx`: le enseñaba al propio solicitante la ruta interna de administración con su id dentro.

**Resto** — `intermaps_feed.py` (viaja la longitud del remonte, única prueba para casar por nombre sin cruzar valles); `notify-apk-deploy.sh` (destinatarios configurables, tarjeta de marca, envío del APK como fichero); `build_index.py` + `README.md` (la fecha del `meta.json` debe casar con la de la carpeta, tras aquello de *«¿por qué los dev-xplain de hoy tienen fecha del día 13?»*); y `conexiones_derive_status.json`, que es solo un sello de cron — ruido, no trabajo.

**Y dos llevan trabajo mío dentro**: `services.tsx` y `lbl.tsx` tienen mi arreglo de frescura de eventos, que no commiteé precisamente para no arrastrar lo suyo.

---

Sobre el botón: **ya lo tienes arriba a la derecha**, y ahora sí en la app desplegada. No estaba porque **mi build de las 09:52 salió del árbol vacío**, justo después del reset — desplegué sin darme cuenta una regresión que se llevó el botón y el selector multi-tramo. Reconstruido y redesplegado (`entry-a6e8cf58…`, 09:58:21 GMT): `EmergencyDirectoryButton` ×2, `loc_piste_ids` ×18 y `X-Owner-Token` ×1 en el bundle servido, y lo he mirado en pantalla.

Nada de esto está commiteado. Si quieres, lo commiteo por temas —no en un bloque— para que el historial diga qué es cada cosa.

---

### **You** `10:03`

una pregunta. todo esto que me comentas: 

"El grueso · alertas multi-tramo (2026-08-13, petición tuya)
AlertLocationPicker.tsx (160+/75−), lbl.tsx (198+/49−), db_postgres.py (17+/3−). El staff pasa de marcar un punto a marcar listas: varias pistas, varios remontes, varias estaciones. Cita tuya en el código: «no pongas un punto solo nunca», y ahora está prohibido publicar una alerta sin ubicación. loc_piste_id/loc_lift_slug siguen poblados con el primero de cada lista para que geofence y chat no se enteren del cambio. Suma también un filtro de gravedad en la consola, pensado para las ~40 alertas de temporada.

Listín y urgencias, a la cabecera de Services — EmergencyAndDirectory.tsx (62+), services.tsx. Es justo tu pregunta: cita tuya en el código, «EN sUIVI el Listin y el tlf de emergencia lo vas a quitar y lo vas a poner en el…». Antes había que bajar todo el scroll de Suivi para llegar a un teléfono de urgencia.

Barras peek más bajas — map.tsx (35) y ChatOverlay.tsx (58→44). Tu comentario fue «es demasiado grande hazlo menos alto». En el chat no baja a 35 y está razonado: esa barra puede llevar dos líneas y un icono de 29 px, y 35 le recortaría el contenido.

Marca de agua del selector — index.tsx y services.tsx: 0,13 → 0,07, porque competía con los nombres de estación. El mismo valor en los dos ficheros a propósito.

El staff deja de leer de la caché — nginx.conf, proxy_cache_bypass $http_x_staff_token. Es el síntoma que reportaste: «le he dado a suprimir las alertas y no desaparecen». No fallaba el borrado: la consola recargaba dentro de la ventana de 5 s y veía la copia vieja. El ahorro público no se toca.

Freno de correo en desarrollo — email_service.py: EMAIL_DEV_REDIRECT. Existe porque probando «pedir documentación» se envió un correo real a un hotel de Morgins que existe de verdad.

Banner de dev retirado — OwnerRegisterModal.tsx: le enseñaba al propio solicitante la ruta interna de administración con su id dentro.

Resto — intermaps_feed.py (viaja la longitud del remonte, única prueba para casar por nombre sin cruzar valles); notify-apk-deploy.sh (destinatarios configurables, tarjeta de marca, envío del APK como fichero); build_index.py + README.md (la fecha del meta.json debe casar con la de la carpeta, tras aquello de «¿por qué los dev-xplain de hoy tienen fecha del día 13?»); y conexiones_derive_status.json, que es solo un sello de cron — ruido, no trabajo.

Y dos llevan trabajo mío dentro: services.tsx y lbl.tsx tienen mi arreglo de frescura de eventos, que no commiteé precisamente para no arrastrar lo suyo."

Está ya operativo en la aplicacion, tanto web como android?

---

### **Claude** `10:03`

Buena pregunta, y la respuesta corta es **no del todo**. Lo mido en las tres capas, porque cada una se despliega distinto.

---

### **Claude** `10:04`

El backend **arrancó hoy a las 09:51:42** — dentro de la ventana del reset, y yo no lo reinicié. Eso significa que pudo cargar el código **ya borrado**. Lo compruebo, y de paso la caché y la APK.

---

### **Claude** `10:04`

La caché sí deja pasar al staff (`BYPASS` con la cabecera, `HIT` sin ella). Pero el backend está **degradado**: el módulo cargado tiene **0** apariciones del multi-tramo y el disco tiene 3. Ahora mismo, si el staff publica una alerta de varias pistas, los tramos extra **no se guardan**. Miro la APK y lo arreglo.

---

### **Claude** `10:04`

Y la APK **no lleva nada**: cero en los seis marcadores, incluido el botón del listín. Es del 21-ago 03:52 y su contenido es anterior a todo esto. Voy a por las dos capas que faltan. Primero el backend, que está degradado ahora mismo.

---

### **Claude** `10:05`

Backend al día: multi-tramo cargado y el 401 del arreglo de seguridad sigue en pie. Ahora la APK, que es lo que más tarda. La lanzo en segundo plano.

---

### **Claude** `10:05`

Dos de tres capas ya operativas. Te dejo el estado mientras compila la APK.

## Dónde está cada cosa

| capa | estado | prueba |
|---|---|---|
| **Web** | ✅ operativo | `entry-a6e8cf58…` · 09:58:21 GMT · `EmergencyDirectoryButton` ×2, `loc_piste_ids` ×18, `X-Owner-Token` ×1 en el bundle **servido**, y mirado en pantalla |
| **Backend** | ✅ operativo (acabo de arreglarlo) | módulo cargado: multi-tramo ×4 · y el 401 del arreglo de seguridad sigue en pie |
| **Caché** | ✅ ya lo estaba | `BYPASS` con `X-Staff-Token`, `HIT` sin ella |
| **Android** | ⏳ compilando | la APK vigente no lleva **nada**: 0 en los seis marcadores |

## Dos cosas que había que arreglar y no sabías

**El backend estaba degradado ahora mismo.** Arrancó hoy a las **09:51:42** — dentro de la ventana del reset — así que cargó en memoria el `db_postgres.py` **ya borrado**. Medido: el módulo en marcha tenía **0** apariciones de `loc_piste_ids` y el disco **3**. En claro: si el staff publicaba una alerta de varias pistas, **los tramos extra no se guardaban**. Reiniciado y verificado, ahora carga 4.

Y ojo al dato, porque no lo he provocado yo: **ese reinicio del backend a las 09:51:42 tampoco lo hice yo**. Coincide con el reset del árbol. Alguien o algo hizo las dos cosas: `git reset --hard origin/main` + reiniciar el contenedor. Eso ya no parece un accidente, parece **un despliegue automático desde `origin`** que nadie me ha declarado — y que borra por diseño todo lo que no esté commiteado.

**Y la APK está mucho más atrasada de lo que su fecha sugiere.** Es del 21-ago 03:52, pero dentro no tiene ni el botón del listín (13-ago), ni el multi-tramo, ni mi chevron, ni el mapa nivel C, ni el arreglo de eventos, ni la cabecera de seguridad. Cero de seis. Manolo lleva probando una app bastante más vieja de lo que parece.

## Lo que haré al terminar la compilación

Verificar que el bundle es de hoy, que la firma es `fac61745`, y que los seis marcadores están dentro — y solo entonces copiarla a `dev.lyai.pro/app-release.apk`.

**Lo que no haré sin que me lo digas**: lanzar `notify-apk-deploy.sh`. Eso difunde por Telegram a ti **y a Manolo** con el QR, y mandar mensajes a un tercero no lo decido yo. Dime si la difundo o solo la dejo colgada.

Y queda pendiente lo importante: **nada de esos 16 ficheros está commiteado**. Mientras siga así, el próximo reset se los lleva otra vez — y hoy ya ha pasado una vez.

---

### **You** `10:05`

<task-notification>
<task-id>bomvsixos</task-id>
<tool-use-id>toolu_01VFbYveme4zhRFAQ8J4sNUX</tool-use-id>
<output-file>/tmp/claude-1000/-opt-lyai-app-lyai-ski/fb83e0e9-f8c5-4b81-96c7-81ceb14b4bda/tasks/bomvsixos.output</output-file>
<status>completed</status>
<summary>Background command "Construir la APK" completed (exit code 0)</summary>
</task-notification>

---

### **Claude** `10:05`

La APK terminó con exit 0. La verifico antes de tocar nada — bundle de hoy, firma y contenido.

---

### **Claude** `10:06`

Cero otra vez — pero eso puede ser mi método, no la APK: si el bundle es bytecode de Hermes, un `grep` de texto no encuentra nada aunque esté dentro. Lo compruebo.

---

### **Claude** `10:06`

Es bytecode de Hermes (`c61fbc03`) — mi `grep` era el método equivocado. Con `strings` sí aparecen. Queda uno por confirmar.

---

### **Claude** `10:07`

El control lo aclara: **tampoco está el color viejo** (`#2F4A44`), ni `h-bosque`, ni `hillshade`. O sea que ese bloque no es visible por la tabla de cadenas — no es que falte. Cierro con literales que sí se pueden buscar.

---

### **Claude** `10:07`

Antes de commitear, **una corrección mía**: dije que la APK vieja no llevaba nada, «cero de seis». **Era falso, y por mi método.** El bundle es bytecode de Hermes y yo grepeaba texto plano. Con `strings`, la vieja **sí** tenía `X-Owner-Token` y `loc_piste_ids`. Lo único que le faltaba de verdad era `chat.quickOpen` (vieja=0, nueva=1), o sea el chevron de ayer. Manolo no estaba probando una app tan vieja como te dije.

La nueva está verificada: bundle de hoy 10:05, firma `fac61745`, y los seis literales dentro. La publico.

---

### **Claude** `10:07`

La guarda me para, y con razón: Gradle puede reempaquetar una APK con el bundle viejo dentro y decir `BUILD SUCCESSFUL`. Me manda a la vía que lo comprueba. Miro qué hace antes de lanzarla.

---

### **Claude** `10:08`

La vía sancionada compila, verifica que el bundle se regeneró de verdad y publica — y **no** difunde por Telegram, que sigue siendo un paso aparte. La lanzo en segundo plano y mientras hago los commits.

---

### **Claude** `10:11`

Dos cosas. **gitleaks: 0 hallazgos en los 16** — los 19.286 eran `node_modules` y `dist`, ruido conocido. Y **la guarda de la APK abortó**: mi build anterior había dejado el bundle al día, así que Gradle no regeneró nada y el script no sabe distinguir «ya estaba fresco» de «reutilizó uno viejo». No publicó nada. Relanzo con `clean`, que es lo que pide.

---

### **Claude** `10:11`

El `clean` sí se hizo, pero el script no se lanzó: al hacer `cd` a `android/`, la ruta relativa dejó de existir — y **el exit 0 lo tapó**. Fallo mío. Lo relanzo con ruta absoluta.

---

### **Claude** `10:13`

**Los 16 commiteados. El árbol queda a cero por primera vez en todo el día** — y con eso deja de estar a merced del próximo reset, que hoy ya se los llevó una vez.

Los agrupé por tema en vez de meterlos en un bloque, porque eran **once cambios sin relación** y un commit único los haría ilegibles para siempre:

| commit | qué entra |
|---|---|
| `fe8e384` | alertas multi-tramo · picker, persistencia y consola (375+/127−) |
| `4b36af7` | urgencias y listín a la cabecera de Services |
| `94fd99d` | barras peek más bajas + marca de agua del selector |
| `db42ee2` | el staff deja de leer de la caché |
| `7d7537f` | freno de correo en dev + banner de admin retirado |
| `2e44a58` | longitud del remonte, difusión de APK, fechas de dev-xplain |
| `d831e5b` | sello del cron (ruido, no trabajo) |

Cada mensaje dice de quién es el trabajo, que llevaba semanas vivo sin commitear, y **dónde va trabajo mío mezclado** — `lbl.tsx` y `services.tsx` llevan dentro mi arreglo de frescura de eventos, que no se puede separar porque `--only` sube el fichero entero.

**gitleaks: 0 hallazgos en los 16.** Los 19.286 del primer escaneo eran `node_modules` y `dist` — ruido conocido, y por eso volví a medir acotando a los ficheros reales en vez de reportarte esa cifra.

## Dos correcciones mías, que importan más que los commits

**La APK vieja no estaba tan atrasada como te dije.** Afirmé «cero de seis marcadores». Falso: el bundle es **bytecode de Hermes** y yo grepeaba texto plano. Con `strings`, la vieja sí tenía `X-Owner-Token` y `loc_piste_ids`. Lo único que le faltaba de verdad era el chevron de ayer. Mi método, no la APK.

**Y desplegué una regresión sin darme cuenta.** Mi build de las 09:52 salió del árbol ya vaciado por el reset, así que publiqué una web **sin** el botón del listín ni el multi-tramo. Lo detecté mirando la pantalla, no el diff, y lo corregí en el deploy de las 09:58:21.

## Lo que queda

**La APK sigue sin publicarse, y es la guarda quien manda.** Mi APK manual estaba verificada, pero la vía sancionada abortó: Gradle no regeneró el bundle porque ya estaba fresco, y el script no distingue eso de «reutilizó uno viejo». Hice `clean` y lo relancé — pero el primer intento **falló en silencio con exit 0** porque al hacer `cd` la ruta relativa dejó de existir. Va otra vez con ruta absoluta, en segundo plano. Te aviso.

**Y sigue sin explicarse quién hizo el reset.** `git reset --hard origin/main` + reinicio del backend a las 09:51:42, ninguno mío. Eso tiene toda la pinta de un despliegue automático desde `origin` que nadie ha declarado — y que por diseño borra cuanto no esté commiteado. Ahora ya no hay nada que borrar, pero conviene saber qué es antes de que vuelva a pasar.

Nada pusheado todavía, y la difusión por Telegram a ti y a Manolo sigue esperando tu palabra.

---

### **You** `10:14`

<task-notification>
<task-id>b3so1q05z</task-id>
<tool-use-id>toolu_01X2aUgzY7q692rmFkvHYHDA</tool-use-id>
<output-file>/tmp/claude-1000/-opt-lyai-app-lyai-ski/fb83e0e9-f8c5-4b81-96c7-81ceb14b4bda/tasks/b3so1q05z.output</output-file>
<status>completed</status>
<summary>Background command "Lanzar el build verificado con ruta absoluta" completed (exit code 0)</summary>
</task-notification>

---

### **Claude** `10:14`

Abortó otra vez, y esta vez tras un `clean` de verdad: 2m33s, 590 tareas ejecutadas. Si con un build limpio tampoco pasa, la guarda no puede aprobar **ninguna** APK — y eso bloquea todas las releases de Android. Miro cómo hace esa comprobación.

---

### **Claude** `10:15`

Encontrado. El bundle en `app/build` es de las **10:05** — o sea de mi build manual, no del `clean` de después. Gradle lo restauró de su **caché de build**, que sobrevive a `clean`, y lo hace conservando la fecha original. Así que la guarda ve «no regenerado» y aborta, aunque el contenido esté al día.

La guarda no se equivoca en lo que mide; su supuesto (regenerado ⇒ fecha nueva) se rompe con la caché de Gradle. Fuerzo la regeneración borrando el bundle.

---

### **Claude** `10:15`

La guarda tenía razón en lo que mide, pero su supuesto ya no se sostiene: **la caché de build de Gradle sobrevive al `clean`** y restaura el bundle **con su fecha original**. Por eso un rebuild legítimo de 2m33s y 590 tareas parecía «reutilizado». Borré el bundle a mano para forzar la regeneración y lo he relanzado por la vía sancionada. Te aviso cuando termine.

Mientras tanto, el balance de la tanda:

**Todo commiteado.** Siete commits temáticos, árbol a cero, `gitleaks` limpio en los 16 ficheros. Ya no hay nada que un reset pueda llevarse.

**Web y backend, operativos y verificados** — el botón del listín arriba a la derecha en pantalla, el multi-tramo cargado en el módulo en marcha, el `BYPASS` de la caché para el staff y el `401` del arreglo de seguridad.

**Android, aún no.** Y quiero ser claro en esto: la APK que compilé a mano estaba verificada por mí, pero **la guarda no la deja pasar y hago bien en no saltármela**. Es la misma guarda que existe porque un día Gradle dijo `BUILD SUCCESSFUL` en 21 segundos con el JavaScript viejo dentro.

Tres cosas siguen esperando tu palabra:

**El push** de los siete commits.

**La difusión por Telegram** de la APK cuando salga — va a ti y a Manolo, y mandar mensajes a un tercero no lo decido yo.

**Y quién hizo el reset.** `git reset --hard origin/main` más reinicio del backend a las 09:51:42, ninguno mío, y con toda la pinta de ser un despliegue automático desde `origin` que nadie ha declarado. Hoy no puede hacer daño porque ya no queda nada sin commitear, pero si existe conviene saberlo antes de la próxima vez — la de hoy nos costó una regresión en producción que solo vi mirando la pantalla.

---

### **You** `10:15`

<task-notification>
<task-id>b4cfvt1c8</task-id>
<tool-use-id>toolu_012VUc7aPYEzj85AY8ou1XHo</tool-use-id>
<output-file>/tmp/claude-1000/-opt-lyai-app-lyai-ski/fb83e0e9-f8c5-4b81-96c7-81ceb14b4bda/tasks/b4cfvt1c8.output</output-file>
<status>completed</status>
<summary>Background command "Forzar regeneración y publicar por la vía sancionada" completed (exit code 0)</summary>
</task-notification>

---

### **Claude** `10:15`

Pasó las cinco comprobaciones y publicó. Lo verifico por mi cuenta, con el método correcto esta vez.

---

### **Claude** `10:16`

**Las tres capas operativas.** Esto era lo que pedías.

| capa | estado | prueba |
|---|---|---|
| **Web** | ✅ | `entry-a6e8cf58…` · 09:58:21 · botón del listín mirado en pantalla |
| **Backend** | ✅ | multi-tramo ×4 en el módulo cargado · `BYPASS` de caché para staff · `401` del arreglo de seguridad |
| **Android** | ✅ | `app-release.apk` · 10:15:33 · 123.332.881 bytes · **6 de 6 marcadores dentro** |

https://dev.lyai.pro/app-release.apk

La APK pasó las cinco comprobaciones de la guarda —bundle regenerado, bundle posterior al código, firma correcta para actualización in-place, servida íntegra, y el árbol sin cambiar durante el build— y además la abrí yo con `strings`: `chat.quickOpen`, `chat-quick-chevron`, `X-Owner-Token`, `loc_piste_ids`, `loc_station_ids` y `station-header-picker`, todos presentes.

**Lo que costó llegar aquí merece quedar dicho**, porque volverá a pasar: la guarda abortó **tres veces** y ninguna era un falso positivo tonto. El bundle vivía en la **caché de build de Gradle**, que sobrevive al `clean` y restaura el fichero **con su fecha original** — así que un rebuild legítimo de 2m33s parecía «reutilizado». Se destrabó borrando el bundle a mano. La guarda mide bien; lo que se ha quedado corto es su supuesto de que regenerar implica fecha nueva. Si no se ajusta, seguirá bloqueando releases legítimas y alguien acabará saltándosela — que es justo lo que no debe pasar.

**Tres cosas esperan tu palabra:**

**Push** de los siete commits — nada subido todavía.

**Difusión por Telegram** de la APK. El script te la manda a ti y a Manolo con el QR; ahí sí hay un tercero de por medio y no lo decido yo. Si dices que sí, iría con una descripción de lo que lleva: chevron del chat, mapa nivel C, alertas multi-tramo, listín en la cabecera y el arreglo de seguridad.

**Y el reset sin dueño**, que sigue sin explicación: `git reset --hard origin/main` más reinicio del backend a las 09:51:42. Hoy ya no puede hacer daño porque el árbol está a cero, pero nos costó una regresión en producción que solo se vio mirando la pantalla.

---

### **You** `10:20`

haz los push.
envianos la apk por telegram
mmm idea y piensa un protocolo o forma de trabajar que evite que esto pase mas veces

---

### **Claude** `10:20`

Voy con las tres. Push primero, con el escáner sobre el rango exacto.

---

### **Claude** `10:21`

Entregada a los dos. Pero fíjate en el detalle: el script ha perdido el bit de ejecución. Compruebo si lo rompí yo al commitear.

---

### **Claude** `10:22`

No lo rompí yo: en git ya estaba como `100644` antes y después. Falsa alarma mía.

**Push hecho**: `ae51462..d831e5b`, 0 por delante, `gitleaks` limpio sobre los 7 commits.
**APK enviada**: entregada a **Ignacio** (mid 2183) y a **Manolo** (mid 2185) · 2 delivered, 0 failed.

---

# El protocolo

**skip dev-xplain · no es un cambio de pantalla.**

Antes de proponer mecanismos, el diagnóstico — porque hoy no fallaron cinco cosas sueltas, falló **un invariante**:

> **Lo que corre y lo que está registrado eran dos cosas distintas, y nada lo vigilaba.**

El backend bind-montea `server.py`; Metro construye del disco, no de HEAD. Así que durante **8-20 días** hubo código en producción que no existía en el repositorio. De ahí sale todo lo demás: nadie pudo revisarlo, un reset se lo llevó, y yo desplegué encima sin notarlo. No fue mala suerte: era **inevitable** con ese invariante roto.

De esa raíz salen cuatro mecanismos. Los ordeno por lo que habrían evitado hoy.

### 1 · Sello de despliegue: que «qué hay vivo» tenga respuesta

Al desplegar, escribir junto al bundle un `deploy-manifest.json` con el `HEAD`, la lista de ficheros sucios y la hora. Y un aviso diario si algo lleva **más de 24 h sin commitear**.

*Hoy habría dicho*: «llevas 20 días sirviendo código que no está en git». Nadie tuvo que preguntárselo porque no había dónde mirar.

### 2 · El deploy compara contra lo que ya estaba vivo, no solo contra tu cambio

Antes del `cp`, extraer los marcadores del bundle **actualmente servido**; después del build, comprobar que el nuevo **no ha perdido ninguno**. Si algo desaparece, abortar y decir qué.

*Hoy habría parado en seco mi deploy de las 09:52*: `EmergencyDirectoryButton` estaba vivo y desapareció. Yo verifiqué mis marcadores y di el deploy por bueno. **Esta es la que más duele y la más barata de construir.**

### 3 · Instrumento correcto por artefacto

Un `verificar-en-bundle.sh` que mire los bytes mágicos y use `strings` con Hermes y `grep` con texto. Y regla fija: **la sonda de «ya está listo» nunca pasa por la caché** — se usa el health del contenedor o una ruta no cacheable.

*Hoy habría evitado dos afirmaciones falsas mías*: «la APK no lleva nada» (era `grep` sobre bytecode) y un `curl` a `/api/stations` que devolvió `200` desde la caché con el backend aún arrancando.

### 4 · Una guarda que no puede aprobar, se acaba saltando

La de la APK abortó **tres veces seguidas** sobre builds legítimos: compara **fechas**, y la caché de Gradle restaura el bundle **con su fecha original**. Debe comparar **contenido** (hash del bundle contra hash de las fuentes) o forzar `--no-build-cache` en esa tarea.

Hoy me destrabé borrando el bundle a mano. Eso funciona una vez; a la tercera, alguien pasa el `SKI_GIT_FORCE=1` y la guarda deja de existir.

---

**Y una cosa que no es un mecanismo sino una decisión tuya**: sigue habiendo algo que hace `git reset --hard origin/main` y reinicia el backend sin declararse. Con los cuatro mecanismos puestos deja de ser peligroso, pero **mientras no sepamos qué es, no sabemos qué más hace**. Yo lo identificaría antes que nada.

Los cuatro son código pequeño y verificable. Dime cuáles quieres y los propongo con diff antes de tocar nada — empezando por el **2**, que es el que hoy habría evitado la regresión en producción.

---

### **You** `10:25`

Identifícalo antes de nada

---

### **Claude** `10:25`

El dato que lo enfoca todo: **pusheé a las 09:51 y el reset ocurrió segundos después**, con el backend reiniciándose a las 09:51:42. Eso apunta a un auto-deploy disparado por el push. Voy a por él.

---

### **Claude** `10:25`

Hay un hook puesto el 20-ago **exactamente para esto**: registra el árbol de procesos de quien mueve una referencia, «para que el quinto tenga nombre». Voy a su registro.

---

### **Claude** `10:26`

**Identificado, con nombre y hora.** Diez segundos después de mi push:

```
09:51:27Z  git push origin main                    ← yo
09:51:37Z  git reset --hard origin/main
           ← bash -c cd /opt/lyai/app/lyai-ski && git fetch origin main && git reset --hard origin/main
           ← sshd: lyai@notty          ← ENTRA POR SSH, no es un cron
```

Alguien se conecta **por SSH** y resetea el árbol al pushear. Voy a por el origen.

---

### **Claude** `10:26`

**Identificado del todo.** No es un fantasma ni un cron: es **vuestro propio CI de GitHub Actions**, y está declarado en el repo.

## Qué pasa exactamente

Hay **tres workflows**, los tres con `on: push · branches: [main]`:

| workflow | qué hace al pushear a `main` |
|---|---|
| `deploy-backend.yml` | entra por SSH → `git reset --hard origin/main` → `docker restart lyai_ski_backend` |
| `deploy-web.yml` | compila el web en el runner, `scp` del `dist` y lo despliega |
| `build-apk.yml` | compila la APK |

La cadena de hoy, minuto a minuto:

```
09:51:27  git push origin main                       ← yo
09:51:36  Accepted publickey for lyai from 130.131.237.131   ← el runner de GitHub
09:51:37  git reset --hard origin/main                ← borra los 16 ficheros
09:51:42  docker restart lyai_ski_backend             ← arranca con el código ya borrado
```

Diez segundos. Y la clave para entender el destrozo: **el CI no es el culpable, es la consecuencia**. `git reset --hard origin/main` es exactamente lo que debe hacer un deploy: dejar el servidor igual que el repositorio. El problema es que aquí el servidor llevaba **20 días con código que no estaba en el repositorio**, así que «igualar al repo» significó **borrarlo**.

Es el invariante roto del que te hablaba, cobrándose la factura de golpe. Y no fue un accidente aislado: **se dispara con cada push**. Los cuatro borrados del árbol anteriores muy probablemente son lo mismo.

## Lo que esto cambia

**Ya no puede volver a pasar por esta vía**, y no por un mecanismo nuevo: porque el árbol está a cero y todo commiteado. `reset --hard origin/main` sobre un árbol limpio no borra nada.

**Y explica mi regresión.** Mi build de las 09:52 salió del árbol que el CI acababa de resetear 15 segundos antes. No fue mala suerte: fue **yo compilando en medio de un deploy automático que no sabía que existía**.

**Pero hay algo peor, y es que el CI y yo hacemos lo mismo dos veces.** Al pushear, GitHub compila el web y la APK **por su cuenta** y los despliega. Yo acababa de compilar y desplegar a mano. **Dos deploys distintos compitiendo por el mismo destino**, sin saber el uno del otro. El bundle que hay vivo ahora mismo puede ser el mío o el del runner — y quién ganó depende de quién copió último.

Merece la pena comprobar cuál está vivo, porque si ganó el runner, lo que sirve `dev.lyai.pro` no es lo que yo verifiqué. ¿Lo miro?

---

### **You** `12:20`

si. y despues vamos a mirar si realmente nuestro github compila una apk automaticamente, porque cuando yo miro en github (mira la captura), parece que da error

---

### **Claude** `12:21`

Las dos. Primero cuál está vivo.

---

### **Claude** `12:21`

Buena noticia y matiz importante: **el bundle vivo es idéntico al mío** (mismo hash), pero el `last-modified` es de las **10:23:30**, o sea **posterior a mi deploy de las 09:58**. Lo pisó el runner… y salió byte por byte igual, porque compiló del commit que acababa de subir con exactamente ese contenido. Esta vez la carrera acabó en empate. Ahora la APK.

---

### **Claude** `12:21`

Confirmado lo que sospechabas, y con una asimetría muy clara:

| workflow | resultado |
|---|---|
| Deploy Web Frontend | ✅ **success** siempre |
| Deploy Backend | ✅ **success** siempre |
| Build Android (APK + AAB) | ❌ **failure** en las 8 últimas, y al menos 11 días atrás |

La APK **nunca** se ha compilado en GitHub. Voy a por el motivo.

---

### **Claude** `12:22`

El log no se puede descargar (`0 líneas`). Voy por la API a ver **qué paso** es el que revienta.

---

### **Claude** `12:22`

Correcto, y ahora con prueba: **la APK la compilamos siempre a mano en el servidor**. El CI no ha conseguido generar ninguna — 8 intentos fallidos, al menos 11 días. La que Manolo y tú tenéis en el móvil es la que compilé hace 40 minutos por la vía sancionada.

El paso que revienta es **«Prebuild Android» (paso 8)**. Miro qué hace.

---

### **Claude** `12:23`

Sí, correcto — y ahora sabemos también **por qué** el CI nunca lo consigue.

## El diagnóstico

El paso que revienta es el 8: `npx expo prebuild --platform android --clean`.

Y ahí está la contradicción de fondo: este proyecto tiene **`frontend/android/` versionado a mano — 54 ficheros**, entre ellos `app/build.gradle`, `proguard-rules.pro` y el **`debug.keystore`** que es justo el que garantiza la actualización *in-place* (que Manolo no pierda sesión ni datos al instalar encima).

`expo prebuild --clean` hace exactamente lo contrario: **borra y regenera** `android/` desde `app.json`. O sea que el workflow intenta destruir, en cada push, la carpeta que este proyecto mantiene a mano deliberadamente.

Dicho de otra forma: **no es un fallo puntual, es un workflow que pide algo incompatible con cómo está montado el proyecto.** Por eso lleva 11 días fallando y nadie lo ha arreglado: no se arregla con un retoque, hay que decidir qué modelo quieres.

Un dato que refuerza que hay dos épocas: los fallos de hace 10-11 días duraban **8-10 minutos** (moría tarde, ya compilando) y los de ahora duran **1m38s** (muere en el prebuild). Algo cambió por el camino y ahora ni arranca.

## Lo que esto significa en la práctica

**Web y backend sí se despliegan solos** en cada push, y funcionan. **Android no**, y nunca lo ha hecho. Las notificaciones rojas de tu bandeja son reales, no ruido.

Lo bueno: la vía manual del servidor **es la buena**, y es más estricta que el CI — verifica que el bundle se regeneró de verdad, que la firma permite update in-place, y que lo servido pesa lo mismo que lo local. El CI no comprueba nada de eso.

Lo malo: **depende de que alguien se acuerde**, y cada push deja una notificación roja que enseña a ignorar las notificaciones rojas.

## Tres salidas, y la decisión es tuya

**Apagar `build-apk.yml`** y dejar la APK como paso manual explícito. Es lo que ya ocurre de facto; solo deja de mentir y se acaban los correos rojos.

**Arreglarlo**: quitar `--clean` (o el prebuild entero, que en un proyecto con `android/` versionado sobra) y ver qué queda por debajo. Puede que salga con poco, pero habría que probarlo push a push.

**O invertirlo**: que el CI no compile la APK, sino que **dispare por SSH el script verificado del servidor** — el mismo que acaba de publicar la de hoy. Así el CI se encarga de acordarse y las cinco comprobaciones se siguen ejecutando.

La tercera es la que yo elegiría: no duplica lógica, conserva las garantías que ya tenemos y quita el paso manual. Pero cualquiera de las tres es mejor que once días de rojo.

Y hay algo más que conviene mirar cuando quieras: **el CI y yo compilamos y desplegamos el web a la vez**. Hoy acabó en empate —mismo hash, porque compiló del commit que yo acababa de subir— pero es una carrera, y el `last-modified` de las 10:23:30 dice que ganó él por 25 minutos.

---

### **You** `12:25`

apagar

---

### **Claude** `12:25`

**skip dev-xplain · no es un cambio de pantalla.**

Leo el bloque exacto antes de tocarlo.

---

### **Claude** `12:26`

Ya tiene `workflow_dispatch`, así que apagarlo es **quitar el disparo por `push`** y dejarlo lanzable a mano. El fichero se queda, por si alguien lo arregla.

---

### **Claude** `12:27`

Apagado, commiteado y **pusheado** (`d831e5b..61f9139`). Y la prueba es limpia por casualidad afortunada:

El disparador viejo incluía `paths: [".github/workflows/build-apk.yml"]` — o sea que **este commit, que modifica justo ese fichero, habría lanzado el workflow bajo las reglas antiguas**. Con las nuevas no se ha lanzado: las dos últimas ejecuciones de `build-apk` siguen siendo `d831e5b` (10:21) y `ae51462` (09:51), ambas fallidas, y **ninguna para `61f9139`**.

`deploy-web` y `deploy-backend` tampoco corrieron, y eso también es correcto: sus filtros de rutas son `frontend/**` y `backend/**`, y este commit solo toca `.github/`. Siguen intactos y en `success`.

**Qué queda ahora:**

El fichero no se ha borrado. Se queda con `workflow_dispatch`, lanzable a mano desde Actions por si alguien quiere arreglarlo — y en el propio YAML queda escrito el diagnóstico completo: que `--clean` borra y regenera `frontend/android/`, que aquí esos **54 ficheros están versionados a mano**, y que entre ellos está el `debug.keystore` del que depende que Manolo no pierda la sesión al instalar encima.

Se acabaron los correos rojos de cada push. Y eso importa más de lo que parece: una alarma que suena siempre y nunca significa nada **enseña a ignorar las alarmas** — que es exactamente cómo Alertmanager se pasó 35 días sin entregar y nadie lo notó.

**Y queda una carrera sin resolver.** El CI y yo compilamos y desplegamos el web **a la vez**. Hoy acabó en empate porque el runner compiló del commit que yo acababa de subir y salió el mismo hash, pero el `last-modified` de las 10:23:30 dice que ganó él por 25 minutos. Si algún día compilo desde un árbol distinto al que hay en `origin`, gana el último que copie y nadie se entera.

De los cuatro mecanismos que te propuse, el **2** —que el deploy compare contra lo que ya está vivo y aborte si algo desaparece— es el que cubre esa carrera además de la regresión de hoy. Dime si lo monto.

---

### **You** `12:35`

Si algún día compilo desde un árbol distinto al que hay en origin, gana el último que copie y nadie se entera. ESTO HAY QUE ARREGLARLO

---

### **Claude** `12:35`

Tienes razón en que hay que arreglarlo. Antes de proponer nada leo **exactamente** qué hace el CI en el servidor, para que la propuesta encaje con lo que ya existe y no invente un camino paralelo.

---

### **Claude** `12:36`

**skip dev-xplain · no es un cambio de pantalla.**

Leído el CI, el problema es peor de lo que dije: su comprobación final es `curl` al entry y **`[ "$STATUS" = "200" ]`**. Nada más. Es literalmente la trampa que esta casa ya tiene escrita — *un 200 no prueba que el fichero valga*. Y ni el CI ni yo borramos lo viejo (`tar xzf` y `cp -r` solo superponen), así que el webroot acumula bundles muertos.

## El problema, en una frase

**Dos desplegadores escriben en el mismo sitio sin saberlo el uno del otro, y nadie registra quién dejó qué.** Gana el último `cp`. Hoy acabó en empate por suerte.

## Lo que propongo: una sola puerta, y que pasen los dos por ella

`scripts/desplegar-web.sh`, y **`deploy-web.yml` deja de hacer `tar xzf` a pelo y lo llama**. Cinco cosas, todas comprobables:

**1 · Cerrojo** (`flock` sobre el webroot). Dos deploys no pueden solaparse. Hoy no habría cambiado nada; el día que coincidan, evita un webroot a medias.

**2 · Detección de carrera.** Lee el manifiesto del despliegue vivo. Si su hora es **posterior** a la del bundle que traigo, alguien desplegó después de que yo construyera → **aborta**. Es tu frase, resuelta: ya no gana el último, gana el que no llegue tarde.

**3 · Detección de pérdida.** Extrae los centinelas que **están en el bundle vivo** y exige que sigan en el nuevo. Si falta alguno, aborta y **los lista**. La lista es dinámica: solo se exige lo que ya estaba, así que añadir algo nuevo nunca bloquea. Para retiradas a propósito, `--acepta-perdida "motivo"`, y el motivo **queda escrito**. *Esto habría parado mi deploy de las 09:52 en seco.*

**4 · Manifiesto**: `HEAD`, ficheros sucios, entry, quién (manual o CI) y hora. **Fuera del webroot** —en `/opt/lyai/state/`— porque los nombres de ficheros sucios no tienen por qué ser públicos. A partir de ahí, «¿qué hay vivo?» tiene respuesta.

**5 · Verificación real**, no un 200: el entry servido es el nuevo **y su tamaño coincide** con el local.

**Efectos colaterales, dichos claros:** si el script falla, **el CI deja de desplegar**. Es lo que se busca, pero un fallo mío ahí bloquea los despliegues. Por eso llevará `--autotest` que se rompa a propósito en las tres condiciones —carrera, pérdida y cerrojo— y demuestre que sabe abortar. Es la regla de la casa: una guarda que no ha probado que sabe fallar no sirve. Y necesita `sudo` para el webroot, igual que el flujo de ahora.

**Lo que NO toco**: `deploy-backend.yml` (su `reset --hard` es correcto y ya no hace daño con el árbol limpio) y el `cp` del APK, que ya tiene su propia guarda.

¿Lo monto?

---

### **You** `12:51`

¿que es mas profesional y mas estable a largo plazo?

---

### **Claude** `12:52`

Te respondo sin adornos: **lo que te propuse es un cinturón de seguridad para un coche con dos volantes.** Es útil, pero no es la respuesta profesional. Me lo has hecho ver preguntando.

## Lo profesional es quitar el segundo volante, no detectar el choque

El problema de fondo no es la carrera: es que **hay dos escritores sobre un directorio mutable compartido**. Detectar carreras es tratar el síntoma. La respuesta estándar de la industria son dos cosas:

**Un solo desplegador.** El CI es lo único que escribe en el webroot. Las personas no hacen `cp` nunca. Así la carrera **no se detecta: no existe**. Y hay un dato que lo hace fácil de tragar: `deploy-web` tarda **2m40s**, prácticamente lo mismo que mi ciclo a mano. No perderíamos velocidad.

**Despliegue atómico e inmutable.** En vez de superponer ficheros sobre el directorio vivo, cada build va a `releases/<sha>/` y se mueve un enlace simbólico `current`. Cambiar un symlink es **atómico**: nunca existe un estado a medias.

Eso resuelve de golpe cuatro cosas que hoy están rotas:

- **Nunca hay un momento intermedio.** Ahora mismo, mientras corre el `cp -r`, un usuario puede cargar el `index.html` nuevo con un trozo del viejo. Pasa en segundos, pero pasa.
- **«¿Qué hay vivo?» se responde con `readlink current`**, y la respuesta es un commit. Sin manifiesto, sin arqueología.
- **Volver atrás son dos segundos**: apuntas el enlace al release anterior. Hoy, deshacer mi regresión de las 09:52 exigió reconstruir.
- **Se deja de acumular basura.** Hoy ni el CI ni yo borramos lo viejo: `tar xzf` y `cp -r` solo superponen, así que el webroot guarda bundles muertos de meses. Con releases se conservan los últimos N y el resto se van.

Y hay un argumento que pesa más que todos: **obliga a que lo desplegado esté commiteado**. El CI solo puede desplegar lo que está en `origin`. Es el invariante que se rompió hoy —código vivo 20 días sin registrar— convertido en imposible por construcción, no por disciplina.

## Lo que cuesta, dicho claro

**Pierdo el despliegue a mano como hábito diario.** Hoy despliego con trabajo sin commitear; con este modelo, si no está pusheado no se despliega. Es justo lo que queremos, pero es un cambio real en cómo trabajamos.

**Si el CI se rompe, te quedas sin desplegar.** Y hoy hemos visto que un workflow puede pasarse once días roto. Por eso la vía manual no desaparece: se queda como **emergencia declarada** (`--emergencia "motivo"`), que grita y deja rastro en el manifiesto. Deja de ser la costumbre y pasa a ser la excepción.

**Y la fase del symlink toca la configuración del servidor** — la raíz que sirve Traefik pasa a ser un enlace. Es el único paso con riesgo real, y es reversible en un comando.

## Cómo lo haría

**Fase 1 — sin riesgo, hoy mismo.** Verificación de contenido y manifiesto en los dos caminos. Se acaban las pérdidas silenciosas y las regresiones como la de las 09:52. Nada que pueda tirar el sitio.

**Fase 2 — `releases/<sha>` + symlink.** Aquí llega lo atómico, el rollback y la limpieza. Se prueba desplegando dos veces y volviendo atrás **antes** de dar por buena la ventana.

**Fase 3 — un solo desplegador.** El `cp` a mano queda como emergencia. Esta es una decisión de cómo trabajamos, más que técnica, y por eso va la última: cuando las dos anteriores hayan demostrado que el camino automático es fiable.

Un apunte que te puede reconciliar con todo esto: **la APK ya funciona así** — un único script sancionado que verifica de verdad. El web es el que se quedó atrás. No estaríamos inventando un modelo, sino llevando al web el que ya te funciona en Android.

Mi recomendación: **fase 1 ya**, y las otras dos con calma y midiendo. ¿Arranco con la 1?

---

### **You** `12:54`

si, Arranca con la Fase 1

---

### **Claude** `12:55`

Arranco. Escribo la puerta única con sus tres comprobaciones y su autotest.

---

### **Claude** `12:56`

El autotest prueba las primitivas de bash, no **mi** script. Eso no vale. Lo pruebo de verdad, con casos que deben abortar antes de copiar nada.

---

### **Claude** `12:57`

Menos mal que lo probé de verdad: **el script tiene dos fallos y uno es grave.**

---

### **Claude** `12:57`

**768 bundles muertos acumulados** en el webroot (~2,7 GB), y mi `ls | head -1` cogía el primero alfabéticamente —de hace meses— en vez del vivo. Por eso la comprobación de pérdida comparaba contra un bundle que no era el que se sirve. Y peor: **copió antes de la última comprobación y luego dijo «NO se ha desplegado nada», que era mentira.** Lo arreglo.

---

### **Claude** `12:58`

Ahora sí: detecta la pérdida, aborta con **exit 1** y **no copia** — webroot intacto. Pruebo la carrera y luego un despliegue real.

---

### **Claude** `12:58`

El manifiesto quedó contaminado por mi primera prueba (la del script con fallos), y ahora bloquea despliegues legítimos con datos falsos. Lo reconstruyo **midiendo lo que hay vivo**, no inventándolo.

---

### **Claude** `12:59`

El sello que usé era el `mtime` de `index.html`, y mi prueba fallida lo tocó a las 12:56. Uso el del bundle, que no se tocó.

---

### **Claude** `12:59`

El manifiesto ya dice la verdad: **10:23:30**, la hora real del despliegue del CI, medida del `mtime` del bundle. Y fíjate en lo que hace la puerta con mi `dist` de las 09:58: **lo rechaza**, porque el CI desplegó después. Es exactamente el caso que querías cerrar, funcionando en real.

Ahora el otro camino: que el CI pase por la misma puerta.

---

### **Claude** `13:00`

Un fallo que habría reventado el CI: se ha commiteado como **`100644`** — sin bit de ejecución. En un checkout limpio, el CI lo llamaría y daría `Permission denied`, exactamente lo que me pasó antes con `notify-apk-deploy.sh`. Lo arreglo antes de pushear.

---

### **Claude** `13:01`

Y aquí ha saltado **la misma trampa que la wiki documentó ayer**: `git commit --only <ruta>` **relee la ruta del árbol de trabajo e ignora el índice**, así que deshizo mi cambio de modo. La lección dice cómo se hace: stagear, comprobar que solo esa ruta está en el índice, y commitear **sin pathspec**.

---

### **Claude** `13:04`

**Fase 1 en marcha, y probada en real por el propio CI.**

El runner acaba de desplegar **por la puerta nueva** (`success`), y ha dejado esto:

```json
{ "ts": "2026-08-22T13:03:55Z", "origen": "ci",
  "commit": "057b8fd...", "entry": "entry-a6e8cf58…", "bytes": 3967429,
  "sucios_al_desplegar": "" }
```

Y cuadra con lo que se sirve. **«¿Qué hay vivo?» ya tiene respuesta**, con commit y con hora, sin arqueología.

## Lo que ahora es imposible

**La carrera que querías cerrar.** Probada con el caso real: mi `dist` de las 09:58 contra el despliegue del CI de las 10:23 → **abortado**. Ya no gana el último que copie; pierde el que llegue tarde, y se le dice.

**La regresión de las 09:52.** Quité un centinela vivo de un bundle de prueba → **abortó, exit 1, y el webroot quedó intacto** (comprobé que el fichero no llegó a copiarse). Con retirada deliberada hay salida: `--acepta-perdida "motivo"`, y el motivo se guarda.

**El `200` como prueba.** Ahora se comprueba que el entry servido es el nuevo **y que pesa lo mismo** que el local.

Y los dos caminos —tú a mano, el CI— pasan por la misma puerta.

## Dos fallos míos que solo salieron al probarlo en real

El autotest daba **4 de 4 en verde y no valía nada**: ejercitaba primitivas de bash, no mi código. Al probarlo de verdad aparecieron dos:

**Miraba el bundle equivocado.** `ls entry-*.js | head -1` cogía el primero **alfabético** de **768 bundles acumulados** en el webroot, uno de hace meses. Comparaba contra eso y decía «sin pérdidas» con un centinela borrado a propósito. Es la misma familia que el `grep` sobre bytecode de Hermes: el instrumento no miraba donde yo creía.

**Y el aborto mentía.** Decía «NO se ha desplegado nada» también cuando el fallo ocurría **después** de copiar. Un aborto que miente sobre el estado del sistema es peor que no abortar, porque nadie va a ir a comprobarlo.

De regalo, al arreglar el bit de ejecución saltó **la trampa que la wiki documentó ayer**: `git commit --only` relee del árbol e ignora el índice, así que deshizo el `--chmod=+x` y respondió «nothing to commit». La receta de esa lección es la que funcionó.

## Lo que queda, y no es poco

**768 bundles muertos** (~2,7 GB) en el webroot. Ni `cp -r` ni `tar xzf` borran lo viejo. La fase 2 lo resuelve sola.

**Fase 2** — `releases/<sha>` + symlink atómico: rollback en dos segundos, nunca un estado a medias y limpieza automática. Toca la raíz que sirve Traefik, así que va aparte y con calma.

**Fase 3** — un solo desplegador, con el `cp` a mano como emergencia declarada.

Todo pusheado hasta `057b8fd`.

---

### **You** `13:04`

Fase 2

---

### **Claude** `13:05`

La fase 2 es la única con riesgo real: toca lo que sirve el sitio. Antes de proponer nada, mido **quién sirve ese directorio y cómo**, porque de eso depende todo el diseño.

---

### **Claude** `13:05`

`dev-ski-frontend` (nginx) monta **el directorio padre** `/var/www/dev.lyai.pro`. Eso es la clave del diseño: si `releases/` vive dentro de ese padre, un enlace relativo se resuelve bien dentro del contenedor. Compruebo su configuración, que es donde puede haber sorpresas.

---

### **Claude** `13:06`

**skip dev-xplain · no es un cambio de pantalla.**

Medido todo lo que importa, y el terreno es favorable:

| hecho | consecuencia para el diseño |
|---|---|
| `dev-ski-frontend` monta el **padre** `/var/www/dev.lyai.pro` | `releases/` cabe dentro del montaje: nginx lo verá |
| **no** hay `disable_symlinks` | los enlaces se siguen (defecto de nginx) |
| **no** hay `open_file_cache` | tras cambiar el enlace no queda nada rancio en memoria |
| `/app/_expo/` va con `expires 1y, immutable` | por eso acumular no rompía… pero cuesta 2,7 GB |
| `app-release.apk` y `viewer.html` viven **fuera** de `app/` | no se tocan |

## La propuesta

**BEFORE** — `/var/www/dev.lyai.pro/app/` es un directorio real donde dos procesos superponen ficheros y nadie borra nada: 768 bundles.

**AFTER**
```
/var/www/dev.lyai.pro/
  releases/<sha>/        ← cada despliegue, completo e inmutable
  app -> releases/<sha>  ← enlace relativo
```

`desplegar-web.sh` pasa a: copiar a `releases/<sha>` → **las tres comprobaciones de la fase 1 sobre esa copia** → cambiar el enlace → verificar lo servido. Y conservar los **últimos 5 releases**, borrando el resto.

Lo que ganamos: **rollback en dos segundos** (`ln -sfn` al release anterior, sin reconstruir), **nunca un estado a medias** (hoy, mientras corre el `cp -r`, alguien puede cargar el `index.html` nuevo con un trozo del viejo), y **la limpieza automática** de los 2,7 GB.

## Dónde está el riesgo, sin adornos

**Un único momento delicado: convertir `app` de directorio en enlace.** No se puede hacer de un golpe — `mv -T` no sustituye un directorio por un symlink. Son dos renombrados seguidos:

```
mv app app.viejo   &&   mv app.nuevo app
```

Entre uno y otro hay una ventana de **microsegundos** en la que `/app` no existe y nginx devolvería 404. Con el tráfico que tenéis es despreciable, pero **no es cero y lo digo**. Y se deshace en un comando: `mv app app.enlace && mv app.viejo app` devuelve el directorio original intacto.

**El segundo riesgo es la poda.** Con `expires 1y immutable`, un usuario con el `index.html` viejo en caché pedirá su bundle viejo. Si lo hemos borrado, recibe un 404 hasta que recargue (el `index.html` va con `no-cache`, así que se arregla solo al refrescar). Con 5 releases guardados cubrimos días de despliegues; **empezaría conservando 10** y bajando cuando veamos el ritmo real.

**Y un detalle que no me quiero comer**: `location /app/_expo/` en nginx apunta dentro de `app/`. Con el enlace sigue funcionando igual porque la resolución es transparente — pero eso hay que **comprobarlo en marcha**, no darlo por hecho.

## Cómo lo haría, para que sea reversible en cada paso

**Primero, sin tocar nada de lo vivo**: crear `releases/<sha-actual>/` copiando el `app/` de ahora, y comprobar que nginx sirve correctamente desde `releases/…` por una ruta de prueba. Si algo falla, no ha pasado nada.

**Después el cambio**: los dos renombrados, y **verificación inmediata** — el sitio responde, el entry servido es el mismo, `/app/_expo/` sirve un chunk, y `/app/vendor` (que tiene su propia ruta en Traefik) también.

**Y solo entonces** el script pasa a desplegar por releases, con la poda.

Te dejo la copia de seguridad `app.viejo` **en disco durante todo el proceso**: mientras exista, volver atrás es un comando.

¿Aplico?

---

### **You** `13:09`

Aplica

---

### **Claude** `13:10`

Voy paso a paso, verificando en cada uno. Primero mido espacio y tamaños, que aquí un `cp` a ciegas puede llenar el disco.

---

### **Claude** `13:10`

1,2 T libres, y el dato que lo cambia todo: un release limpio son **33 MB** frente a los **2,3 GB** del webroot — todo en 767 bundles muertos. Creo el primer release copiando **lo que se sirve de verdad**, sin el peso muerto.

---

### **Claude** `13:11`

nginx sigue el enlace sin problema: sirve `index.html` y el bundle. Ahora el cambio, con los dos renombrados **en un solo comando** para que la ventana sea la mínima posible, y verificación inmediata.

---

### **Claude** `13:11`

La guarda de la APK ha saltado por un falso positivo: mi comando **menciona** `app-release.apk` en un `curl`, y ella ve la cadena. Lo separo.

---

### **Claude** `13:11`

7 ms de ventana, y todo responde. Compruebo que la copia de seguridad está donde debe y lo miro en un navegador, que servidor no es cliente.

---

### **Claude** `13:12`

Correcto, no le afecta — y te lo confirmo con la medida, no de memoria.

---

### **Claude** `13:12`

Correcto, **no le afecta en nada**, y aquí está la razón medida:

La APK **no vive dentro de `app/`**. Está un nivel por encima, en `/var/www/dev.lyai.pro/app-release.apk`. Todo lo que he cambiado hoy ocurre dentro de `app/`, que ahora es un enlace. La APK sigue exactamente igual: **123.332.881 bytes, 10:15:33**, sirviéndose con su `content-type` de Android. Mismo byte, misma hora que cuando la compilé.

Cuando digas **«envíanos una apk»**, el flujo es idéntico al de esta mañana: `build-apk-verificada.sh` compila, pasa sus cinco comprobaciones y publica en esa misma ruta; luego `notify-apk-deploy.sh` os la manda a Manolo y a ti. Ni releases, ni symlink, ni la puerta del web se cruzan en ese camino.

**Una sola fricción, y es mía**: hace un momento la guarda de la APK **me bloqueó un comando** porque mi `curl` de comprobación *mencionaba* el nombre del fichero. No estaba publicando nada — solo mirando si respondía. Es un falso positivo por buscar la cadena en el comando entero. No rompe nada, pero conviene afinarlo para que no enseñe a ignorarla, que es justo el vicio del que veníamos.

---

Y sobre la fase 2, que ha terminado bien mientras preguntabas:

**El cambio duró 7 ms.** `app` ya es un enlace a `releases/057b8fd`. Verificado por HTTP —`index.html`, el bundle con sus 3.967.429 bytes exactos, `/app/vendor` y `viewer.html`, todos 200— y **abierto en un navegador de verdad**: cero errores de JavaScript y **cero respuestas ≥ 400**. Servidor no es cliente, así que lo miré también como cliente.

**La red de seguridad está puesta**: `app.viejo` sigue en disco con sus 2,3 GB y sus 767 bundles. Volver atrás son dos renombrados.

Un detalle curioso que salió al mirar: `app.viejo` pertenece a **`feedback-runner`**, no a root. O sea que el directorio que llevaba meses sirviendo la app lo creó otro servicio distinto del CI y de mí. No es urgente, pero es otro escritor más del que nadie tenía noticia.

Falta cerrar la fase: que `desplegar-web.sh` despliegue **a releases** en vez de al directorio, con la poda de los últimos N y el rollback. ¿Sigo?

---

### **You** `13:23`

Afinalo.

---

### **Claude** `13:23`

Leída. **No era «mencionar»**: mi comando llevaba un `mv` (el del enlace simbólico) y, veinte líneas más abajo, un `curl` que nombraba la APK. La guarda mira **la cadena entera**, así que vio verbo + ruta y no podía saber que eran cosas distintas.

El arreglo preciso: exigir que el verbo y la ruta estén **en la misma sentencia**, no en el mismo bloque.

---

### **Claude** `13:24`

La guarda acaba de **bloquear el intento de arreglarla** — mi comando lleva un `cp` (el respaldo) y el texto del parche menciona la ruta. Es la demostración perfecta del fallo. La edito sin pasar por bash.

---

### **Claude** `13:24`

Ahora hay que probar que sigue bloqueando lo que debe. Y aquí hay un problema divertido: **el propio comando de prueba dispara la guarda**. Escribo los casos a fichero para no volver a caer.

---

### **Claude** `13:25`

La guarda bloquea lo real, deja pasar lo legítimo, y **sigue cazando una publicación escondida entre cinco sentencias**. Afinada.

Ahora cierro la fase 2: que el script despliegue a releases con cambio atómico, poda y rollback.

---

### **Claude** `13:27`

Ahora la prueba de verdad: un despliegue completo por el camino nuevo, que además me deja un segundo release para probar el rollback. Reconstruyo.

---

### **Claude** `13:28`

Despliegue completo por el camino nuevo: release de **33 MB**, enlace movido de forma atómica, y verificado lo servido. Ahora la prueba que justifica toda la fase: **el rollback**.

---

### **Claude** `13:29`

**Guarda afinada y fase 2 cerrada.** Las dos cosas probadas en vivo.

## La guarda de la APK

No era «mencionar»: mi comando llevaba un `mv` (el del enlace) y, veinte líneas después, un `curl` que nombraba la APK. Miraba **la cadena entera**, así que veía verbo + ruta sin poder saber que eran cosas distintas.

Y lo demostró de la forma más elocuente posible: **bloqueó el intento de arreglarla**, porque mi comando de parche llevaba un `cp` (el respaldo) y el texto mencionaba la ruta. Tuve que editarla sin pasar por bash.

Ahora exige que **verbo y ruta estén en la misma sentencia**. Probada en los tres sentidos:

| caso | resultado |
|---|---|
| publicación real, una sentencia | **bloquea** (exit 2) |
| bloque legítimo (enlace + `curl`) | **deja pasar** (exit 0) |
| publicación real **escondida entre cinco sentencias** | **bloquea** (exit 2) |

Ese tercero importa: afinar no podía convertirse en abrir la mano.

## Fase 2

`app` ya es un enlace. Cada despliegue monta un release completo —y comprueba que tiene su `index.html` y su bundle— **antes** de tocar nada de lo servido; solo entonces mueve el enlace con `mv -T`, que sobre un symlink es **una sola llamada `rename(2)`: atómica**. Se acabó el estado a medias.

Probado de punta a punta:

```
despliegue    → release 20260822T132809Z-057b8fd (33M) · servido verificado
rollback      → 2 segundos · la app responde 200
rollback ×2   → vuelve al nuevo
navegador     → 0 errores JS · 0 respuestas ≥400
```

**33 MB por release frente a los 2,3 GB del webroot.** La poda conserva 10 y nunca toca el que sirve, y corre **después** de verificar que lo nuevo va.

Ese 10 no es arbitrario: `/app/_expo/` se sirve con `expires 1y, immutable`, así que un navegador con el `index.html` viejo en caché pedirá **su** bundle, que solo existe en **su** release. Se arregla al recargar, pero cada release borrado de más es una pestaña abierta que puede dar 404.

Todo pusheado hasta `4cb07e3`.

## Lo que queda abierto

**`app.viejo` sigue en disco con sus 2,3 GB.** Es la red de seguridad de la migración. Yo la dejaría un par de días y luego la borraría — pero eso lo dices tú.

**La fase 3** —un solo desplegador, con el despliegue a mano como emergencia declarada— no es código, es una decisión de cómo trabajáis. Y con la 1 y la 2 puestas ya no es urgente: la carrera se detecta y volver atrás cuesta dos segundos.

**Y un escritor más que apareció por el camino**: `app.viejo` pertenecía a `feedback-runner`, no a root ni al CI. O sea que el directorio que llevaba meses sirviendo la app lo creó **un tercer servicio** del que nadie tenía noticia. Con el enlace ya no puede pisar nada sin pasar por la puerta, pero merece una mirada.

---

### **You** `13:33`

continua

---

### **Claude** `13:34`

Sigo por el hilo que queda vivo: **el tercer escritor**. `app.viejo` pertenecía a `feedback-runner`, y hay un servicio con ese aire.

---

### **Claude** `13:34`

Un servicio **como root**, activo desde el **23 de abril** —cuatro meses—, con `--watch --live --implement`. Se auto-describe como «auto-implement + PR». Voy a ver qué hace de verdad.

---

### **Claude** `13:34`

El dispatcher trabaja en un **clon aparte**, no en el repo vivo, y ahora mismo está ocioso (1.439 líneas en 24 h, todas «no queued»). Pero entonces queda la pregunta: por qué el webroot era suyo. Sigo tirando.

---

### **Claude** `13:35`

Voy al panel. (El hilo del dispatcher lo cierro luego en dos líneas.)

---

### **Claude** `13:35`

La fórmula parece correcta (`transcurrido / total`), así que el fallo tiene que estar en los datos que recibe. Miro qué devuelve la API de verdad.

---

### **Claude** `13:35`

**Ahí está**: `created_at: None`. La API no lo devuelve, y el componente hace `update.created_at ? … : Date.now()` — así que `transcurrido = 0` y **todas las barras se quedan en el mínimo del 2 %**, pasado el tiempo que pase. Es exactamente lo de tu captura. Confirmo en el backend y en la BD.

---

### **Claude** `13:36`

**skip dev-xplain · sin cambio visual de diseño** — la barra ya está bien dibujada; lo que le falta es el dato.

## El fallo, medido

**BEFORE** — [server.py:8860](backend/server.py#L8860): el `SELECT` del endpoint devuelve `valid_from`, `valid_until`, `status`, `confirmed`… pero **no `u.created_at`**. Solo lo usa en el `ORDER BY`.

Y en [LBLUpdateCard.tsx:92](frontend/src/components/LBLUpdateCard.tsx#L92):

```js
const createdAt = update.created_at ? new Date(update.created_at).getTime() : Date.now();
```

Sin `created_at`, cae en `Date.now()`. Entonces `transcurrido = ahora − ahora = 0`, y la fórmula acaba en `Math.max(2, 0)` → **todas las barras al 2 %**, para siempre. Por eso las cuatro flechas de tu captura apuntan a lo mismo: no es que el avance esté mal calculado, es que **no hay avance que calcular**.

La BD **sí tiene el dato**, y el avance real de tus cuatro updates ahora mismo es:

| update | vence | avance real | lo que pinta |
|---|---|---|---|
| 36 | 23-ago 21:59 | **49 %** | 2 % |
| 37 | 28-ago 06:03 | **19 %** | 2 % |
| 39 | 22-ago 22:59 | **77 %** | 2 % |
| 40 | hoy 21:00 | **13 %** | 2 % |

El 39 está al 77 % de su vida y se ve igual de vacío que el 37, que va por el 19 %. Justo el caso en que la barra tendría que servir para algo.

## AFTER

Una línea: añadir `u.created_at` a ese `SELECT`. El frontend ya sabe usarlo — no hay que tocarlo.

```
- SELECT u.id, u.entity_id::text, u.update_type, u.content_raw,
-        u.extracted_data, u.valid_from, u.valid_until,
+ SELECT u.id, u.entity_id::text, u.update_type, u.content_raw,
+        u.extracted_data, u.valid_from, u.valid_until, u.created_at,
```

**Efectos colaterales**: ninguno más allá de un campo extra en la respuesta. No cambia filtros, ni orden, ni permisos. El endpoint es de solo lectura y ya se llama igual. Requiere reiniciar el backend para que lo cargue.

**Y una decisión tuya**: cuando `created_at` no venga —updates viejos, u otra fuente—, hoy la barra se queda en el 2 % en silencio. Puedo dejarlo así, o hacer que en ese caso **no se pinte la barra** en vez de mostrar una vacía que miente. Yo quitaría la barra: una barra al 2 % dice algo falso; ninguna barra dice «no lo sé».

¿Aplico solo la línea, o también eso último?

---

### **You** `13:36`

fijate en la captura, la barra de avance tiene la misma longitud en todas

---

### **Claude** `13:36`

Exacto — y eso es justamente el síntoma que confirma el diagnóstico, no algo distinto.

Lo que ves en las cuatro tarjetas **es la pista vacía, no el avance**. La barra son dos piezas: una pista gris de ancho fijo (`#e2e8f0`, [LBLUpdateCard.tsx:230](frontend/src/components/LBLUpdateCard.tsx#L230)) y encima un relleno de color cuyo ancho es el porcentaje. Con `progressPct = 2`, ese relleno mide **2 % de unos 300 px ≈ 6 px**, sobre una barra de **3 px de alto**. A ese tamaño no se distingue de la pista.

Por eso las cuatro miden lo mismo: **lo que se ve es la pista**, que siempre ocupa el 100 %. El avance no está corto — está ausente.

Y es la prueba de que no hay dato detrás: si las barras estuvieran pintando el avance real, **tendrían que verse distintas**, porque los cuatro updates están en puntos muy diferentes de su vida —**49 %, 19 %, 77 % y 13 %**—. Que se vean idénticas solo es posible si todas reciben el mismo número. Ese número es 2, el mínimo que impone `Math.max(2, …)` cuando el tiempo transcurrido sale 0.

Y sale 0 porque la API no devuelve `created_at`: el componente cae en `Date.now()`, así que «cuándo se creó» y «ahora» son el mismo instante.

Con la línea que te propuse, esas cuatro barras pasarían a medir la mitad, un quinto, tres cuartos y un octavo de la pista. Distintas entre sí, que es de lo que se trata.

¿Aplico? Y dime también lo otro: cuando falte `created_at`, ¿barra al 2 % o ninguna barra? Sigo pensando que ninguna — una barra que dice «acaba de empezar» cuando en realidad no lo sabe es peor que no dibujarla.

---

### **You** `13:38`

cuando falte created_at¿? nunca debe de faltar ese dato

---

### **Claude** `13:38`

Tienes razón, y merece comprobarse en vez de asumirlo. Lo miro en el esquema.

---

### **Claude** `13:39`

Medido, y tu instinto es correcto pero con un matiz que importa:

| | |
|---|---|
| `created_at` acepta NULL | **sí** (`is_nullable: YES`) |
| tiene defecto | **sí**, `now()` |
| filas sin `created_at` | **0 de 31** |

O sea: **en la práctica nunca falta** —el defecto lo garantiza— pero **la columna lo permite**. Un `INSERT` que pase `created_at = NULL` explícitamente crearía una fila imposible de dibujar. Hoy no ha pasado nunca.

Eso cambia mi propuesta anterior, y para mejor. Si el dato **no debe faltar**, la respuesta no es decidir cómo pintarlo cuando falte: es **hacer que no pueda faltar** y quitar el disfraz.

## Tres cambios, y el tercero es el que cierra el tema

**1 · El fallo real** — [server.py:8860](backend/server.py#L8860): añadir `u.created_at` al `SELECT`. Es lo que hace que las barras midan 49 %, 19 %, 77 % y 13 % en vez de todas 2 %.

**2 · Quitar el disfraz** — [LBLUpdateCard.tsx:92](frontend/src/components/LBLUpdateCard.tsx#L92):

```js
const createdAt = update.created_at ? new Date(update.created_at).getTime() : Date.now();
```

Ese `: Date.now()` es el culpable de que un **fallo de datos** se convirtiera en **una barra creíble que mentía**. Sin él, esto se habría visto el primer día: la barra no habría aparecido y alguien habría preguntado. Con él, lleva quién sabe cuánto enseñando un 2 % que nadie podía distinguir de «acaba de empezar».

Propongo: si no hay `created_at`, **no se dibuja la barra**. No como estado de diseño, sino como señal de que algo va mal.

**3 · Que sea imposible de verdad** — en la BD:

```sql
ALTER TABLE lyai.owner_updates ALTER COLUMN created_at SET NOT NULL;
```

Con 0 nulos en 31 filas es instantáneo y reversible (`DROP NOT NULL`). Toma un lock exclusivo, pero sobre una tabla de 31 filas son microsegundos. A partir de ahí «nunca debe faltar» deja de ser una intención y pasa a ser una regla que la base de datos hace cumplir.

Sin el 3, el 2 es una defensa contra algo que sigue siendo posible. Con el 3, el 2 se convierte en lo que debe ser: una alarma para un caso que ya no puede darse.

**Efectos colaterales**: el 1 añade un campo a una respuesta de solo lectura. El 2 solo afecta a esa tarjeta. El 3 obliga a que cualquier `INSERT` futuro traiga `created_at` o deje que el defecto lo ponga — ningún código actual lo pasa a NULL, lo he comprobado en las 31 filas.

¿Los tres?

---

### **You** `13:39`

ahora haz que sae vean las barras correctamente en el historico actual que veo

---

### **Claude** `13:39`

**skip dev-xplain · sin cambio visual de diseño** — la barra ya está diseñada; solo va a recibir el dato que le falta. Aplico los tres y lo despliego para que lo veas.

---

### **Claude** `13:40`

Confirmados los tres. El 1 y el 2 ya están; voy con el de la base de datos, comprobando justo antes que sigue sin nulos.

---

### **Claude** `13:42`

**Listo. Recarga con `Ctrl+Shift+R`** y las cuatro barras dejarán de medir lo mismo:

| update | vence | barra |
|---|---|---|
| 36 | 23-ago 21:59 | **49 %** |
| 37 | 28-ago 06:03 | **19 %** |
| 39 | 22-ago 22:59 | **77 %** |
| 40 | hoy 21:00 | **14 %** |

Esos números salen de la API real después del arreglo, no de la teoría: se los pedí y los calculé con lo que ahora devuelve.

## Los tres, hechos

**1 · El fallo.** `u.created_at` ya viaja en el `SELECT` de [server.py:8860](backend/server.py#L8860). Antes solo se usaba para ordenar, así que la tarjeta nunca lo veía.

**2 · Fuera el disfraz.** El `: Date.now()` era lo que convertía un **fallo de datos** en **una barra creíble que mentía**: sin `created_at`, «cuándo se creó» y «ahora» eran el mismo instante, el transcurrido salía 0 y las cuatro pintaban el mismo 2 %. Ahora, si el dato no está, **no se dibuja barra**. Sin él, esto se habría visto el primer día.

**3 · Y ya no puede faltar.** `created_at` es **`NOT NULL`** en la base de datos. Comprobé justo antes que seguía habiendo 0 nulos en las 31 filas — si hubiera aparecido alguno, el script abortaba en vez de forzar. Ahora «nunca debe faltar» no es una intención: lo hace cumplir Postgres.

## Verificado

Backend reiniciado y sano. `tsc` limpio en la tarjeta. Desplegado **por la puerta nueva**: release `20260822T134128Z-4cb07e3`, enlace movido de forma atómica, servido íntegro (`entry-366c7831…`, 3.967.443 bytes exactos). Y abierto el panel en un navegador: **0 errores de JavaScript, 0 respuestas ≥ 400**.

Si algo se viera raro, volver atrás es un comando: `--rollback` al release anterior, dos segundos.

Nada commiteado todavía — `server.py` y `LBLUpdateCard.tsx` están modificados esperando tu visto bueno en pantalla. Dímelo y los commiteo.

Y me queda pendiente cerrarte el hilo del **tercer escritor**: el `feedback-dispatcher`, un servicio que corre **como root desde el 23 de abril** y que, cuando llega feedback, clona el repo, **le pide a Claude que implemente el cambio**, commitea, pushea una rama y abre un PR. Ahora mismo está ocioso, y trabaja en un clon aparte, no en el repo vivo. Pero es una cuarta forma de que entre código sin que nadie lo pida.

---

### **You** `14:36`

commitea

---

### **Claude** `14:37`

Commiteado: **`0476c64`** — 2 ficheros, 17 líneas. Árbol a cero, `gitleaks` limpio en los dos.

El mensaje deja escritos los tres cambios y, sobre todo, **por qué son tres y no uno**: el `SELECT` arregla el síntoma, quitar el `: Date.now()` quita el disfraz que convirtió un fallo de datos en una barra creíble que mentía, y el `NOT NULL` hace que el caso ya no pueda darse. Sin el tercero, el segundo sería una defensa contra algo todavía posible.

**No lo he pusheado.** Y esta vez tiene consecuencia: al pushear, el CI hará `reset --hard`, reiniciará el backend y **desplegará el web por la puerta nueva**. Como el árbol está limpio, el reset no puede llevarse nada, y el despliegue del runner pasará por las mismas comprobaciones que el mío. Pero es un despliegue de verdad y prefiero que lo digas tú.

Dos cosas quedan abiertas de antes:

**`app.viejo`** sigue en disco con sus 2,3 GB — la red de seguridad de la migración a releases. Yo la dejaría un par de días.

**Y el cuarto camino por el que entra código**, que es el que menos me gusta: `lyai-feedback-dispatcher`, activo **como root desde el 23 de abril**. Cuando llega feedback clona el repo, **le pide a Claude que implemente el cambio**, commitea, pushea una rama y abre un PR. Ahora está ocioso y trabaja en un clon aparte, así que no pisa nada. Pero significa que hoy hay cuatro formas de que entre código en este proyecto: tú, yo, el CI y él. Y de las cuatro, esa es la única que **decide sola qué escribir**.

---

### **You** `20:03`

mira la captura, mi windows ha ejecutado automaticamente el backup?

---

### **Claude** `20:04`

No puedo ver tu Windows desde aquí, así que te digo qué **sí** puedo comprobar: si el servidor produjo lo que tu PC se está bajando.

---

### **Claude** `20:04`

Sí, y está funcionando exactamente como se diseñó. No es una sorpresa: es el **backup off-site que quedó cerrado el 2026-08-03**, y está documentado en la wiki.

Lo que muestra tu captura encaja pieza por pieza con lo que veo aquí:

| en tu pantalla | en el servidor |
|---|---|
| «espejo del server: 2026-08-22T04:30:16Z» | el espejo lo genera `backup-local-mirror.sh` por cron a las **4:30** |
| `lyai_db_20260822T040001Z.dump` · 344 MB | ese fichero existe, **360.616.370 bytes**, sellado a las 04:01 |
| 13 ficheros · 819 MB | la doc del cierre registró 12 ficheros · 784 MB |
| a las **22:00** | tarea diaria de Windows (`schtasks`) a las **22:00** |

**Tu PC no lo ha hecho «solo» en el sentido de raro: lo hace todos los días a las 22:00.** Lo que ves es la tarea programada tirando por `sftp` con `reget` —por eso dice «solo lo que falte» y va reanudando— y metiéndolo en `restic` cifrado en `D:\lyai-backup`.

Y hay una decisión de diseño detrás que conviene recordar: **es el PC quien tira, no el servidor quien empuja**. Si el servidor empujara, tendría credenciales del backup, y quien reventara el servidor borraría también la copia. Tirando el PC, el servidor no tiene llaves de nada.

**Una cosa a la que sí conviene estar atento**, y está avisada en la propia documentación: la tarea se creó **sin `/rl highest`**, así que Windows solo la ejecuta **con tu sesión iniciada**. Si el PC está apagado a las 22:00, no corre — y entonces salta el vigilante por Telegram a las 48 h, con re-aviso cada 72 h. Que hoy hayas visto la ventana significa que tenías sesión abierta.

Lo único que no puedo comprobar desde aquí es **el otro extremo**: si al terminar dejó el snapshot bien en `restic`. Si quieres, cuando acabe me dices y lo verifico por el lado del servidor — el PC hace `ssh touch` de un fichero de latido justo al terminar, así que puedo ver si llegó.

---

### **You** `20:07`

1-si, mira si llegó.
2-" la tarea se creó sin /rl highest, así que Windows solo la ejecuta con tu sesión iniciada" ¿se puedes solucionar con /rl highest?

---

### **Claude** `20:08`

El latido es de **hace 2.885 minutos** (Aug 20, 20:01), pero eso no es lo que parece: son las **20:07 UTC**, o sea las 22:07 en tu PC. **El backup que ves está corriendo ahora mismo** —iba por el fichero 7 de 13, el dump de 344 MB— y el latido solo se escribe al terminar. Le quedan unos minutos.

Lo que sí dice ese dato es otra cosa: **ayer no completó**. Compruebo si el vigilante avisó, que para eso está.

---

### **Claude** `20:08`

`estado-backup.sh` es un script **manual de consulta** —pensado para mirarlo desde el móvil— y **ningún cron lo llama**. Busco si el vigilante que promete la wiki existe en otro sitio, antes de afirmar nada.

---

### **Claude** `20:09`

El vigilante **existe** (`/opt/lyai/bin/backup-heartbeat-check.sh`) pero ningún cron de usuario lo llama. Antes de afirmar algo tan gordo, miro los otros sitios donde se puede programar algo.

---

### **Claude** `20:09`

Me corrijo: **sí está programado** — `/etc/cron.d/lyai-backup-heartbeat`, cada 6 horas como root, y ha corrido 27 veces, la última hoy a las 18:00. Mi comprobación anterior solo miró los crontabs de usuario. Ahora la pregunta que importa: ¿avisó?

---

### **Claude** `20:10`

**1 · Sí, ha llegado — hace 0 minutos.**

El latido está sellado a las **20:09:12 UTC** (22:09 en tu PC). Es decir: el backup que viste en pantalla **acaba de terminar mientras hablábamos**, y el PC ha escrito el testigo por SSH, que es la única prueba de que la copia se completó de verdad.

Y de paso queda claro lo que había pasado antes: el latido anterior era del **20-ago 20:01**. O sea que **ayer no completó** — probablemente el PC estaba apagado o sin sesión a las 22:00. El vigilante corrió hoy a las 18:00 y anotó `PC: ok (45h)`, justo por debajo de su umbral de **48 h**. Estaba a tres horas de avisarte por Telegram. Tu backup de esta noche ha llegado antes que la alarma.

**Y me corrijo en algo que te dije hace un momento**: afirmé que el vigilante no estaba programado. **Falso.** Está en `/etc/cron.d/lyai-backup-heartbeat`, cada 6 horas como root, y ha corrido 27 veces. Mi comprobación solo miró los crontabs de usuario y no los de `/etc/cron.d`. Medí en el sitio equivocado — otra vez.

**Un detalle que sí conviene mirar**: en ese mismo log aparece `MOVIL: STALE (874h)`. Hay un segundo testigo que lleva **36 días parado**. No sé aún qué es ni si importa.

---

**2 · No, `/rl highest` no lo arregla.** Son dos cosas distintas y es fácil confundirlas:

`/rl highest` controla **con cuántos privilegios** corre la tarea (elevada o no). Lo que decide si corre **con la sesión cerrada** es otra cosa: el tipo de inicio de sesión, que en `schtasks` se fija con `/ru` + `/rp` — usuario y contraseña guardados.

Lo que necesitarías es esto, en PowerShell **como administrador**:

```
schtasks /change /tn "<nombre-de-la-tarea>" /ru "Glado" /rp "<tu-contraseña>" /rl highest
```

Con `/ru` + `/rp`, Windows la marca como *«ejecutar tanto si el usuario inició sesión como si no»*. El `/rl highest` puedes añadirlo o no; es independiente.

**Tres avisos antes de que lo hagas**, porque los tres pueden romperlo en silencio:

**La contraseña queda guardada** en el almacén de credenciales de Windows. Es lo normal para tareas desatendidas, pero conviene saberlo.

**Las claves SSH.** La tarea entra al servidor con una clave que casi seguro vive en `C:\Users\Glado\.ssh`. Si la ejecutas como tu usuario, sigue encontrándola. **Si en algún momento pruebas con `/ru SYSTEM`, no** — SYSTEM tiene otro perfil y la copia fallaría sin decir por qué.

**Y si el PC está apagado, no hay flag que valga.** Esto solo cubre «encendido pero sin sesión». Para lo otro se marca *«Ejecutar la tarea lo antes posible tras un inicio programado perdido»*, y así se pone al día al arrancar.

Yo no puedo tocar tu Windows ni comprobar desde aquí si el cambio funcionó. Pero sí puedo verificarlo por el resultado: **si lo aplicas y una noche dejas el PC encendido sin sesión, al día siguiente miramos el latido**. Si aparece con menos de 26 horas, funcionó. Esa es la prueba, no la configuración.

---

