# Arquitectura del proyecto

## Estado implementado

```text
tools/fetch_pilot.py
    → data/raw/<fecha>/GeoJSON + metadatos + fichas + manifest
tools/build_pilot.py
    → reproyección local + recorte + triangulación + alturas estimadas
    → game/data/pilot.json + data/processed/summary.json
game/scripts/explorer.gd
    → mallas agrupadas + marcadores + cámara libre + interfaz
```

El JSON de mallas facilita inspeccionar y validar esta prueba. Para ampliar el mapa se reemplazará por recursos binarios por sector; no cargar toda Bogotá en un único JSON. Los datos originales permanecerán fuera de la escena y se conservarán como fuente de reconstrucción.

## Primera conducción implementada

`tools/build_bus.py` → Blender editable + GLB con cuerpos independientes. `bus_motion.gd` integra el vehículo en el plano; `bus_collision.gd` comprueba sus cuerpos; `bus_visual.gd` aplica poses, ruedas, puertas y fuelle. `practice_service.gd` verifica anclajes de cuatro puertas y el ciclo de parada. `practice_world.gd` construye la pista y sus obstáculos; `practice.gd` enlaza entrada, cámaras y HUD. Las pruebas del motor están en game/tests.

Esta cinemática plana no resuelve alturas ni suspensión. El mundo real continúa separado de la pista para no presentar la cartografía plana como carriles ya transitables.

## Sistemas propuestos y ampliaciones

| Sistema | Responsabilidad |
|---|---|
| WorldStreamer | Cargar sectores cercanos, retirar los lejanos, administrar niveles de detalle y origen local. |
| RoadNetwork | Carriles dirigidos, niveles, conexiones permitidas, superficies y colisiones. |
| VehicleController | Estado de conducción, velocidad, dirección, frenos, marcha y contacto con el suelo. |
| ArticulationController | Trayectoria de remolques, límites de ángulo, maniobras de reversa y colisiones de todos los cuerpos. |
| DoorController | Puertas independientes por lado, animaciones, enclavamiento y compatibilidad con el punto de parada. |
| StationController | Vagones, plataformas, puertas de estación, puntos de detención y accesos. |
| ServiceController | Servicio elegido, secuencia de paradas, sentido, calendario y progreso del recorrido. |
| WorksOverlay | Cierres, geometría temporal, desvíos y fechas de validez del escenario. |
| TrafficController | Buses y tráfico mixto simplificados, después de validar la conducción principal. |

## Contratos de datos

Todos los objetos deben tener identificador estable, fuente, fecha, unidad y estado de validación. Una altura estimada debe poder corregirse sin editar a mano una malla generada.

```text
WorldTile:
  id, bounds, origin, geometry_version, source_snapshot,
  mesh_resources, collision_resources, lods, reviewed_at

Lane:
  id, centerline_m, width_m, direction, level_id,
  allowed_vehicle_types, speed_design_kmh, next_lane_ids,
  valid_from, valid_to, evidence

Station:
  id, name, location, modules[], platforms[], access_points[], evidence

StopAnchor:
  id, station_id, module_label, lane_id, position_m, heading,
  platform_height_m, permitted_vehicle_types, door_alignment,
  valid_from, valid_to, verified

VehicleSpec:
  id, body_manufacturer, chassis, generation, propulsion,
  dimensions_m, axles[], articulation_joints[], doors[], livery_id,
  driving_parameters, dimension_sources

ServicePattern:
  id, source_feed, route_id, direction_id, stop_sequence[],
  calendar_id, lane_path_ids[], variant, verified

WorksEvent:
  id, area, scenario_date, valid_from, valid_to,
  closed_lane_ids[], temporary_lane_ids[], temporary_stop_ids[],
  construction_meshes[], source_url, evidence_date, confidence
```

Los nombres A/B/C son etiquetas de módulos cuando estén verificados, no identificadores globales de estación ni categorías de longitud del bus. Separar `source_id` de identificadores propios evita que una actualización del proveedor borre anotaciones de modelado.

## Escala y precisión

Piloto: WGS84 geográfico recibido del servidor → AEQD local en metros, origen -74.136, 4.63027. Mapeo a Godot: X = este, Y = altura relativa al suelo, Z = -norte. Los vértices finales se redondean al milímetro para el archivo; esto no convierte la cartografía original en una medición de precisión milimétrica.

Para la expansión, conservar coordenadas geográficas/proyectadas con doble precisión fuera de las físicas. Cada sector usa un origen local; desplazar el origen de la simulación si lo exige la extensión. Construir bordes coincidentes y comprobar que las colisiones no dejan escalones entre sectores.

## Recursos y regeneración

Guardar modelos de Blender editables, exportaciones GLB, materiales, sonidos y configuraciones de vehículo por separado. Las correcciones manuales de una zona van en una capa de ajustes, aplicada después de la generación. No corregir exclusivamente el archivo generado: se perdería al reconstruir.

Reutilizar módulos de estación y mobiliario, con variantes por sitio. Usar instancias para postes, árboles y elementos repetidos. Reservar geometría y texturas de mayor resolución para el bus y el entorno próximo a la cabina.

## Comprobaciones por fase

- Geografía: origen, escala, orientación, polígonos con huecos, duplicados, unidades y continuidad entre sectores.
- Conducción: aceleración/frenado, curva cerrada, cambio de carril, reversa y pendiente; observar toda la envolvente del bus.
- Paradas: aproximación en ambos sentidos, lado de puertas, alineación y bloqueo de movimiento con puertas abiertas.
- Obras: no existe conexión transitable a estructuras incompletas; desvíos y paradas temporales corresponden a la fecha elegida.
- Rendimiento: recorrido reproducible con memoria y tiempos de cuadro, además de FPS. Medir con bus, estaciones y tráfico antes de extrapolar desde el explorador.

El primer objetivo técnico después de esta prueba es un bus articulado manejable sobre una pista métrica y luego una estación completa. La expansión de kilómetros se hace cuando esos sistemas permiten recorrer el piloto sin bloqueos.
