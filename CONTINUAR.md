# Continuidad — Transmi 2D

Actualizado: 10 de septiembre de 2026. Esta entrega sustituye las notas que describían solo un laboratorio. Leer README.md, docs/OPERACION_Y_DATOS.md y docs/VALIDACION_20260910.md antes de continuar.

## Instrucciones y decisiones de Daniel

- Simulador 2D geográfico 1:1 de troncales y duales. Zonales y TransMiCable fuera del alcance. 3D pausado en `archive/transmi3d`; no retomar Godot/Blender por inercia.
- Referencia visual preferida: Subway Builder, con legibilidad de Mini Metro. Mapa real, paneles compactos, colores publicados, sin construcción de líneas.
- Metros y km/h reales; reloj 1×/acelerado y reversible. Seleccionar ruta, una o varias troncales, o la red. No son posiciones GPS en vivo.
- Autorizó expresamente estimaciones ajustables de frecuencia/demanda y pruebas completas en navegador. Dos carriles por sentido como abstracción, paso independiente de atención y pequeñas colas. Las asignaciones de vagón estimadas se identifican.
- Añadió pasajeros por estación/hora y orientación al centro en la mañana/periferia en la tarde. Integrado mediante validaciones históricas + hipótesis; no dejarlo descrito como enteramente pendiente.
- Destacó F63/Z63 dual articulado eléctrico; perfil publicado 160 integrado. Otros tipos sin ficha por ruta siguen estimados (80/160/240/250).
- Corrigió C15 Chapinero Ciclovía: es zonal, ID366 excluido. C15/3915 y H15/367 troncales, 19 paradas cada una, enlazadas en búsqueda y detalle. Evidencia del API TransMiApp conservada.
- Push a `daniii3012/transmi-game` autorizado. Mantener aplicación local; no desplegar. No pedir nuevamente las autorizaciones ya concedidas. Agentes ligeros solo para investigación acotada; los dos usados terminaron, uno agotó cuota. No hay tarea automática pendiente.

## Ubicación y ejecución

Repo: `/Users/daniel/Documents/Codex/2026-09-08/ho/outputs/BogotaTransmi`. Rama `main`, remoto `https://github.com/daniii3012/transmi-game.git`.

- Fuente web editable: `app/dist`; módulos de simulación, worker y renderer separados. Three.js 0.186.0 local.
- Servidor loopback `python3 tools/serve_network_2d.py`, URL `http://127.0.0.1:8766/`. El lanzador `ABRIR_SIMULACION_2D.command` abre/reutiliza el servidor. Sirve solo `app/dist` y envía no-store. No detener procesos del usuario.
- Python geo disponible: `../../work/venv/bin/python`. Python estándar sirve web e importa agregados. Node está disponible en PATH.
- `/work/` del repo está ignorado. No añadir archivos temporales ni ZIP/CSV de transacciones.
- `web/transmi2d` es compatibilidad con la ubicación anterior, no otra aplicación activa.

## Estado integrado

- 138 servicios/variantes depurados; 115 utilizables de 103 códigos, 23 pendientes. Mapa bruto: 116 registros/100 códigos. 113 variantes con salidas el jueves inicial 10 sep. 2026. Los contadores significan cosas diferentes.
- Geometría oficial recortada, secuencia de paradas, fuentes, hashes, calendarios, vigencia y bloqueo de anomalías. M85 empieza en el tramo correcto; K86/629 completo bloqueado, no confundirlo con aeropuerto/5316.
- Calendario colombiano, ventanas partidas y nocturnas, reemplazo Ciclovía solo explícito, horas pico/valle y reloj reversible. Se precalculan día anterior + elegido para cruzar medianoche.
- Movimiento métrico, aceleración/frenado/curvas, paradas y reservas por vagón. Expresos no heredan la cola de la parada. Cantidad de vagones oficial, asignación y dimensiones estimadas.
- Demanda histórica agregada de 1.920.298 validaciones, archivo 9 sep., 14 posteriores a medianoche. 1.920.297 enlazadas a 142 estaciones lógicas; una de cable excluida. Se descarta información transaccional del producto. Perfiles por hora, dirección/descenso/fines de semana estimados, capacidad y abandono de espera.
- F63/Z63 eléctricos de 160, mezcla ajustable de biarticulados y padrones duales estimados. Tipo estable por vehículo y reutilización compatible en terminal.
- Contexto OSM 15.573 elementos, colores oficiales, puentes con bordes y túneles punteados si están etiquetados. No se infiere nivel ni conexión por intersección de líneas; no es auditoría completa de obras.
- UI con rutas, operación, terminales, datos, inspectores de ruta/bus/estación, guardar/restaurar, filtros, seguimiento y velocidades 1/8/32/120.
- Worker sustituido al reconstruir, instancias gráficas, agrupación visual, dibujo actualizado en zoom incluso pausado. No se borran buses para esconder la congestión.

