# Continuidad del proyecto — 9 de septiembre de 2026

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
- El bus NO está integrado en las calzadas reales. Sin pasajeros visibles, sonido, tráfico, espejos funcionales, selector de rutas oficiales, guardado de partida, pendientes ni streaming.

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

docs/ESTACION_MANDALAY.md registra num_est 05101, punto oficial, longitud publicada 115,705 m, ancho publicado 3 m y dos vagones. El significado geométrico del ancho/longitud sigue pendiente. El visor de planos identifica TM0082, pero sus enlaces de imagen devolvieron 404 y una reconsulta de la API por urllib dio 403. La tabla oficial de 2019 sirve como antecedente, no para rotular operación de 2026. El principal contrastó los atributos con la instantánea local y la fecha de la nota oficial. Aún no se construyó el modelo detallado de la estación.

## Comprobaciones completadas

- Python geográfico: 2 pruebas, escala cardinal de 1 km y triangulación cóncava con patio.
- Godot conducción: **19/19 comprobaciones**. Círculo delantero contrastado con radio teórico y remolque con radio interior independiente, límite/reanudación de articulación, puertas, parada y barreras de 5 cm delante y detrás.
- Comentarios del usuario: **12/12 comprobaciones**, en test_player_feedback.gd. Roce lateral diez segundos: unos 39,9 m de avance a 4 m/s, sin solape final de las tres envolventes; puede separarse girando hacia fuera. Impacto frontal sigue deteniendo, margen de parada acepta/rechaza los casos previstos y cámara permite orientar/centrar.
- Integración de escena: PASS. Importa cuerpos y ocho hojas, se aproxima automáticamente a la plataforma usando sus colisiones, atiende la parada y abre las hojas visuales.
- Carga headless de escena principal: PRACTICE_READY. Captura nativa sobre OpenGL/Metal M3 Pro: PRACTICE_CAPTURE_COMPLETE. Se inspeccionaron docs/preview_practica.png, preview_cabina.png y preview_puertas.png; muestran vistas distintas, el bus completo y puertas abiertas.
- Capturas actualizadas tras los ajustes visuales en work/cozy_capture.log, PRACTICE_CAPTURE_COMPLETE. Las pruebas no constituyen aún validación de conducción por puentes reales ni ensayos largos de rendimiento. La próxima revisión de Daniel se reservará para un hito integrado.
- Compresión: **8 pruebas Python aprobadas**, 6 nuevas de intervalos, inversión, geometría protegida, límites y piloto real; las 2 geográficas previas siguen pasando. Integración Godot del estudio aprobada: ambas instancias del articulado mantienen dimensiones con diferencia inferior a 1 mm, escala y anclaje. Capturas nativas de comparación y detalle revisadas; work/scale_study_capture.log terminó en SCALE_STUDY_CAPTURE_COMPLETE.

## Checkpoint adicional: investigación de Mandalay guardada

Se obtuvo una fuente oficial nueva con nueve polígonos de las secciones de Mandalay. Fuente, respuesta y hashes están en data/research/mandalay_scheme_20260909/; descargador tools/fetch_mandalay_scheme.py. La revisión del agente fue contrastada y corregida: cuatro Vagon, una Externa, una Conexa, una Conexion, una Transicion y una Entrada. tipo/nombre/id_vagon tienen discrepancias, no inferir A/B ni operación. Licencia de este servicio aún no establecida, independiente de las capas CC BY previas.

Se inspeccionó una ortofoto SIMUR nominal 2021: dos franjas de plataforma/cubierta, zona central amplia y puente peatonal al este. Referencia local work/mandalay/ortofoto_2021.png, petición con hash junto a ella; no es textura ni prueba de vigencia de 2026. Ver docs/MANDALAY_REFERENCIAS_ADICIONALES.md para evidencia y límites. El nuevo modelo conducible todavía no está implementado en este checkpoint.

## Próximo trabajo concreto

1. Continuar desde docs/MANDALAY_REFERENCIAS_ADICIONALES.md: usar la nueva fuente poligonal para la sección conducible, con dos sentidos y ciclo de parada. Alturas y puertas siguen pendientes de cota; registrar estimaciones. No extruir Externa 287 como obstáculo ni interpretar nombre como clasificación fiable. Mantener estación y puente peatonal en zona sin compresión.
2. Construir la primera sección BRT con medidas locales coherentes y su correspondencia a la fuente geográfica; conectar el bus a ella. La disposición condensada es una base de diseño, no carriles ya validados. No habilitar Boyacá hasta revisar puente, rampas, niveles y continuidad.
3. Introducir datos configurables de vehículo y anclajes, antes de multiplicar variantes. El prototipo tiene constantes de ensayo en motion y service; al usar una variante real deben migrar a una especificación compartida.
4. Integrar un pequeño recorrido entre paradas del piloto, con selector de práctica, próxima parada y guardado. Patrón real solo cuando se compruebe toda la cobertura necesaria.
5. Aplicar la dirección cozy a esa sección como un conjunto: materiales, plataforma y fachadas cercanas. Preservar proporciones y reconocimiento; revisar desde cabina y exterior, medir tiempo de recorrido y rendimiento. El diseño del contexto reemplaza repetición por módulos; no aplasta edificios reales.
6. Con el grafo y los anclajes definidos, introducir un NPC en circuito según docs/IA_DE_BUSES.md antes de extenderlo a servicios reales. Mantener este trabajo como una fase explícita, no declarar tráfico existente.

## Ejecución y limitaciones del entorno

Desde la raíz del proyecto, usar Godot absoluto en vez de depender del PATH:

```sh
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_driving.gd
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_player_feedback.gd
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_practice_scene.gd -- --keep-running
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_scale_study.gd -- --keep-running
../../work/venv/bin/python tools/build_scale_study.py
../../work/venv/bin/python -m unittest discover -s tests -v
```

Blender genera el modelo con `Blender -b -t 2 --python tools/build_bus.py`. En un entorno restringido previo, Blender falló al inicializar Metal y Godot gráfico al conectar con WindowServer; sus scripts .command funcionaron desde Finder mediante CUA. Con los permisos actuales, Godot gráfico ya se ejecutó directamente desde comandos y guardó las tres capturas con `-- --capture-practice`. No asumir que aquel fallo sigue vigente. Scripts auxiliares de sesión: work/build_bus.command, work/preview_practice.command y work/preview.command.

No desactivar protecciones. Capturas nativas de CUA fallaron antes; el propio viewport de Godot guarda PNG revisables. No cerrar terminales/aplicaciones del usuario. Los recursos .godot y copias .blend1 no se versionan.

Capturar el estudio: Godot `--path game res://scenes/scale_study.tscn -- --capture-scale-study`. Ejecutar gráficamente; el modo headless normal solo comprueba carga. Las dos vistas se capturan en serie. Los materiales de las bandas usan iluminación uniforme para distinguir reservas en esta vista de diseño; no representan el acabado final del pavimento.

## Respaldo

Git local, rama main, remoto origin https://github.com/daniii3012/transmi-game.git. El remoto estaba vacío; el primer push autorizado terminó correctamente con upstream main. Se usa la identidad Git configurada por Daniel. No cambiar visibilidad, forzar historial ni desplegar. Guardar los siguientes hitos y verificar coincidencia entre HEAD local y origin/main.
