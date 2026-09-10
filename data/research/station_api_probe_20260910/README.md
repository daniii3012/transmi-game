# Probe de estaciones y rutas (2026-09-10)

Consulta acotada para la simulación 2D de troncales y buses duales en Bogotá. Hora de consulta: 2026-09-10, America/Bogota (UTC−05). No se descargaron imágenes ni se recorrió el catálogo completo.

## Hallazgos

### Publicado por API oficial

- `https://tramites.transmilenio.gov.co/station-maps/api/map` respondió HTTP 200 y JSON de 48.842 bytes. El esquema observado tiene `base_image`, `markers` y `sizes`; contiene 156 marcadores y 13 líneas. Cada marcador trae `id`, `code`, `name`, `type`, `x_pct`, `y_pct`, `line{id,name,color}` e `image_url`.
- La muestra de líneas incluye `Carrera 7` (`id=12`, `#00949C`), `Carrera 10` (`id=11`, `#00949C`), `Américas` (`id=6`, `#BB0615`) y otras troncales. No aparece una línea llamada Avenida 68 en este visor de planos.
- La API de rutas del buscador oficial (`ms-transmiapp-rm2xahnybq-uk.a.run.app`) publicó P85 (`id=1316`) y M85 (`id=4596`) con fechas de vigencia, horarios y paraderos. Los JSON sanitizados están en `p85.json`, `p85_paraderos.json`, `m85.json` y `m85_paraderos.json`.

### P85/M85 y Avenida 68

P85 figura como `AV 68 Calle 9`, troncal `Avenida 68`, color `#A80F79`, vigente del 2026-06-28 al 2026-09-14. Horarios publicados: `L-S 05:00–21:00` y `D-F 14:00–21:00`. Sus ocho paraderos en el orden de `posicion` son Museo Nacional (estación), Centro Memoria, Quinta Paredes, CAN - British Council, Salitre El Greco - Vive Claro y tres paraderos de calle en AK 68 (Cl 23, Cl 20, Cl 12A).

M85 figura como `Museo Nacional Ciclovía`, troncal `Carrera 7`, color `#009A9D`, vigente del 2026-06-28 al 2026-09-13. Horario publicado: `L-D 05:00–21:00`. Sus diez paraderos en orden son cuatro paraderos de calle en AK 68 (Cl 11, Cl 9A, Cl 12, Cl 13), AK 68 Cl 19, Salitre El Greco - Vive Claro, CAN - British Council, Quinta Paredes, Centro Memoria y Museo Nacional (estación). La respuesta vincula el tramo de calle y estaciones, pero no publica geometría de carril, plataforma, puerta ni vagón.

### Duales por Carrera Séptima

La fuente oficial de rutas publica para M85 el troncal `Carrera 7`; la página oficial de la ruta y la guía general de diciembre de 2025 también describen servicios duales con paraderos de calle y estaciones. Como referencia histórica/oficial complementaria, el comunicado de 2018 enumera paraderos de C84/M86/D81 hacia el norte y K86/M81/M84/L82 hacia el sur; el esquema KR7 documenta la familia L80/M80, H81/M81, L82/M82, D83/L83, C84/M84, L85/M85 y K86/M86. Es evidencia de operación publicada, pero las páginas históricas no garantizan vigencia 2026.

## Límites para el modelo

- `station-maps/api/map`: publicado para localización visual relativa y color de troncal. No contiene rutas, correspondencia ruta→vagón, accesos, puertas, longitud/ancho de estación ni paradas en calle.
- API de rutas: publicada para servicio, fechas, horarios y secuencia de paraderos. No contiene asignación de vagón, puerta, geometría de plataforma ni coordenadas geográficas en las respuestas probadas.
- No encontrado en las muestras: calendario operacional semanal más detallado que `tipoDia`/inicio/fin; posición de parada por carril; una capa pública que relacione cada servicio con vagón o puerta; una lista vigente de todos los duales de Carrera 7 en el mismo endpoint consultado.
- Para la simulación: usar las posiciones/secuencia de paraderos como datos publicados; tratar el desplazamiento 2D, carril, vagón y puerta como estimaciones explícitas. No convertir `posicion` (metros de recorrido del servicio) en coordenada geográfica.

## Fuentes consultadas

- Plano oficial: https://tramites.transmilenio.gov.co/plano-estaciones-portales-transmilenio
- API del plano: https://tramites.transmilenio.gov.co/station-maps/api/map
- Buscador oficial: https://buscador-rutas.transmilenio.gov.co/rutas/1316/P85/TransMilenio/AK%2068%20-%20CL%209
- API P85: https://ms-transmiapp-rm2xahnybq-uk.a.run.app/api/v1/rutas/1316/P85/ y `/paraderos`
- API M85: https://ms-transmiapp-rm2xahnybq-uk.a.run.app/api/v1/rutas/4596/M85/ y `/paraderos`
- Comunicado oficial sobre MP85: https://portalold.transmilenio.gov.co/publicaciones/154848/bogota-estrena-la-ruta-mp85-primer-servicio-de-la-troncal-avenida-68/index.html
- Esquema oficial KR7: https://www.transmilenio.gov.co/files/1605e912-531c-4aa4-9e32-70c3d7141725/b31624d5-4bd5-4a9f-ba61-9ba458d670b2/esquema_de_servicios_troncales_kr7.pdf
- Paraderos duales Carrera 7 (2018): https://www.transmilenio.gov.co/comunicaciones/publicaciones/2018/la-carrera-septima-tendra-mas-paraderos

## Clasificación

- **oficialpublicado:** JSON y atributos descritos arriba, fechas/horarios/paraderos y colores tal como los entregaron los endpoints.
- **estimación:** cualquier geometría 2D local, carril, ubicación precisa de puerta/vagón y correspondencia con plataformas.
- **noencontrado:** asignación ruta→vagón/puerta y coordenadas geográficas de los paraderos en las respuestas muestreadas.