## Fuentes y regeneración

Base `data/raw/services/20260910T185326Z`; complemento `supplement_20260910`; curación `data/curated/services.json`. Paraderos duales y contexto tienen sus manifests/respuestas. Los detalles de C15/H15 en `data/research/c15_h15_20260910` contrastan enlaces aportados por Daniel.

`tools/build_services.py` → services.json + auditoría; `build_context.py` → context.json; `aggregate_validations.py` → agregado de un ZIP oficial; `import_passenger_profiles.py` → demand.json. El ZIP de referencia se descargó en el trabajo de la tarea `/Users/daniel/Documents/Codex/2026-09-10/create-an-image-of-2/work/passengers/`, fuera del repositorio, y no hace falta para ejecutar el simulador.

Usar el agregado versionado para reproducir la app sin consultar internet. Si se vuelve a descargar, preservar fuente/fecha/hash y revisar licencias por conjunto. El artículo de buses 240 es histórico de 2015, no una noticia de 2025. Fuentes actuales de F63/Z63 verificadas en publicaciones oficiales de agosto de 2026.

## Verificación y límites

30 pruebas Node y 3 Python activas. Incluyen escala, velocidades, curvas, calendarios, pausa/retroceso, medianoche, capacidad/conservación, reservas sin superposición por posición, paso expreso, tipos estables, F63/Z63 y corrección C15. El laboratorio anterior tiene pruebas propias; su prueba de 3.000 buses no representa la operación real.

Benchmark actual del motor: referencia máximo 944 buses, 4 en cola local simultánea, preparación ~4,0 s, muestreo ~0,41 ms, heap ~389 MB; estrés (2/3 min, demanda3, mezcla40%) máximo 1.938 buses, 42 en cola, ~9,2 s, ~1,33 ms, ~808 MB. Son mediciones Node de esta máquina, no FPS ni promesa universal. Reportes JSON versionados.

QA en navegador de escritorio documentada por acciones verificadas. Se recuperó el servidor local que estaba apagado; no se detuvo otro. Se abrió una pestaña nueva porque la anterior quedó en una página de error al recargar. No declarar QA completa de móviles o de cada una de las 115 geometrías.

## Pendientes concretos

1. Conseguir trazados vigentes de E48, H76/J76, K86 completo y aclarar Ciclovía de L81/L82/M82/M85/M86/P85. Doce registros bloqueados ya están vencidos; no reactivarlos artificialmente.
2. Asignaciones reales ruta→tipo, vagón/puerta, patios/inventario y recorridos en vacío. Actualmente terminales abstractas, vehículos creados según oferta, sin flota fija de operador.
3. Calibrar con más días, frecuencias y tiempos de viaje, salidas y matriz OD. No confundir denegaciones de abordaje repetidas con personas únicas ni validaciones con viajes completos.
4. Contrastar rotondas/puentes/deprimidos y obras una por una. La forma se conserva, pero no se certifica una topología de niveles exhaustiva.
5. Ampliar QA táctil/móvil y medir FPS/memoria en equipos modestos; mantener los límites configurables y el trabajador cancelable.

La versión funcional queda integrada; el trabajo futuro debe resolver estos huecos con evidencia, no reiniciar arquitectura ni investigación ya guardada. Al guardar un nuevo hito, confirmar push y coincidencia entre HEAD local y remoto.

## Nueva solicitud activa · 11 septiembre

Daniel probó el checkpoint y envió15capturas y una lista extensa de correcciones. **Aplicar ahora docs/OBSERVACIONES_20260911.md después de respaldar este checkpoint.** Cambia defaults a50calle/60troncal±5, capacidades80/160/240 y tamaño fijo por ruta; pide plataformas físicas OSM, trazados duales grises solo fuera de troncal, mejor seguimiento/selección/slider, modo oscuro, hora actual y lanzadorLAN. No confundir guardar el checkpoint con terminar estas nuevas tareas. Los23registros pendientes deben permanecer pendientes.
