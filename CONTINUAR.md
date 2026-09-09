# Continuidad — leer antes de trabajar

Guardado el 8 de septiembre de 2026, Bogotá. El usuario pidió preservar el progreso porque se aproxima al límite de uso de cinco horas. No confundir ese límite con una cancelación del proyecto.

## Intención y decisiones del usuario

Daniel quiere un videojuego personal de conducción de TransMilenio en Bogotá, escala 1:1 para las distancias, con apariencia reconocible y más detalle que un mapa muy básico. La física debe ser de simulador arcade, con puertas, articulaciones y paradas. No busca publicar ni llevar a producción. Ha autorizado al asistente a encargarse de investigar, instalar herramientas, modelar y desarrollar durante varias sesiones.

Corredores prioritarios elegidos: **Américas, Calle 13 y centro, NQS/Carrera 30, Carrera Séptima y Calle 26**. Quiere el **estado actual con obras y desvíos**. NO reemplazar esta decisión por una ciudad sin obras ni escoger Autonorte como alcance aceptado.

Referencias aportadas: Mapas Bogotá 2D/3D, mapa digital de TransMilenio, dos publicaciones de X, Bogotá TM Bus en Roblox, noticia de obras de Carrera 50–Américas–Calle 13–Calle 6 y noticia de 50 articulados eléctricos duales. Están en docs/FUENTES.md. El usuario mencionó extremos grises en duales, una franja amarilla en articulados y dos en biarticulados; revisar variantes y fotografías antes de convertirlo en una regla universal.

## Ubicación y herramientas

- Raíz del proyecto: `/Users/daniel/Documents/Codex/2026-09-08/ho/outputs/BogotaTransmi`.
- Trabajo temporal y herramientas: `/Users/daniel/Documents/Codex/2026-09-08/ho/work`.
- Godot: `work/tools/Godot.app/Contents/MacOS/Godot`, relativo a la carpeta `ho`.
- Versión verificada: `4.7.2.stable.official.ed1daf0bf`.
- ZIP oficial: SHA-256 `c58a24e31d720be9d62f60cb5627c4e695fb72f21b0cfe1bc9ccaa9a3b3ba63e`.
- La firma del paquete se verificó con `codesign --verify --deep --strict` antes de ejecutar. No se alteró el paquete.
- Python preparado: `work/venv/bin/python`, versión base 3.9. Dependencias fijadas en tools/requirements.txt.
- Blender todavía NO está instalado. Se propone instalarlo para la siguiente fase de modelado, desde su web oficial para Apple Silicon.
- Máquina: MacBook Pro M3 Pro, GPU de 14 núcleos y 18 GB de memoria unificada. Había aproximadamente 221 GiB disponibles según `df` al iniciar. No se necesita comprar herramientas para esta prueba.
- Se concedió escritura de sesión en `~/Library/Application Support/Godot` y `~/Library/Caches/Godot` para sus ajustes. El acceso de red se concedió para el turno; comprobar permisos si hace falta en otra sesión.

## Resultado comprobado

1. `tools/fetch_pilot.py` completó la descarga oficial. Instantánea `data/raw/20260909T035301Z` (UTC; aún 8 de septiembre local). Incluye GeoJSON, metadatos de servicios, fichas CKAN y manifest.json.
2. Capas completas consultadas: 153 registros de estaciones y 22 de trazados. Son registros del servicio; NO afirmar que equivalen al número actual de estaciones operativas o de troncales.
3. Recorte geográfico: 9.772 registros de construcción, 523 calzadas, 797 andenes y 140 separadores. Los registros de construcción pueden representar partes de edificios.
4. `tools/build_pilot.py` genera `game/data/pilot.json` (300.729 triángulos) y data/processed/summary.json.
5. Pruebas Python: **2/2 pasaron**. Verifican distancias de 1 km desde el origen en cuatro direcciones y triangulación de un polígono cóncavo con patio interior.
6. Godot en modo headless cargó la escena y terminó correctamente: `PILOT_READY triangles=300729.0 stations=3`.
7. Primera ejecución gráfica nativa completada en OpenGL 4.1 sobre Metal / Apple M3 Pro. Se generaron y visualizaron dos PNG. Log: `work/godot_capture.log`.

