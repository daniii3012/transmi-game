# Continuidad — Transmi 2D

Actualizado: 11 septiembre de 2026. Leer README.md, docs/OPERACION_Y_DATOS.md y docs/VALIDACION_FASE2_20260911.md. El checkpoint de la primera revisión es `f6fa207e3830ef75979640caf8ab9af4c64feac8`, verificado y subido antes de esta segunda revisión. La segunda revisión integra todos los portales, semáforos corroborados, planificador y etiquetas fluidas. No reiniciar la arquitectura.

## Proyecto y autorizaciones

Repo: `/Users/daniel/Documents/Codex/2026-09-08/ho/outputs/BogotaTransmi`, rama main, remoto `https://github.com/daniii3012/transmi-game.git`. Push autorizado. Simulador 2D geográfico 1:1 de troncales y duales; zonales/cable fuera, conducción 3D pausada en archive/transmi3d. Diseño inspirado en Subway Builder/Mini Metro, sin construcción. No son posiciones GPS en vivo.

Estimaciones ajustables y QA de navegador autorizadas; dos carriles por sentido como abstracción y paso expreso independiente de atención. Daniel autorizó servir por LAN, pero no publicar una versión jugable en internet. Investigación acotada con agentes ligeros autorizada por AGENTS; la investigación de plataformas terminó. La captura semafórica se revisó y completó localmente después de que el agente alcanzara su límite; no hay trabajo pendiente que esperar de agentes ni automatizaciones.

## Ejecutar y desarrollar

- Fuentes estáticas editables `app/dist`, Three.js 0.186.0 local y cámara ortográfica. No hace falta npm ni bundler.
- `ABRIR_SIMULACION_2D.command`: loopback `http://127.0.0.1:8766/`.
- `ABRIR_EN_RED_LOCAL.command`: escucha LAN en puerto 8767; imprime IP actual. Ambos sirven solo app/dist, no-store, sin listar directorios. Mantener Terminal abierta. Cada navegador tiene su propia simulación.
- Python geográfico: `../../work/venv/bin/python`, con shapely/pyproj. Python del sistema sirve la web pero no trae esas bibliotecas. Node en PATH.
- `work/` está ignorado. ZIP de validaciones en la carpeta work/passengers de la tarea original, fuera del repo. Nunca añadir transacciones crudas a Git. El agregado versionado basta para reproducir.
- `web/transmi2d` es compatibilidad histórica. No confundirlo con otra aplicación.

## Estado después de las observaciones

137 registros: 117 utilizables de 105 códigos, 20 pendientes. El jueves inicial 10 sep. hay 115 variantes con ventanas. El mapa bruto tiene 116 registros/100 códigos, no 116 rutas únicas. C15 zonal/366 excluida; C15/3915 y H15/367 troncales tienen 19 paradas. F23/10082 Banderas excluida por indicación de Daniel; se conserva F23/396 Portal Américas. **Los 20 pendientes deben permanecer pendientes por ahora.** E48/12444, H76/1213 y K86 completo/629 salieron de esa lista el 11 sep. al reimportar su detalle publicado; los demás siguen sin trazado o con calendario Ciclovía ambiguo. No confundirlo con aeropuerto/5316.

