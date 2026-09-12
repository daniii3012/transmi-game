# Semáforos con evidencia directa en calzada TransMilenio

Consulta OSM capturada en `20260911T120000Z`; cobertura tomada de `app/dist/services.json` y filtrada a 12 m de sus polilíneas. Se evaluaron 2588 nodos `highway=traffic_signals`; se aceptaron 450 con pertenencia directa a `highway=busway` o a un `highway=service` con identificación explícita de TransMilenio/acceso bus-only.

No se activan cruces por proximidad: los nodos rechazados por no tener un way calificable se conservan en la auditoría JSON. OSM no aporta aquí fases, ciclos ni coordinación; `timings` queda en `null` como dato de fuente; el motor usa por separado ciclos estimados visibles.

- Resultado: [`data/curated/busway_signals.json`](../data/curated/busway_signals.json), 450 señales aceptadas.
- Raw y hashes: [`data/raw/busway_signals/20260911T120000Z/manifest.json`](../data/raw/busway_signals/20260911T120000Z/manifest.json), [`data/raw/busway_signals/20260911T120000Z/osm_map.json`](../data/raw/busway_signals/20260911T120000Z/osm_map.json), [`data/raw/busway_signals/20260911T120000Z/evidence.json`](../data/raw/busway_signals/20260911T120000Z/evidence.json).
- Fuente: OpenStreetMap contributors, ODbL 1.0; URLs de nodo y way y sus SHA-256 están en cada `way_source`.

## Geometría y auditoría de integración

La captura inicial de celdas se complementó con **189 respuestas `way/full` y 450 respuestas de nodo**. Se archivan 639 XML con URL y SHA-256 en `details/manifest.json`. Las vías completas incluyen nodos normales, indispensables para calcular la tangente local. No se calcula la orientación uniendo semáforos alejados. `osm_map.json` y `evidence.json` tienen hashes propios en el manifiesto principal. La carpeta `20260911T120000Z` es un identificador; la ampliación se consultó a partir de `2026-09-11T22:26:47Z`.

De 450 señales con evidencia, **449** se asocian por geometría y sentido a **112 variantes utilizables** (3.936 asociaciones señal/recorrido, no señales adicionales). Una queda sin asociación operativa. El inventario no es una auditoría exhaustiva de todos los semáforos ni certifica su estado físico actual.

Para activar una señal en un recorrido se exige pertenencia nodal a una vía calificada y archivada, distancia ≤12 m, tangente compatible (coseno ≥0,87 en valor absoluto), `oneway` y `traffic_signals:direction` cuando existen. La tolerancia de la asociación a la polilínea oficial es una aproximación documentada, independiente de la evidencia de existencia. Se preservan vueltas distintas de una ruta sin duplicar el mismo cruce en vértices contiguos.

## Operación estimada

Cada señal usa un ciclo de **90 s: 52 verde, 3 amarillo y 35 rojo**, con desfase reproducible por ID. No son fases oficiales ni se simula coordinación semafórica o tráfico transversal. Amarillo se trata conservadoramente como detención. El cálculo ajusta la envolvente métrica de velocidad para frenar a cero, espera hasta verde y vuelve a acelerar; no teletransporta el bus. Si la luz cambia a verde durante la aproximación, puede conservarse un frenado conservador.

Las esperas son por vehículo. No se resuelven colas longitudinales microscópicas en el semáforo: varios buses pueden coincidir visualmente en el punto de control. Las reservas de atención en estaciones siguen siendo independientes. La reproducción acelerada o el retroceso conservan exactamente las mismas fases y esperas para un mismo instante.

El ajuste **Semáforos corroborados** está activado por defecto en Operación. Los puntos de color aparecen al acercarse. El detalle del bus informa “Esperando luz verde” y los segundos restantes; “en espera” suma atención y semáforos, con desglose al posar el cursor. Los tiempos del planificador son nominales y no predicen fases ni aforo.

Reproducción sin red: `../../work/venv/bin/python tools/build_busway_signals.py --raw data/raw/busway_signals/20260911T120000Z`. Una nueva descarga se hace expresamente con `tools/fetch_busway_signals.py`, sin reemplazar silenciosamente las fuentes al jugar.
