# Continuidad del proyecto — 10 de septiembre de 2026

Leer este archivo, README.md y docs/PLAN_DEL_PROYECTO.md antes de continuar. Daniel pidió conservar el progreso entre sesiones por los límites de uso. Eso no cancela el proyecto. Los documentos y el código están en Git; revisar `git log` y `git status` para el último checkpoint.

## Decisiones vigentes

- **Meta final: un Bus Simulator de Bogotá centrado en todo el sistema BRT de TransMilenio**, con ciudad cozy y condensada. Daniel reconsideró la obligación de distancias jugables 1:1 y autorizó continuar con compresión selectiva. Fuente geográfica intacta; un metro del motor sigue siendo un metro jugable. Se acortan intervalos intermedios candidatos, conservando dimensiones coherentes de buses, plataformas, carriles y maniobras. No se fija un 1:2 global: factor 0,5 solo como hipótesis local.
- Américas es el piloto; zona inicial Mandalay–Av. Américas/Av. Boyacá–Marsella. Después ampliar Américas, Calle 13/centro, NQS/Carrera 30, Calle 26 y Séptima; continuar al resto del sistema. No reducir la meta a esos corredores.
- Ciudad actual con obras y desvíos. Fecha inicial del escenario: 8–9 de septiembre de 2026; evidencia y vigencia por zona. Carrera 50–Américas–Calle 13–Calle 6 y la futura actualización de 68–Américas son nodos expresamente pedidos. No habilitar diseños finales antes de comprobar apertura.
- **Dirección visual cozy confirmada**, basada en over the hill, la maqueta ferroviaria de Nick y el proyecto de Givros. Formas suaves, materiales mate, color contenido y detalle selectivo, con longitudes reales y jugables separadas. ETS/Bus Simulator orientan recorrido y operación. Ver docs/DIRECCION_VISUAL.md y docs/ESCALA_Y_COMPRESION.md. No presentar los ensayos como el acabado urbano final.
- **Exclusivamente para un jugador.** La meta incluye otros buses haciendo rutas con IA local: carriles, paradas, puertas, colas, reservas y simulación lejana. Plan en docs/IA_DE_BUSES.md; aún no implementado. No introducir multijugador.
- Conducción accesible, puertas y articulación coherentes; sin obligación de simulación mecánica exhaustiva.
- Posible publicación futura si alcanza un buen desarrollo. **Push a https://github.com/daniii3012/transmi-game está expresamente autorizado**; no se pidió desplegar una versión del juego.
- El asistente tiene autorización para investigar, instalar herramientas y desarrollar/modelar. Daniel confirmó que instaló Blender. No pedir que lo vuelva a instalar.
- Daniel autorizó agentes ligeros para investigación y tareas acotadas. Ya se usó gpt-5.6-luna; sus borradores se revisaron. docs/TRABAJO_CON_AGENTES.md contiene los siguientes paquetes. Mantener física e integración con el principal; no prometer porcentajes de ahorro de cuota.
- **Próxima exploración solicitada: simulación 2D con Three.js**, inspirada en la legibilidad de Mini Metro, con geografía fuente 1:1, mayoría de rutas troncales y mayoría de la flota del escenario circulando simultáneamente. Es una línea paralela, no reemplaza el juego 3D condensado. Ver docs/EXPLORACION_TRANSMI_2D.md; todavía no implementada. El piloto pequeño solo valida la arquitectura.
- Daniel ya probó la pista. Pidió roce lateral sin frenado completo, cámara orientable y mayor margen de parada; están integrados y comprobados. Pidió evitar ciclos continuos de pequeñas pruebas manuales: agrupar el trabajo y la revisión por hitos coherentes.

## Ubicación y herramientas

