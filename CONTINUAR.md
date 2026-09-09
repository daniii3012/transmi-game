# Continuidad del proyecto — 9 de septiembre de 2026

Leer este archivo, README.md y docs/PLAN_DEL_PROYECTO.md antes de continuar. Daniel pidió conservar el progreso entre sesiones por los límites de uso. Eso no cancela el proyecto. Los documentos y el código están en Git; revisar `git log` y `git status` para el último checkpoint.

## Decisiones vigentes

- **Meta final: un Bus Simulator de Bogotá centrado en todo el sistema BRT de TransMilenio**, con distancias espaciales 1:1. Prioridad: escala, red, conducción y operación antes que gráficos complejos.
- Américas es el piloto; zona inicial Mandalay–Av. Américas/Av. Boyacá–Marsella. Después ampliar Américas, Calle 13/centro, NQS/Carrera 30, Calle 26 y Séptima; continuar al resto del sistema. No reducir la meta a esos corredores.
- Ciudad actual con obras y desvíos. Fecha inicial del escenario: 8–9 de septiembre de 2026; evidencia y vigencia por zona. Carrera 50–Américas–Calle 13–Calle 6 y la futura actualización de 68–Américas son nodos expresamente pedidos. No habilitar diseños finales antes de comprobar apertura.
- Apariencia reconocible con materiales y luz cuidados. Referencias del usuario: over the hill, ETS y Bus Simulator; su última aclaración da prioridad a escala y sistemas. No presentar el entorno ficticio de pruebas como el acabado final de Bogotá.
- Conducción accesible, puertas y articulación coherentes; sin obligación de simulación mecánica exhaustiva.
- Posible publicación futura si alcanza un buen desarrollo. **Push a https://github.com/daniii3012/transmi-game está expresamente autorizado**; no se pidió desplegar una versión del juego.
- El asistente tiene autorización para investigar, instalar herramientas y desarrollar/modelar. Daniel confirmó que instaló Blender. No pedir que lo vuelva a instalar.

## Ubicación y herramientas

- Proyecto: `/Users/daniel/Documents/Codex/2026-09-08/ho/outputs/BogotaTransmi`.
- Temporales y herramientas portables: `/Users/daniel/Documents/Codex/2026-09-08/ho/work`.
- Godot: `work/tools/Godot.app/Contents/MacOS/Godot`, versión `4.7.2.stable.official.ed1daf0bf`. ZIP oficial verificado, SHA-256 `c58a24e31d720be9d62f60cb5627c4e695fb72f21b0cfe1bc9ccaa9a3b3ba63e`.
- **Blender de Daniel: `/Applications/Blender.app/Contents/MacOS/Blender`, 5.2.1 LTS**, usado para generar el bus. También quedó una copia portátil previa en work/tools/Blender.app y el DMG oficial; no se necesita otra descarga.
- Python: `work/venv/bin/python`, base 3.9, dependencias en tools/requirements.txt.
- Equipo: M3 Pro, GPU 14 núcleos, 18 GB de RAM. No se ha hecho benchmark de una ciudad completa.
- Se concedió red y escritura en ajustes/caché de Godot a nivel de sesión. Si el entorno cambia, usar los permisos mínimos del entorno sin pedir nuevamente autorización de alcance.

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
- `bus_collision.gd`: barrido de traslación y solape final por pasos pequeños, cajas de los dos cuerpos y envolvente del fuelle. Obstáculos en capa 1. No hay suspensión ni contacto de ruedas con terreno 3D todavía.
- `bus_visual.gd`: importación, cuerpos, ruedas, hojas de puertas y fuelle dinámico.
- `practice_service.gd`: alineación de las cuatro puertas, tiempo de atención 4 s, cierre y salida 15 m.
- `practice_world.gd` y `practice.gd`: pista, plataforma, controles, cámaras, HUD, pausa y reinicio.
- Controles: W acelera, S frena, A/D gira, Espacio freno de mano, R avance/reversa estando detenido, P puertas detenido, C cámaras, Retroceso reinicia, Esc pausa, F2 mapa.
- El bus NO está integrado en las calzadas reales. Sin pasajeros visibles, sonido, tráfico, espejos funcionales, selector de rutas oficiales, guardado de partida, pendientes ni streaming.

### Catálogo de rutas