- Reloj, calendarios/festivos colombianos, medianoche, demanda pico/valle, geometría métrica, curvas, aceleración y frenado integrados. Motor por eventos en worker; recorridos y reservas reproducibles al retroceder.
- Capacidad fija 80/160/240 y tamaño fijo por ruta. Fáciles 1–8 articuladas, M51/F51 biarticuladas por usuario; F63/Z63 dual articulado eléctrico publicado. Otros duales padrón; otros servicios ≥18 km biarticulados y menores articulados, hipótesis documentada, no verificación de flota.
- Cruceros 60 troncal/50 calle, variación por vehículo −5/−2/0/+2/+5. Los buses frenan en curvas/paradas; calle en pico factor 0,82.
- Nuevo 1× de demanda = 2,25 del modelo previo. Demanda medida sobre 17 días (24 ago.–9 sep. 2026, 28.014.777 validaciones): perfil horario por tipo de día en `hourly_by_day_type`, 13 días de semana, 2 sábados y 2 domingos. Factores medidos sábado 0,654 y domingo 0,302, frente a los 0,70/0,55 estimados que reemplazan; el domingo estaba sobreestimado ~80%. Entre días de semana la variación es 2,0%. OD, descensos, direcciones y abandono medio 30 min siguen estimados. Denegaciones son oportunidades repetidas, no personas únicas. Detalle en docs/DEMANDA_MULTIDIA_20260911.md.
- Salidas 4/8 min, variación opcional ±12%; refuerzos limitados a una minoría de salidas pico con presión estimada alta, intercalados a 120 s. Reutilización de vehículos por terminal/tipo; patios operativos abstractos, sin circulación en vacío.
- Calzada real de OSM dibujada bajo los corredores: 929 vías conservadas de 1.203 descargadas, 341 con carriles publicados y las demás dibujadas con un carril. Ancho carriles×3,5 m, tonos distintos para calzada exclusiva y compartida, visible al acercarse y apagable con el botón ═. Los buses siguen la polilínea publicada del servicio, no esta calzada; pueden separarse unos metros. Detalle en docs/CALZADAS_20260911.md.
- Fondo: solo troncales de color. Tramos tipo_tra=2 (Séptima exterior y otras extensiones) y segmentos de calle de duales son grises discontinuos. Geometría exacta aparece al seleccionar servicio o bus; atenuada al seguirlo.
- OSM físico en 40 estaciones: nueve portales, Banderas, Ricaurte y Jiménez, más las 28 troncales con más servicios. Hay 111 elementos de parada/plataforma, 98 áreas y 478 líneas internas; los 111 incluyen nodos, no son 111 plataformas físicas. Calle 72 - Areandina y Virrey - Cendiatra no tienen geometría en OSM. Norte tiene puntos/área, sin contorno de plataforma inventado. Las otras estaciones mantienen vagones esquemáticos.
- `station-layouts.mjs` sitúa 477 de 648 visitas compatibles sobre las polilíneas existentes; 171 conservan referencia oficial. La selección de estaciones se calcula con `--stations N` desde el catálogo, no a mano. No redirige ni une rutas por proximidad. Inventario en TODOS_LOS_PORTALES_20260911.md.
- Semáforos: 723 con evidencia nodal directa, 450 en calzada exclusiva y 273 en tramos de calle de los duales (Séptima, Av. 68). 669 asociados a las 117 variantes por distancia ≤12 m y sentido/eje, con 4.807 pares. Reglas compartidas en `tools/busway_criteria.py`; el camino de calle solo aplica donde el servicio deja la troncal. Ciclos estimados de 90 s (52 verde / 3 amarillo / 35 rojo), frenado métrico y espera reproducible, activados por defecto/desactivables en Operación. No coordinación ni colas microscópicas en cruces. Estado `signal` separado de cola de atención; ambos suman el indicador en espera.
- Planificador: toda la red utilizable, fecha/hora independientes, hasta dos transbordos y seis horas de horizonte. Calendarios publicados, frecuencias y tiempos nominales, caminatas estimadas entre puntos de una misma estación lógica. No predice fases ni aforo. Itinerario y geometría parcial en la pestaña Planear viaje. `planner.mjs`, mensajes `plan` del worker e IDs de solicitud.
- Exploración Ruta separada del alcance operativo. Solo los botones de simular cambian servicios. Al volver a red se conserva hora y estado de reproducción. Cambiar de pestaña limpia ruta visual. Seleccionar otro bus actualiza su ruta; final de viaje vuelve a detalle de ruta.
- Seguimiento interpolado en distancia sobre la polilínea más cámara suavizada cada frame. Las etiquetas conservan nodos DOM y transformaciones de posición en cada actualización de cámara; las colisiones se recalculan por separado. Zoom de rueda/pinch más sensible. Clusters se reposicionan también al mover cámara en pausa.
- Slider protegido durante arrastre, respuestas del worker numeradas, botón Ahora (Bogotá), modo oscuro persistente, fuentes propias y notas de archivo al final de estación. No hay filtro Duales ni notas de una ruta particular en Operación.
- Guardado v3, restaurado pausado. Se lee v2 si falta v3: conserva fecha/hora/alcance y parámetros compatibles, migra antiguos cruceros por defecto 48/30 a 60/50 y elimina mezcla/capacidad configurables. F23 antiguo se redirige a 396.