- Proyecto: `/Users/daniel/Documents/Codex/2026-09-08/ho/outputs/BogotaTransmi`.
- Temporales y herramientas portables: `/Users/daniel/Documents/Codex/2026-09-08/ho/work`.
- Godot: `work/tools/Godot.app/Contents/MacOS/Godot`, versión `4.7.2.stable.official.ed1daf0bf`. ZIP oficial verificado, SHA-256 `c58a24e31d720be9d62f60cb5627c4e695fb72f21b0cfe1bc9ccaa9a3b3ba63e`.
- **Blender de Daniel: `/Applications/Blender.app/Contents/MacOS/Blender`, 5.2.1 LTS**, usado para generar el bus. También quedó una copia portátil previa en work/tools/Blender.app y el DMG oficial; no se necesita otra descarga.
- Python: `work/venv/bin/python`, base 3.9, dependencias en tools/requirements.txt.
- Equipo: M3 Pro, GPU 14 núcleos, 18 GB de RAM. No se ha hecho benchmark de una ciudad completa.
- En la revisión actual hay acceso completo a archivos y red; Godot gráfico ya pudo lanzarse directamente desde comandos. Comprobar el contexto vigente si cambia de sesión, sin confundir permisos del entorno con autorización de alcance.

## Qué funciona ahora

### Base geográfica

Instantánea oficial `data/raw/20260909T035301Z`: 153 registros de estaciones, 22 de trazados (no equivalen a conteo operativo); recorte con 9.772 registros de construcción, 523 calzadas, 797 andenes y 140 separadores. Procedencia, fichas y hashes conservados.

`tools/build_pilot.py` genera `game/data/pilot.json`: 300.729 triángulos. Origen AEQD WGS84 lon -74.136, lat 4.63027; Godot X este, Y arriba, Z sur. 1 unidad = 1 metro. Las alturas siguen siendo estimaciones CONNPISOS × 3 m, con reserva de 2 pisos para 16 valores inválidos. CONELEVACI NO son metros; CONALTURA requiere interpretación.

Explorador con cámaras, edificios y marcadores. Terreno y puentes planos; no es una carretera validada para conducir. **Se corrigió y verificó la captura de dos vistas distintas**. `docs/preview_general.png` y `docs/preview_boyaca.png` ahora tienen hashes diferentes y muestran encuadres correctos. Último log: work/godot_capture.log, CAPTURE_COMPLETE.

### Primera pista conducible

`ABRIR_SIMULADOR.command` abre la nueva escena principal. `ABRIR_EXPLORADOR.command` conserva la vista geográfica. F2 cambia entre ambas. La pista y plataforma son ficticias y métricas.

- Articulado provisional de dos cuerpos, longitud nominal 18 m, carrocería de 2,55 m, tres ejes, cuatro puertas izquierdas (ocho hojas), cabina sencilla y fuelle flexible.
- Blender editable: assets/source/articulado_prototipo.blend. GLB de juego: game/assets/vehicles/articulado_prototipo.glb. Generador original: tools/build_bus.py. Dimensiones de ensayo, no una réplica verificada de un fabricante.
- `bus_motion.gd`: cinemática plana con enganche fuera del eje, reversa y límite de articulación de 60°, dirección que se modera con velocidad, freno y resistencia.
- `bus_collision.gd`: barrido de traslación y solape final por pasos pequeños, cajas de los dos cuerpos y envolvente del fuelle. `resolve` conserva avance tangencial al rozar el andén, comprobando la pose candidata; contacto frontal sigue deteniendo. `check` conserva comprobación estricta para pruebas. Obstáculos en capa 1. No hay suspensión ni contacto de ruedas con terreno 3D todavía.
- `bus_visual.gd`: importación, cuerpos, ruedas, hojas de puertas y fuelle dinámico.
- `practice_service.gd`: alineación de las cuatro puertas, separación puerta-andén 0,025–0,90 m, error longitudinal hasta 1,20 m por puerta y rumbo del frente dentro de 6°. Son valores de ensayo, no normativa real. Tiempo de atención 4 s, cierre y salida 15 m.
- `practice_world.gd` y `practice.gd`: pista, plataforma, controles, cámaras, HUD, pausa y reinicio.
- `driving_camera.gd`: tres vistas orientables; clic derecho + ratón mira, rueda acerca/aleja, V centra, Q/E mirada lateral rápida en cabina. La cámara exterior limita su posición ante obstáculos mediante un rayo; no es aún una solución exhaustiva para toda geometría de estación.
- Controles: W acelera, S frena, A/D gira, Espacio freno de mano, R avance/reversa estando detenido, P puertas detenido, C cámaras, Retroceso reinicia, Esc pausa, F2 mapa; ratón, V y Q/E como se indica arriba.
- Primera aplicación cozy en la pista: pintura mate, paleta del entorno, copas agrupadas, variación del suelo y HUD verde oscuro/crema. Se aplica en Godot; los materiales base del archivo Blender siguen siendo los originales del generador.
- La pista permanece como ensayo independiente. El bus ya está integrado en una primera sección local de Mandalay, descrita abajo. Sin pasajeros visibles, sonido, tráfico, espejos funcionales, selector de rutas oficiales, guardado de partida, pendientes ni streaming.

