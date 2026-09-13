# Sondeo de detalles de rutas — 2026-09-10

Consulta HTTP de solo lectura al buscador oficial de TransMilenio. La evidencia resumida está en `probe.json`; no se guardó el catálogo completo ni datos administrativos o personales.

## Contrato verificado

- Enumeración observada en el auditor previo: `POST https://api.buscador-rutas.transmilenio.gov.co/api/v1/rutas/buscar?page=N&size=50&sort=idCodigo,asc`, cuerpo `{ "activa": true, "tipo": "TransMilenio" }`. La auditoría previa registró 256 filas e IDs distintos en seis páginas. La muestra actual usa ese catálogo ya capturado.
- El frontend actual también consulta `POST https://api.buscador-rutas.transmilenio.gov.co/api/v1/rutas/troncales` con cuerpo `{}`. La respuesta del 2026-09-10 tuvo **116 registros** y solo los campos `id`, `codigo`, `nombre`, `color` (hash en `manifest.json`). Esto contrasta la cifra 116 con el mapa digital: es un conteo de objetos devueltos por ese endpoint, no una prueba de 116 corredores físicos, rutas jugables o duales.
- Detalle por ID: `GET https://api.buscador-rutas.transmilenio.gov.co/api/v1/rutas/{id}/rutaDetalle`.
- Respuesta de detalle: claves `color`, `nombre`, `estaciones`, `horario`, `trazado`.
- `trazado`, cuando existe, es GeoJSON `LineString` con pares `[longitud, latitud]`; en los ocho casos hubo aridad 2. El conteo fue 552–1.330 coordenadas salvo el registro sin geometría (M86 Ciclovía, ID 5490).
- `estaciones` conserva el orden del recorrido en la muestra. Cada parada tiene `id`, `codigo`, `nombre`, `direccion`, `posicion`, `sistema`, `color`; `posicion` está en metros y fue monótona creciente en los ocho detalles.
- `horario` contiene `id`, `tipoDia`, `inicio` y `fin`. Es una ventana horaria por tipo de día; no es una frecuencia.

## M85, P85 y Séptima

El catálogo previo contiene dos registros para M85 (IDs 1315 y 4596) y dos para P85 (IDs 1316 y 4595). Los pares base/Ciclovía comparten muchas paradas, pero tienen IDs, nombres, horarios y, en algunos casos, longitud de trazado distintos. M86 muestra el mismo patrón (IDs 1185 y 5490), y el segundo carece de `trazado`. En la respuesta de `troncales` de 116 objetos solo aparecieron M47, M51 y M83 entre los códigos que empiezan por M/P; por tanto, ese endpoint no es intercambiable sin más con el catálogo de rutas auditado.

En los registros inspeccionados no aparece una etiqueta o campo que diga `dual`, `vagón`, `plataforma` o `tipo de bus`. Los códigos de Carrera 7 presentes en el catálogo (M82, M83, M84, M85, M86 y M47/M51) demuestran asociación de troncal y recorrido publicado, pero no prueban por sí mismos “duales Séptima”. La cifra 116 no puede derivarse de estos ocho detalles ni de la mera cantidad de IDs; debe contrastarse contra el mapa digital y la cobertura de paradas/segmentos.

## Lagunas para la simulación 2D

El endpoint no entrega frecuencia/headway, composición del bus, tipo de vehículo, asignación de vagón, plataforma, lado de puertas ni una marca explícita de sentido. Para una integración jugable todavía hay que decidir cómo mapear `posicion` y la línea a carriles, verificar continuidad de la geometría y contrastar fechas de vigencia y calendario con el escenario. No asumir equivalencia entre ID, código visible, nombre y ruta física.
