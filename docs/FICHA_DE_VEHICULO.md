# Ficha compartida del articulado

9 de septiembre de 2026. Implementada para el articulado provisional de dos cuerpos; las medidas siguen siendo de ensayo, no una réplica de fabricante.

La fuente única es `game/data/vehicles/articulado_prototipo.json`. Contiene dimensiones nominales, extremos de cada cuerpo, ejes, enganche, IDs y posiciones de puertas, ruedas, apertura, cámaras y parámetros de conducción. La distancia entre ejes, centros y tamaños de envolvente se derivan de esos campos. Los IDs de puerta son estables: front_1, front_2, rear_1 y rear_2.

## Consumidores

| Componente | Uso de la ficha |
|---|---|
| `tools/vehicle_definition.py` | Carga y validación antes de generar recursos; límites, topología, ejes y puertas |
| `tools/build_bus.py` | Cuerpos, ejes, huecos y hojas; genera Blender editable y GLB |
| `vehicle_definition.gd` | Lectura compartida en Godot y detección de un GLB desactualizado |
| `bus_motion.gd` | Conducción, enganche, remolque y posición de cada puerta |
| `bus_collision.gd` | Envolventes de ambos cuerpos y fuelle, ubicadas con el mismo enganche |
| `bus_visual.gd` | Modelo, hojas identificadas, recorrido de apertura y radio de ruedas |
| `driving_camera.gd` | Anclaje de cabina y objetivo de seguimiento |
| `tools/build_mandalay.py` | Puntos de práctica y umbrales del bus, con IDs y hash de la ficha usada |
| Servicios de práctica | Comprueban las puertas que publica la cinemática, sin repetir sus coordenadas |

El fuelle visual ahora convierte sus vértices al espacio local del vehículo. Esto evita desplazarlo dos veces cuando el bus se coloque dentro de un sector trasladado o girado. No equivale a implementar un origen flotante ni físicas sobre pendientes.

## Reconstrucción

Si cambia la ficha, reconstruir en este orden desde la raíz:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python tools/build_bus.py
../../work/venv/bin/python tools/build_mandalay.py
../../work/tools/Godot.app/Contents/MacOS/Godot --headless --path game --editor --import --quit
```

`articulado_prototipo.manifest.json`, junto al GLB, conserva el hash de la ficha, hash del modelo, revisión y anclajes. El juego detecta una ficha/modelo desincronizados antes de iniciar la conducción. Mandalay rechaza una parada cuyos anclajes se generaron con otra revisión. Las prácticas siguen ajustadas a las medidas originales; no se cambiaron los 18 m nominales, 2,55 m de ancho, enganche de 2,7 m ni los márgenes pedidos por Daniel.

## Alcance y límites

Es una plantilla para un articulado de dos cuerpos con embarque izquierdo. No se ha creado un selector de flota ni se admite todavía un biarticulado o puertas derechas operativas. El validador rechaza topologías no implementadas y huecos inválidos, en lugar de generar una variante aparentemente utilizable.

La ornamentación, mobiliario interior y varios detalles de carrocería siguen siendo una plantilla de modelado. Una variante real requiere revisar la cabina, anchos libres, alturas, puertas, envolventes y comportamiento, además de cambiar números. La ficha central facilita ese trabajo; no convierte automáticamente el prototipo en cualquier Volvo, Scania o BYD.

Las puertas todavía se validan en planta porque la física es plana. La altura de embarque tendrá que entrar en la comprobación al implementar calzadas elevadas y pendientes. Una estación verificada tendrá anclajes propios: no se moverán sus puertas para acomodar cualquier bus. Los umbrales de Mandalay siguen siendo de práctica.

## Comprobaciones

- 14 pruebas Python: incluyen coherencia de anclajes, hashes de GLB/ficha, rechazo de topología y puertas inválidas, además de las pruebas geográficas anteriores.
- 7 comprobaciones Godot nuevas: correspondencia GLB/ficha, cuatro puertas articuladas bajo un sector trasladado y girado, fuelle local, cambio de enganche, envolvente de colisión y rechazo de recursos/puertas desactualizados.
- Se mantienen aprobadas las 19 comprobaciones de conducción, 12 de comentarios del usuario, integración de la pista, 17 de Mandalay y comparación de escala.
- Modelo regenerado con Blender 5.2.1, importación en Godot 4.7.2 y capturas nativas de Mandalay revisadas. No se ha hecho un benchmark de toda la ciudad.