### Estudio de compresión del piloto

**ABRIR_ESTUDIO_ESCALA.command** abre game/scenes/scale_study.tscn. Escena de comparación 3D, no conducible: 1 muestra los dos ejes con la misma escala de cámara, 2/3 acercan Mandalay en cada versión, clic derecho orbita, rueda acerca, F2 pista y F3 explorador geográfico. Capturas en docs/preview_escala.png y docs/preview_escala_mandalay.png.

- `data/design/americas_scale_study.json`: fuente fijada a 20260909T035301Z, tres IDs de estación, factor 0,5 en intervalos candidatos, 180 m extra por extremo. Las estaciones reservan su longitud publicada más 60 m de aproximación por extremo; Boyacá reserva 220 m a cada lado del punto. Estas reservas son supuestos de diseño pendientes de revisión de calle y de niveles; no equivalen a cotas del puente o plataformas.
- `tools/corridor_layout.py`: transformación de un único eje por intervalos, mantiene vectores dentro de áreas protegidas y ofrece distancia fuente ↔ jugable reversible. Une reservas solapadas. Factor válido (0,1]; no encoge las mallas de los vehículos.
- `tools/build_scale_study.py`: recorta el único componente oficial TZ009 que contiene las estaciones, conserva IDs, posiciones y hashes; rechaza desconexión o autointersección resultante. Genera `game/data/scale_study.json` y `data/processed/scale_study_summary.json`. Los datos raw y el pilot.json original permanecen intactos.
- Eje del estudio: **1.602,47 m → 1.285,94 m**, reducción **19,75 %**. Contiene **969,42 m protegidos** y **633,05 m candidatos**. Mandalay–Boyacá: 789,26 → 563,56 m; Boyacá–Marsella: 453,21 → 410,03 m. Son distancias sobre el eje, no sobre carriles ni itinerarios de servicio.
- Dos instancias del bus conservan dimensiones. Hay 60 módulos de contexto en referencia y 44 en condensada; son edificios ilustrativos con tamaño propio. Ese conteo no mide ahorro total de modelado. Bandas arena = reserva de diseño; las estaciones son marcadores, sin modelo detallado.
- El transformador no resuelve redes con ramificaciones/ciclos ni geometría de manzanas. Antes de unir troncales, resolver nodos compartidos, niveles, circulación y entorno mediante una disposición común. No deformar todas las mallas GIS ni dar por transitables las líneas del estudio.

### Catálogo de rutas

El buscador oficial aportado por Daniel tiene una API pública. `tools/audit_routes.py` conserva candidatos con campos de transporte y hashes, excluyendo metadatos administrativos. Auditoría inicial en `data/research/20260909T090945Z/`: 256 registros/IDs del filtro TransMilenio, seis páginas. **No son 256 rutas troncales distintas.** Hay códigos con guion, un 16 sin troncal asignada y códigos repetidos con destinos diferentes. No clasificar solo por formato, campo tipo o presencia de troncal.

Ver docs/RUTAS_INVESTIGACION.md. Falta importar secuencia de paradas y validar variantes, fechas y carriles. No se descargó GTFS vigente: el endpoint antiguo falló. La licencia de la API del buscador no se ha establecido; no heredar la de la cartografía. Ninguno de estos candidatos está ofrecido como servicio jugable.

### Referencias y Mandalay

Se inspeccionó visualmente la experiencia ferroviaria enlazada por Nick y la galería oficial de over the hill. De Givros se leyó la descripción, pero X exigió iniciar sesión para el vídeo completo; no afirmar que se revisaron su animación y acabado. Links y traducción a Bogotá en docs/DIRECCION_VISUAL.md.

