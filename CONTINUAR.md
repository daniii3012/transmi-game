# Continuidad — Transmi 2D

Actualizado: 11 septiembre de 2026. Leer README.md, docs/OPERACION_Y_DATOS.md y docs/VALIDACION_20260911.md. El checkpoint previo a la revisión de Daniel es `c0ed10116fbf708b13b96f7dcceada9a4e4ddd44`, verificado y subido antes de implementar sus observaciones. Esta revisión continúa ese trabajo; no reiniciar la arquitectura.

## Proyecto y autorizaciones

Repo: `/Users/daniel/Documents/Codex/2026-09-08/ho/outputs/BogotaTransmi`, rama main, remoto `https://github.com/daniii3012/transmi-game.git`. Push autorizado. Simulador 2D geográfico 1:1 de troncales y duales; zonales/cable fuera, conducción 3D pausada en archive/transmi3d. Diseño inspirado en Subway Builder/Mini Metro, sin construcción. No son posiciones GPS en vivo.

Estimaciones ajustables y QA de navegador autorizadas; dos carriles por sentido como abstracción y paso expreso independiente de atención. Daniel autorizó servir por LAN, pero no publicar una versión jugable en internet. Investigación acotada con agentes ligeros autorizada por AGENTS; la investigación de plataformas terminó. No hay agentes ni tareas automáticas pendientes que esperar.

## Ejecutar y desarrollar

- Fuentes estáticas editables `app/dist`, Three.js 0.186.0 local y cámara ortográfica. No hace falta npm ni bundler.
- `ABRIR_SIMULACION_2D.command`: loopback `http://127.0.0.1:8766/`.
- `ABRIR_EN_RED_LOCAL.command`: escucha LAN en puerto 8767; imprime IP actual. Ambos sirven solo app/dist, no-store, sin listar directorios. Mantener Terminal abierta. Cada navegador tiene su propia simulación.
- Python geográfico: `../../work/venv/bin/python`, con shapely/pyproj. Python del sistema sirve la web pero no trae esas bibliotecas. Node en PATH.
- `work/` está ignorado. ZIP de validaciones en la carpeta work/passengers de la tarea original, fuera del repo. Nunca añadir transacciones crudas a Git. El agregado versionado basta para reproducir.
- `web/transmi2d` es compatibilidad histórica. No confundirlo con otra aplicación.

## Estado después de las observaciones

137 registros: 114 utilizables de 103 códigos, 23 pendientes. El jueves inicial 10 sep. hay 112 variantes con ventanas. El mapa bruto tiene 116 registros/100 códigos, no 116 rutas únicas. C15 zonal/366 excluida; C15/3915 y H15/367 troncales tienen 19 paradas. F23/10082 Banderas excluida por indicación de Daniel; se conserva F23/396 Portal Américas. **Los 23 pendientes, incluido K86 completo/629, deben permanecer pendientes por ahora.** No confundirlo con aeropuerto/5316.

