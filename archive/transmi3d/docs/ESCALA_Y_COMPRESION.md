# Escala y compresión selectiva

Estado al 9 de septiembre de 2026: dirección de Bogotá condensada autorizada por Daniel. Primera comparación de ejes implementada y medida. El factor y las reservas siguen siendo hipótesis de diseño; no se ha validado todavía un corredor conducible ni un porcentaje de ahorro de producción.

## Tres magnitudes que deben permanecer separadas

- **Geografía fuente:** datos oficiales, coordenadas, trazados, estaciones, conexiones y metadatos conservados 1:1. No se reescriben para hacerlos caber en el mundo jugable.
- **Metros del juego:** una unidad del motor equivale a un metro jugable. Vehículos, plataformas, carriles, anchos y espacios de giro usan medidas coherentes con sus especificaciones verificadas o con estimaciones identificadas.
- **Longitud real y longitud jugable:** un tramo puede tener una longitud real derivada de la fuente y una longitud recorrible en el escenario. Si el estudio aplica compresión a un tramo elegible, la relación queda registrada por tramo y no se presenta como una medida geográfica.

La meta sigue siendo toda la red BRT, con estaciones y conexiones reconocibles, singleplayer y buses NPC mediante IA local futura. La compresión cambia la separación recorrible de algunos tramos repetitivos; no cambia la identidad de la red ni convierte automáticamente datos de rutas en servicios jugables.

## Hipótesis del piloto

El piloto probará una relación candidata de **0,5** solo en tramos repetitivos que no contengan decisiones de conducción relevantes. No se adopta un factor global fijo 1:2. Cada tramo debe clasificarse antes de generar la escena y conservar el vínculo con su geometría y mediciones de origen.

Quedan protegidos de la compresión:

- entornos de estaciones, plataformas, vagones, accesos y cruces peatonales;
- cruces viales, conexiones entre troncales, niveles, puentes, deprimidos y espacios de giro;
- rampas, obras, desvíos, cierres y cualquier transición cuyo reconocimiento o maniobra dependa de la distancia;
- los anclajes necesarios para puertas, carriles, señalización, frenado, colas y operación de buses.

En las zonas protegidas, la geometría y la distancia jugable se construyen y validan en metros del juego. En los tramos candidatos, la compresión debe conservar dirección, orden, conectividad, límites de velocidad de diseño, visibilidad y tiempo suficiente para decidir y maniobrar. Las distancias finales se medirán después de ensamblar el corredor; no se inferirán del factor candidato.

## Estudio reproducible

`tools/build_scale_study.py` genera la comparación del piloto con una configuración sin compresión y otra con compresión selectiva. `tools/corridor_layout.py` conserva una correspondencia reversible de distancia acumulada sobre el eje fuente y distancia jugable. Cada intervalo protegido mantiene sus vectores de desplazamiento; las piezas se sitúan sin escalar sus mallas. El registro por tramo debe incluir identificador de la fuente, longitud real, clasificación, factor aplicado si corresponde, longitud jugable resultante, extremos protegidos y fecha de medición. La escena generada debe poder reconstruirse sin editar los datos fuente.

La revisión comprobará continuidad entre estaciones, lectura desde cabina, aproximación y salida, radios y envolventes del bus, ancho de carriles, espacio de giro, conexiones y transiciones de obra. También se medirá el tiempo de recorrido en el escenario implementado. La medición del eje no constituye una prueba de maniobras ni de ahorro de producción. No se ha comprobado aún cada cruce o acceso dentro de los intervalos candidatos; esas revisiones pueden ampliar las reservas y reducir la compresión. No extrapolar el factor a toda Bogotá.