docs/ESTACION_MANDALAY.md registra num_est 05101, punto oficial, longitud publicada 115,705 m, ancho publicado 3 m y dos vagones. El significado geométrico del ancho/longitud sigue pendiente. El visor de planos identifica TM0082, pero sus enlaces de imagen devolvieron 404 y una reconsulta de la API por urllib dio 403. La tabla oficial de 2019 sirve como antecedente, no para rotular operación de 2026. El principal contrastó los atributos con la instantánea local y la fecha de la nota oficial. Se obtuvo posteriormente otra fuente de polígonos y se construyó una primera sección conducible provisional; ver los apartados siguientes.

## Comprobaciones completadas

- Python geográfico: 2 pruebas, escala cardinal de 1 km y triangulación cóncava con patio.
- Godot conducción: **19/19 comprobaciones**. Círculo delantero contrastado con radio teórico y remolque con radio interior independiente, límite/reanudación de articulación, puertas, parada y barreras de 5 cm delante y detrás.
- Comentarios del usuario: **12/12 comprobaciones**, en test_player_feedback.gd. Roce lateral diez segundos: unos 39,9 m de avance a 4 m/s, sin solape final de las tres envolventes; puede separarse girando hacia fuera. Impacto frontal sigue deteniendo, margen de parada acepta/rechaza los casos previstos y cámara permite orientar/centrar.
- Integración de escena: PASS. Importa cuerpos y ocho hojas, se aproxima automáticamente a la plataforma usando sus colisiones, atiende la parada y abre las hojas visuales.
- Carga headless de escena principal: PRACTICE_READY. Captura nativa sobre OpenGL/Metal M3 Pro: PRACTICE_CAPTURE_COMPLETE. Se inspeccionaron docs/preview_practica.png, preview_cabina.png y preview_puertas.png; muestran vistas distintas, el bus completo y puertas abiertas.
- Capturas actualizadas tras los ajustes visuales en work/cozy_capture.log, PRACTICE_CAPTURE_COMPLETE. Las pruebas no constituyen aún validación de conducción por puentes reales ni ensayos largos de rendimiento. La próxima revisión de Daniel se reservará para un hito integrado.
- Compresión: **8 pruebas Python aprobadas**, 6 nuevas de intervalos, inversión, geometría protegida, límites y piloto real; las 2 geográficas previas siguen pasando. Integración Godot del estudio aprobada: ambas instancias del articulado mantienen dimensiones con diferencia inferior a 1 mm, escala y anclaje. Capturas nativas de comparación y detalle revisadas; work/scale_study_capture.log terminó en SCALE_STUDY_CAPTURE_COMPLETE.

## Investigación nueva y sección conducible de Mandalay

Se obtuvo una fuente oficial nueva con nueve polígonos de las secciones de Mandalay. Fuente, respuesta y hashes están en data/research/mandalay_scheme_20260909/; descargador tools/fetch_mandalay_scheme.py. La revisión del agente fue contrastada y corregida: cuatro Vagon, una Externa, una Conexa, una Conexion, una Transicion y una Entrada. tipo/nombre/id_vagon tienen discrepancias, no inferir A/B ni operación. Licencia de este servicio aún no establecida, independiente de las capas CC BY previas.

Se inspeccionó una ortofoto SIMUR nominal 2021: dos franjas de plataforma/cubierta, zona central amplia y puente peatonal al este. Referencia local work/mandalay/ortofoto_2021.png, petición con hash junto a ella; no es textura ni prueba de vigencia de 2026. Ver docs/MANDALAY_REFERENCIAS_ADICIONALES.md para evidencia y límites. La investigación quedó respaldada en el commit 581aa0f; después se implementó la sección que sigue.

### Mandalay conducible: estado integrado

Abrir **ABRIR_MANDALAY.command**, o desde Esc en la pista anterior. Esc permite elegir práctica hacia Av. Boyacá o hacia Banderas. Son sentidos de práctica local, no servicios oficiales ni trayectos hasta esas estaciones. Aproximación de 75 m, cuatro puertas, 4 s de atención, cierre y salida de 25 m. El mundo sigue plano. Documentación completa en docs/MANDALAY_JUGABLE.md.