- Reloj, calendarios/festivos colombianos, medianoche, demanda pico/valle, geometría métrica, curvas, aceleración y frenado integrados. Motor por eventos en worker; recorridos y reservas reproducibles al retroceder.
- Capacidad fija 80/160/240 y tamaño fijo por ruta. Fáciles 1–8 articuladas, M51/F51 biarticuladas por usuario; F63/Z63 dual articulado eléctrico publicado. Otros duales padrón; otros servicios ≥18 km biarticulados y menores articulados, hipótesis documentada, no verificación de flota.
- Cruceros 60 troncal/50 calle, variación por vehículo −5/−2/0/+2/+5. Los buses frenan en curvas/paradas; calle en pico factor 0,82.
- Nuevo 1× de demanda = 2,25 del modelo previo. Referencia histórica sin modificar: 1.920.298 entradas del archivo 9 sep. (14 después de medianoche), 1.920.297 enlazadas a 142 estaciones, una de cable excluida. OD, descensos, direcciones y abandono medio 30 min estimados. Denegaciones son oportunidades repetidas, no personas únicas.
- Salidas 4/8 min, variación opcional ±12%; refuerzos limitados a una minoría de salidas pico con presión estimada alta, intercalados a 120 s. Reutilización de vehículos por terminal/tipo; patios operativos abstractos, sin circulación en vacío.
- Fondo: solo troncales de color. Tramos tipo_tra=2 (Séptima exterior y otras extensiones) y segmentos de calle de duales son grises discontinuos. Geometría exacta aparece al seleccionar servicio o bus; atenuada al seguirlo.
- OSM físico en seis estaciones: Sur, Suba, Américas, Banderas, Ricaurte y Jiménez. Plataformas explícitas en los primeros cuatro; cubiertas/accesos en los intercambiadores. `station-layouts.mjs` estima 114 visitas compatibles sobre rutas existentes (una visita de Jiménez conserva referencia oficial). No crea conexiones ni redirige por vías OSM. Otros andenes siguen esquemáticos. Puentes/túneles tienen contexto OSM etiquetado, sin auditoría exhaustiva de niveles.
- Exploración Ruta separada del alcance operativo. Solo los botones de simular cambian servicios. Al volver a red se conserva hora y estado de reproducción. Cambiar de pestaña limpia ruta visual. Seleccionar otro bus actualiza su ruta; final de viaje vuelve a detalle de ruta.
- Seguimiento interpolado en distancia sobre la polilínea más cámara suavizada cada frame. Zoom de rueda/pinch más sensible. Clusters se reposicionan también al mover cámara en pausa.
- Slider protegido durante arrastre, respuestas del worker numeradas, botón Ahora (Bogotá), modo oscuro persistente, fuentes propias y notas de archivo al final de estación. No hay filtro Duales ni notas de una ruta particular en Operación.
- Guardado v3, restaurado pausado. Se lee v2 si falta v3: conserva fecha/hora/alcance y parámetros compatibles, migra antiguos cruceros por defecto 48/30 a 60/50 y elimina mezcla/capacidad configurables. F23 antiguo se redirige a 396.

## Reproducir y validar

Fuentes de servicios: data/raw/services/20260910T185326Z + supplement_20260910, curación data/curated/services.json. OSM de estaciones: data/raw/station_layouts/20260911T025000Z (consulta real 2026-09-11T06:05:06Z, base OSM reportada 2026-06-01). La carpeta es identificador de captura, no la hora de consulta.

`build_services.py`, `build_context.py`, `build_station_layouts.py` usan Python geo; `import_passenger_profiles.py` usa agregado existente. Scripts de descarga separados; no actualizar fuentes silenciosamente.

35 pruebas Node y 3 Python pasaron. Benchmarks guardados: referencia 896 buses máximos muestreados, 68 esperando atención en toda la red, ~4,48 s preparación / 0,43 ms muestreo / 370 MB heap; estrés 2/3 min y demanda3: 2.403 buses muestreados, 820 en espera, ~9,03 s / 2,15 ms / 824 MB. El máximo exacto por eventos es 904/2.407 e incluye día previo. Es CPU Node, no FPS. El estrés puede congestionarse: no se oculta eliminando vehículos.

QA de escritorio en navegador incluye las seis estaciones, capas, F23, C15/H15, selección de otro bus, seguimiento/fin de viaje, cambios de alcance, reloj/arrastre/Ahora, temas, fuentes, guardado y URL LAN. Sin errores de consola. No se ha certificado pinch físico, móviles reales ni cada geometría de ruta. Ver informe de validación.

## Pendientes consentidos

23 registros de datos; asignaciones oficiales ruta/tipo/vagón, más planos, patios/inventarios/vacíos; calibración con OD y varios días; revisión exhaustiva de cruces/obras. Semáforos opcionales aplazados porque faltan fases y coordinación fiables. Mantener estas incertidumbres visibles y enlazadas desde la app. Nuevas observaciones del usuario deben incorporarse sobre esta versión.

Antes de terminar cada hito, verificar diff, commit/push y coincidencia HEAD local/remoto. Los informes del 10 sep. se conservan como evidencia histórica, no resultados actuales.