## Reproducir y validar

Fuentes de servicios: data/raw/services/20260910T185326Z + supplement_20260910, curación data/curated/services.json. OSM de estaciones: data/raw/station_layouts/20260911T120000Z, combina seis layouts previos con seis portales nuevos. OSM semáforos: data/raw/busway_signals/20260911T120000Z, 293 celdas más 639 XML detallados con hashes. Las carpetas son identificadores; las horas de consulta están en los manifiestos.

`build_services.py`, `build_context.py`, `build_station_layouts.py` usan Python geo; `import_passenger_profiles.py` usa agregado existente. Scripts de descarga separados; no actualizar fuentes silenciosamente.

56 pruebas Node y 3 Python pasaron. Benchmarks con semáforos de calzada y calle y demanda multidía: referencia 1.113 buses máximos muestreados, 71 esperando atención y 121 en semáforo; preparación 12,01 s, muestreo 1,30 ms, heap 560 MB. Estrés 2/3 min y demanda 3×: 3.303 buses, 1.441 esperando atención y 236 en semáforo; 21,00 s / 4,56 ms / 1.138 MB. Máximos exactos por eventos 1.118/3.337. CPU Node, no FPS; el estrés puede congestionarse, sin borrar vehículos.

QA de navegador: seis portales nuevos y anteriores conservados, transbordos/fecha independiente, etiquetas moviéndose continuamente, rojo de 19 s y arranque en verde con H20, controles, guardado y escenarios. La primera revisión registra las pruebas originales de reloj, selección y LAN. Sin certificación de móviles físicos o pinch. Ver informe final para evidencia concreta de esta revisión.

## Pendientes consentidos

20 registros de datos; asignaciones oficiales ruta/tipo/vagón, más planos, patios/inventarios/vacíos; calibración con OD y varios días; revisión exhaustiva de cruces/obras. Vigencia del catálogo: 12 de los 117 servicios utilizables terminan el 11 sep. 2026 y dejan el corredor de Portal Usme sin alternativas de planificación desde el 12; es límite de la instantánea, no del buscador. Fases y coordinación semafóricas reales por obtener; el ciclo de escenario ya está integrado. Mantener estas incertidumbres visibles y enlazadas desde la app. Nuevas observaciones del usuario deben incorporarse sobre esta versión.

Procedimiento de actualización de fuentes en docs/ACTUALIZAR_DATOS.md; es el documento a seguir cuando cambie el sistema real. Revisión de los pendientes en docs/PENDIENTES_20260911.md. E48/12444, H76/1213 y K86/629 se reimportaron con `tools/refresh_route_details.py`, que baja solo el detalle de los identificadores indicados a una carpeta propia y deja `refresh_latest.json`; la metadata de catálogo, vigencia incluida, sigue viniendo de la instantánea base. Cada ruta lleva `detail_snapshot` con su procedencia. El contexto urbano es la única fuente sin `fetch_*` y con la ruta fija dentro de build_context.py.

Publicación en GitHub Pages **preparada y sin ejecutar** por indicación de Daniel: `.github/workflows/pages.yml` publica solo app/dist, se dispara a mano y comprueba pruebas, JSON, paridad curado/web, versión `?v=` única y ausencia de rutas absolutas; tras desplegar verifica el Content-Type de `.mjs`. Falta activar Settings → Pages → Source: GitHub Actions, que es de la cuenta. Pasos en docs/PUBLICACION_WEB_20260911.md.

Colas de buses en semáforos: analizado y **no implementado** por decisión de Daniel. Ver docs/COLAS_Y_ESPACIO_20260911.md.

Antes de terminar cada hito, verificar diff, commit/push y coincidencia HEAD local/remoto. Los informes del 10 sep. se conservan como evidencia histórica, no resultados actuales.