- data/design/mandalay.json y tools/build_mandalay.py generan game/data/mandalay.json y data/processed/mandalay_summary.json. Instantes fuente fijados y hashes registrados; usa el origen de estación y la tangente de game/data/scale_study.json. No modificar raw ni mezclar esta disposición con todo el eje del estudio.
- Recorte local: 480 m reales → 390 m jugables. Zona central de ±150 m intacta; factor 0,5 fuera. Es una reserva mayor que la del estudio anterior para proteger el acceso representado. X local apunta aproximadamente al sur, Z al oeste, Y arriba; origen geográfico y tangente en el resumen.
- Cuatro huellas Vagon, plaza central unida y arquitectura vertical provisional. Se excluye Externa 287. Plataformas a 1,10 m, cubiertas desde 4,35 m, puente a unos 6,3 m: estimaciones, no cotas. Las puertas corresponden al bus de ensayo, no a A/B o servicios verificados. Cubiertas y plataforma tienen colisiones, además de la estructura principal del puente; rampas peatonales y contexto no tienen navegación física completa.
- 84 partes de edificios con sus huellas y patios intactos, alturas estimadas por pisos. 179 registros omitidos por límites, contacto con vías o solapamiento. Decoración propia de fachadas, árboles, luminarias y jardines; todavía no acabado final.
- Hay 58,68 m² de empalmes de pavimento provisionales para reconciliar bordes del esquema y calzadas. Todos quedan dentro de 1 m de las calzadas fuente; el generador rechaza ajustes mayores. También recorta caras superiores de andenes/separadores para no ocultar el pavimento. No presentar el borde ajustado como medición real.
- game/scripts/mandalay.gd hereda el controlador de practice.gd mediante fábricas de mundo, servicio y pose inicial; conserva controles, HUD y cámaras. mandalay_world.gd genera arquitectura y contexto; station_service.gd verifica anclajes en cualquier orientación. Servicio atendido exige cuatro segundos continuos alineado y salida hacia delante; reversa no completa el ciclo.
- Pruebas Godot nuevas: **17 comprobaciones aprobadas**, incluidos ambos ciclos con colisiones y ocho hojas abiertas. Integración de la pista anterior vuelve a aprobar tras reutilizar el controlador.
- Suite Python: **11 pruebas aprobadas**. Tres nuevas contrastan aristas de estación con geodesia, áreas de huellas/patios y hashes, y toda la envolvente del bus sobre la superficie en 101 poses por sentido. Comprobación independiente de la física del motor.
- Capturas nativas generales, cabina y parada en docs/preview_mandalay*.png; log work/mandalay_capture.log, MANDALAY_CAPTURE_COMPLETE. Capturas de inspección, sin benchmark prolongado ni aprobación final de acabado.

## Ficha compartida del vehículo: cierre integrado

`game/data/vehicles/articulado_prototipo.json` es la fuente común de dimensiones, extremos de cuerpos, ejes, enganche, puertas identificadas, ruedas, cámaras y parámetros de conducción. Se consumen desde Blender/Python y Godot. Las medidas y comportamiento originales permanecen; no se ha creado un nuevo tipo de bus. Ver docs/FICHA_DE_VEHICULO.md.

- `tools/vehicle_definition.py` valida el esquema, la topología de dos cuerpos y los huecos. `vehicle_definition.gd` carga los datos en Godot; `Motion` expone `spec` y `door_positions()`.
- Se actualizaron física, colisiones, visual, cámara, pista y servicio de Mandalay. `tools/build_mandalay.py` genera anclajes desde la misma ficha y registra su hash/IDs; no repite la lista de coordenadas.
- GLB y Blender regenerados. `game/assets/vehicles/articulado_prototipo.manifest.json` vincula ficha y modelo mediante hashes; Godot detecta desincronización. Mandalay no acepta anclajes de otra revisión del bus.
- Fuelle corregido para usar coordenadas locales cuando se coloca el visual dentro de un sector trasladado o girado. No se ha implementado origen flotante ni contacto con terreno 3D.
- **14 pruebas Python y 7 comprobaciones Godot nuevas aprobadas**. Las 19 pruebas base, 12 de ajustes del usuario, integración de pista, 17 de Mandalay y 5 del estudio de escala siguen pasando. Logs work/vehicle_spec_*.log; captura nativa completa en vehicle_spec_capture.log.
- La plantilla aún tiene detalles de carrocería e interior propios del prototipo. No admite biarticulados ni embarque derecho por cambiar únicamente el JSON. Para otra variante, revisar compatibilidad y geometría.

