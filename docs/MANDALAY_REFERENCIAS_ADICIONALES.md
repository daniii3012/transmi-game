# Mandalay: esquema oficial y referencia aérea

Revisión: 9 de septiembre de 2026. Complementa ESTACION_MANDALAY.md. La fecha de descarga no demuestra la vigencia física u operativa de los elementos.

## Esquema poligonal de TransMilenio

Fuente: [ESQUEMAS ESTACIONES, capa 0](https://gis.transmilenio.gov.co/arcgis/rest/services/Troncal/consulta_esquemas_estaciones/FeatureServer/0). Referencia original EPSG:3116; consulta guardada en WGS84. Se conserva la respuesta completa de los nueve polígonos de Mandalay, metadatos y hashes en data/research/mandalay_scheme_20260909/. La consulta reproducible está en su manifest.json; tools/fetch_mandalay_scheme.py reutiliza esa instantánea.

| secciontipo | Cantidad | objectid |
|---|---:|---|
| Vagon | 4 | 27, 120, 218, 426 |
| Externa | 1 | 287 |
| Conexa | 1 | 333 |
| Conexion | 1 | 538 |
| Transicion | 1 | 1040 |
| Entrada | 1 | 1073 |

Las cuatro secciones Vagon corresponden a dos franjas paralelas con dos módulos longitudinales cada una. Sus áreas publicadas están entre 165 y 202 m². La sección Conexion abarca una zona central de aproximadamente 2.049 m² y se solapa parcialmente con otras secciones; debe unirse geométricamente antes de generar una superficie.

**Hay campos contradictorios.** Por ejemplo, objectid 120 tiene tipo «Vagon 1 W-E», nombre «Transicion 1 N-S» y secciontipo «Vagon». El 538 tiene tipo «Conexion» y nombre «Vagon 2». No generar nombres, número de vagón, nomenclatura A/B ni servicios automáticamente desde nombre o id_vagon. Los sufijos E-W y W-E de tipo orientan una hipótesis de circulación que se debe contrastar con las calzadas y referencias visuales.

Las huellas permiten una reconstrucción provisional mucho mejor que el punto de estación con ancho publicado de 3 m. No son un levantamiento constructivo: faltan alturas, bordes de embarque certificados, posición y número de puertas, torniquetes y accesos actuales. La sección Externa 287 cruza parte de la calzada norte; su función física queda pendiente y no debe extruirse como obstáculo por defecto.

Copyright declarado: TransMilenio S.A. **No se ha establecido una licencia de reutilización para este servicio**; no heredar CC BY 4.0 de las seis capas geográficas anteriores. Conservar esta procedencia para la revisión de recursos previa a una distribución futura.

## Ortofoto oficial de referencia

Fuente: [SIMUR, Ortofoto_2021_Bogota_rgb](https://sig.simur.gov.co/arcgis/rest/services/Ortofoto/Ortofoto_2021_Bogota_rgb/MapServer). Se inspeccionó una exportación acotada de 380 × 190 m aproximadamente alrededor de la estación. El nombre del servicio indica 2021; no se ha verificado la fecha concreta del vuelo. La imagen se mantiene como referencia de trabajo, no como textura del juego ni prueba del estado de 2026.

La vista aérea respalda dos franjas de cubierta, una zona central amplia con caminos y vegetación, calzadas BRT a ambos lados y tráfico mixto por fuera. Se observa un puente peatonal cerca del extremo oriental y rampas de acceso. Su altura, pendientes y medidas no se obtienen de esta imagen; cualquier reconstrucción vertical será estimada hasta contar con otras referencias.

Exportación y petición con hash en ../../work/mandalay/ortofoto_2021.png y ortofoto_2021.request.json, fuera del repositorio. La geometría principal se toma de vectores, sin extraer modelos del visor ni incorporar imágenes externas a los materiales.

## Referencia fotográfica histórica

La ficha [Mandalay Transmilenio.JPG](https://commons.wikimedia.org/wiki/File:Mandalay_Transmilenio.JPG) declara autor Felipe Restrepo Acosta, 20 de octubre de 2010 y CC BY-SA 3.0. Sirve como referencia histórica adicional; no se incorpora al juego. No confundir una plataforma elevada con una estación construida sobre un viaducto, ni utilizar una fotografía sin escala para fijar cotas.

## Siguiente integración

Conservar las cuatro huellas Vagon y la zona central, modelar cubiertas y cerramientos con alturas explícitamente provisionales, y configurar puntos de práctica en ambos sentidos. Los anclajes de puertas se ajustarán al bus de ensayo: no representan posiciones verificadas de puertas reales ni paradas comerciales. Proteger la estación y el acceso de cualquier compresión longitudinal; reducir solo el contexto intermedio. Boyacá sigue fuera de circulación hasta verificar sus niveles.
