# Recursos propios de la prueba

`source/articulado_prototipo.blend` y `game/assets/vehicles/articulado_prototipo.glb` se generaron con `tools/build_bus.py` en Blender 5.2.1 instalado por Daniel. Geometría y materiales originales del proyecto; no se copiaron modelos de Roblox, otros videojuegos o fabricantes.

Articulado provisional: dos cuerpos, una articulación, cuatro puertas a la izquierda, 18 m de longitud nominal, 2,55 m de carrocería, tres ejes y acabado rojo con una franja amarilla como referencia general aportada por Daniel. Los retrovisores sobresalen. Las cotas son decisiones de ensayo, no mediciones de un Busscar, Volvo, Scania o eléctrico real. No se usa el nombre de una variante comercial para validarlo.

El GLB conserva `Front` y `Rear` independientes. El motor sitúa `Rear` en el enganche y construye el fuelle flexible en ejecución. El .blend muestra los cuerpos alineados con el enganche a 2,7 m del eje de referencia delantero. Por ello, regenerar con el script mantiene el contrato; reexportar manualmente el .blend sin revisar los orígenes puede duplicar ese desplazamiento.

La pista, edificios de contexto, plataforma, materiales de asfalto y mobiliario son originales y ficticios. No representan la ciudad modelada en el explorador ni una estación real de TransMilenio. La base geográfica tiene atribución independiente en docs/FUENTES.md.