Un agente ligero preparó docs/BOYACA_NIVELES_REFERENCIAS.md. El principal contrastó punto/dimensiones con raw, consultó directamente los campos de accesos en la API oficial y revisó la nota BIM de 2022. Hay una pista de consultoría IDU-529-2022, pero no cotas verificadas de nivel/gálibo/rampas. No habilitar el cruce con alturas inventadas.

## Próximo trabajo concreto

1. **Explorar la simulación 2D solicitada**, según docs/EXPLORACION_TRANSMI_2D.md: Three.js es viable para cámara ortográfica e iconos repetidos. Geografía fuente sin compresión, piloto de red dirigido con buses y paradas, concebido para ampliar a mayoría de rutas y flota concurrente. No confundir los registros candidatos con servicios validados ni animación con operación real. No desplegar.
2. Consolidar Mandalay antes de extender: verificar cotas, puente/accesos, puertas reales y estado 2026 con fuentes fechadas. Se puede inspeccionar la escena entera, pero solo se han comprobado los dos ejercicios locales; no afirmar que todas sus vías laterales son transitables. No inventar rótulos A/B ni rutas.
3. Usar la ficha compartida al incorporar una variante real; revisar geometría, alturas y compatibilidad antes de multiplicar buses. Mantener las pruebas de articulación y puertas.
4. Construir el grafo de carriles dirigido y la conexión a la siguiente estación. La muestra local se tendrá que integrar a una disposición común, sin transformar cada arista por separado. **No habilitar Boyacá** hasta revisar puente, rampas, niveles y continuidad; añadir soporte de altura y pendientes antes de circular por desniveles.
5. Completar el conjunto visual cercano de Mandalay y medir carga, memoria y FPS en conducción. Añadir colisiones de entorno donde corresponda, sonido básico y guardar la selección de práctica. No confundir el modelo cozy provisional con un acabado aprobado.
6. Con el grafo y anclajes definidos, introducir un NPC en circuito según docs/IA_DE_BUSES.md. Continúa planificado, no implementado. Rutas oficiales solo después de verificar secuencias, vigencia y cobertura.

## Ejecución y limitaciones del entorno

Desde la raíz del proyecto, usar Godot absoluto en vez de depender del PATH:

```sh
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_driving.gd
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_player_feedback.gd
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_practice_scene.gd -- --keep-running
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_scale_study.gd -- --keep-running
../../work/venv/bin/python tools/build_scale_study.py
../../work/venv/bin/python tools/build_mandalay.py
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_mandalay.gd -- --keep-running
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_vehicle_definition.gd
../../work/venv/bin/python -m unittest discover -s tests -v
```

Blender genera el modelo con `Blender -b -t 2 --python tools/build_bus.py`. En un entorno restringido previo, Blender falló al inicializar Metal y Godot gráfico al conectar con WindowServer; sus scripts .command funcionaron desde Finder mediante CUA. Con los permisos actuales, Godot gráfico ya se ejecutó directamente desde comandos y guardó las tres capturas con `-- --capture-practice`. No asumir que aquel fallo sigue vigente. Scripts auxiliares de sesión: work/build_bus.command, work/preview_practice.command y work/preview.command.

No desactivar protecciones. Capturas nativas de CUA fallaron antes; el propio viewport de Godot guarda PNG revisables. No cerrar terminales/aplicaciones del usuario. Los recursos .godot y copias .blend1 no se versionan.

Capturar el estudio: Godot `--path game res://scenes/scale_study.tscn -- --capture-scale-study`. Ejecutar gráficamente; el modo headless normal solo comprueba carga. Las dos vistas se capturan en serie. Los materiales de las bandas usan iluminación uniforme para distinguir reservas en esta vista de diseño; no representan el acabado final del pavimento.

## Respaldo

Git local, rama main, remoto origin https://github.com/daniii3012/transmi-game.git. El remoto estaba vacío; el primer push autorizado terminó correctamente con upstream main. Se usa la identidad Git configurada por Daniel. No cambiar visibilidad, forzar historial ni desplegar. Guardar los siguientes hitos y verificar coincidencia entre HEAD local y origin/main.