## Revisión visual pendiente al guardar

El primer render mostró superficies demasiado claras y el pie de controles fuera de pantalla. Se corrigió explorer.gd: iluminación más baja, ACES, especular a cero, encuadre general más amplio y posición del pie. Se lanzó una segunda captura. **Comprobar su finalización y revisar ambos PNG antes de considerar aprobada esta última revisión visual**. El último log leído tenía PILOT_READY, pero todavía no CAPTURE_COMPLETE. Los PNG pueden estar siendo reemplazados durante la captura.

La captura usa la opción `-- --capture`, espera varias imágenes, guarda docs/preview_general.png y docs/preview_boyaca.png, y sale. El lanzador de prueba está en `work/preview.command`.

Limitación del entorno: ejecutar la interfaz gráfica directamente con exec_command produjo código 134; el modo headless sí funciona. Se logró lanzar la interfaz abriendo `work/preview.command` desde Finder mediante CUA. La captura de pantalla nativa de CUA falló con ScreenCaptureKit -3811; se usaron PNG generados por el propio viewport de Godot para revisar el resultado. No desactivar protecciones del sistema. No cerrar terminales ni apps ajenas al proyecto.

## Próxima tarea concreta

1. Terminar la revisión visual indicada arriba y guardar una versión estable del explorador.
2. Definir una sección física verificable de la calzada BRT entre Marsella, Av. Boyacá y Mandalay: carriles por sentido, separadores, adelantamiento, nivel del cruce de Boyacá, pendiente y suelo con colisiones. El explorador plano NO constituye aún una vía transitable fiel.
3. Instalar Blender para Apple Silicon; preparar un bus articulado de prueba en metros, de aproximadamente 18 m hasta elegir y verificar la variante definitiva. Desarrollar manejo y articulación antes de texturas y cabina detallada.
4. Investigar plataformas, vagones, puertas y puntos de detención de una estación del piloto. No inventar nombres de vagones A/B o compatibilidad basándose solo en longitud.
5. Preparar la ficha de obras del nodo Carrera 50 con fecha, PMT/desvíos vigentes y geometría de avance. La nota del 28 de agosto describe avance y proyecto final; no basta para dibujar las trayectorias provisionales al 8 de septiembre.

## Precauciones técnicas específicas

- 1 unidad del motor = 1 metro. CRS de trabajo del piloto: proyección local AEQD WGS84 con origen lon -74.136, lat 4.63027. En Godot: X este, Y arriba, Z sur. Consultas al servidor transformadas a EPSG:4326.
- Todas las alturas del blockout son **estimaciones CONNPISOS × 3 m**, con dos pisos de reserva para 16 valores inválidos. CONELEVACI no es una altura medida en metros. CONALTURA requiere interpretación de niveles de bloques antes de usarlo.
- El terreno está plano; los puentes también aparecen planos. No deducir conectividad vial por cruces de líneas 2D.
- Aún NO hay bus, conducción, colisiones, rutas jugables, animación de puertas, tráfico, estaciones modeladas, streaming de sectores ni obras modeladas.
- GTFS existe en catálogo, pero la ficha antigua dice fecha del dato 2022 y el endpoint probado devolvió HTTP 500. No afirmar que se descargó un GTFS vigente.
- El visor 3D de Bogotá usa extrusión de polígonos; no se ha localizado un modelo completo de Bogotá listo para importar con fachadas y colisiones.
- No tomar imágenes generadas, renders promocionales o mapas antiguos como mediciones ni como prueba de obras terminadas.

## Comandos comprobados

Desde `/Users/daniel/Documents/Codex/2026-09-08/ho`:

```sh
work/venv/bin/python outputs/BogotaTransmi/tools/build_pilot.py
work/venv/bin/python -m unittest discover -s outputs/BogotaTransmi/tests -v
work/tools/Godot.app/Contents/MacOS/Godot --headless --path outputs/BogotaTransmi/game --log-file /Users/daniel/Documents/Codex/2026-09-08/ho/work/godot_headless.log
```

No hace falta volver a investigar todo: consultar docs/FUENTES.md, los metadatos guardados y docs/PLAN_DEL_PROYECTO.md. No hay despliegue, cuenta externa, compra ni automatización del proyecto.