El buscador oficial aportado por Daniel tiene una API pública. `tools/audit_routes.py` conserva candidatos con campos de transporte y hashes, excluyendo metadatos administrativos. Auditoría inicial en `data/research/20260909T090945Z/`: 256 registros/IDs del filtro TransMilenio, seis páginas. **No son 256 rutas troncales distintas.** Hay códigos con guion, un 16 sin troncal asignada y códigos repetidos con destinos diferentes. No clasificar solo por formato, campo tipo o presencia de troncal.

Ver docs/RUTAS_INVESTIGACION.md. Falta importar secuencia de paradas y validar variantes, fechas y carriles. No se descargó GTFS vigente: el endpoint antiguo falló. La licencia de la API del buscador no se ha establecido; no heredar la de la cartografía. Ninguno de estos candidatos está ofrecido como servicio jugable.

## Comprobaciones completadas

- Python geográfico: 2 pruebas, escala cardinal de 1 km y triangulación cóncava con patio.
- Godot conducción: **19/19 comprobaciones**. Círculo delantero contrastado con radio teórico y remolque con radio interior independiente, límite/reanudación de articulación, puertas, parada y barreras de 5 cm delante y detrás.
- Integración de escena: PASS. Importa cuerpos y ocho hojas, se aproxima automáticamente a la plataforma usando sus colisiones, atiende la parada y abre las hojas visuales.
- Carga headless de escena principal: PRACTICE_READY. Captura nativa sobre OpenGL/Metal M3 Pro: PRACTICE_CAPTURE_COMPLETE. Se inspeccionaron docs/preview_practica.png, preview_cabina.png y preview_puertas.png; muestran vistas distintas, el bus completo y puertas abiertas.
- Las pruebas no constituyen aún validación de conducción por puentes reales o ensayos largos de rendimiento. Daniel puede probar los controles para ajustar sensación.

## Próximo trabajo concreto

1. Tomar una estación del piloto, preferiblemente Mandalay, y reunir planos/fotografías actuales y medidas de andén, vagones, puertas y carriles. Consultar el enlace de planos de estaciones descubierto en el cliente del buscador. No inventar la etiqueta A/B o su compatibilidad.
2. Construir una primera sección BRT física en metros, con niveles y anchos comprobados, y conectar el bus a ella. No habilitar el cruce de Boyacá hasta revisar puente, rampas y continuidad.
3. Introducir datos configurables de vehículo y anclajes, antes de multiplicar variantes. El prototipo tiene constantes de ensayo en motion y service; al usar una variante real deben migrar a una especificación compartida.
4. Integrar un pequeño recorrido entre paradas del piloto, con selector de práctica, próxima parada y guardado. Patrón real solo cuando se compruebe toda la cobertura necesaria.
5. Mejorar un segmento visto desde la cabina: materiales, plataforma y fachadas cercanas. Priorizar reconocimiento y operación sobre decorar todo el recorte.

## Ejecución y limitaciones del entorno

Desde la raíz del proyecto, usar Godot absoluto en vez de depender del PATH:

```sh
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_driving.gd
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --script res://tests/test_practice_scene.gd -- --keep-running
../../work/venv/bin/python -m unittest discover -s tests -v
```

Blender genera el modelo con `Blender -b -t 2 --python tools/build_bus.py`. En el entorno de comandos restringido, Blender falló al inicializar Metal y Godot gráfico al conectar con WindowServer. Ambos funcionan al lanzar sus scripts .command desde Finder mediante CUA. Scripts de sesión: work/build_bus.command, work/preview_practice.command y work/preview.command. Para abrir un archivo fuera de pantalla en Finder: Ir a carpeta → ruta exacta → Return → Cmd+O. No depender de una acción AX que no cambie de archivo seleccionado.

No desactivar protecciones. Capturas nativas de CUA fallaron antes; el propio viewport de Godot guarda PNG revisables. No cerrar terminales/aplicaciones del usuario. Los recursos .godot y copias .blend1 no se versionan.

## Respaldo

Git local, rama main, remoto origin https://github.com/daniii3012/transmi-game.git. El remoto estaba vacío; el primer push autorizado terminó correctamente con upstream main. Se usa la identidad Git configurada por Daniel. No cambiar visibilidad, forzar historial ni desplegar. Guardar los siguientes hitos y verificar coincidencia entre HEAD local y origin/main.