La referencia externa es el artículo de SCS sobre reajuste de escala y de intersecciones: [The rescale](https://blog.scssoft.com/2016/06/the-rescale.html). Sirve únicamente como referencia de compresión y reajuste de intersecciones; no es una regla para este proyecto ni sustituye la validación del piloto.

## Rutas, horarios y estado jugable

La longitud de una ruta, sus paradas y sus horarios reales se conservan como datos de servicio con fecha y fuente. No se convierten automáticamente en horarios, tiempos de viaje o servicios jugables. Un servicio se habilitará solo cuando su secuencia, carriles, conexiones, estaciones y escenario vigente estén comprobados en el mundo implementado. Un tramo condensado podrá ofrecerse como práctica identificada mientras la cobertura completa siga pendiente.


## Resultado de la primera comparación

Configuración: [americas_scale_study.json](../data/design/americas_scale_study.json). Resultado reproducible: [scale_study_summary.json](../data/processed/scale_study_summary.json). Fuente: instantánea oficial `20260909T035301Z`, eje `TZ009`; hashes de fuente y configuración conservados en la salida.

| Magnitud | Referencia | Propuesta condensada |
|---|---:|---:|
| Eje completo del estudio | 1.602,47 m | 1.285,94 m |
| Mandalay → Av. Américas–Av. Boyacá, sobre el eje | 789,26 m | 563,56 m |
| Av. Américas–Av. Boyacá → Marsella, sobre el eje | 453,21 m | 410,03 m |
| Longitud total de zonas protegidas | 969,42 m | 969,42 m |
| Módulos de contexto ilustrativos | 60 | 44 |

El eje incluye 180 m adicionales por extremo. La reducción total es **19,75 %**: los 633,05 m candidatos se reducen a la mitad y los 969,42 m protegidos mantienen longitud. La reserva de estación combina su longitud publicada con 60 m de aproximación por extremo; Boyacá reserva 220 m a cada lado del punto oficial. Son márgenes de diseño pendientes de contrastar, no mediciones del puente ni de la plataforma.

La escena muestra ambos ejes con la misma escala de cámara, bandas de reserva, marcadores de las tres estaciones y dos instancias del mismo bus de 18 m. El suelo, ancho de vía de ensayo de 8 m, árboles y edificios son ilustrativos. La menor cantidad de módulos demuestra el efecto de acortar espacio, sin medir ahorro total de modelado. No hay reproducción detallada de Mandalay, puente, niveles ni carriles oficiales en esta escena.

Abrir `ABRIR_ESTUDIO_ESCALA.command`: 1 compara; 2 y 3 acercan Mandalay en cada variante; clic derecho orbita y rueda cambia zoom. F2 abre la pista conducible y F3 el explorador geográfico original. Capturas: [comparación](preview_escala.png) y [detalle](preview_escala_mandalay.png).

Para reconstruir, ejecutar `python tools/build_scale_study.py` con el entorno de dependencias del proyecto. La salida separada es `game/data/scale_study.json`; los GeoJSON originales y `game/data/pilot.json` permanecen intactos.

## Límite de la transformación actual

El algoritmo resuelve un solo eje continuo. Comprueba orden de estaciones, intervalos, inversión de distancias y ausencia de autointersección del eje resultante. No es una deformación general de Bogotá: no distribuye automáticamente cruces compartidos, manzanas o redes con ciclos, ni garantiza espacio lateral de todo el entorno. Antes de conectar corredores, un diseño común deberá resolver sus nodos y niveles. El estado de obras tampoco cambia por acortar un tramo.

## Aplicación local en Mandalay

La primera sección conducible usa un recorte propio de 480 m fuente y 390 m jugables, con ±150 m centrales protegidos. La reserva se amplió para el acceso peatonal representado. Conserva cuatro huellas oficiales de plataforma y dimensiones de edificios; los empalmes provisionales entre esquema y calzadas se registran explícitamente. Este tramo local aún debe conectarse a una disposición común del corredor; no reemplaza automáticamente las cifras ni la geometría del estudio de eje. Ver [Mandalay conducible](MANDALAY_JUGABLE.md).
