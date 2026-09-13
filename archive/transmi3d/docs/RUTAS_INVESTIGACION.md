# Buscador de rutas: primer examen técnico

Consulta del 9 de septiembre de 2026. Fuente: [buscador oficial](https://buscador-rutas.transmilenio.gov.co/rutas). El cliente público observado utiliza `https://api.buscador-rutas.transmilenio.gov.co` para tipos de servicio, troncales, estaciones y búsqueda paginada de rutas. `tools/audit_routes.py` reproduce la consulta y guarda únicamente campos de transporte; omite metadatos administrativos.

La búsqueda con `activa: true, tipo: TransMilenio`, orden `idCodigo,asc`, devolvió **256 registros con IDs distintos** en seis páginas. No equivalen a 256 rutas troncales jugables ni a 256 códigos diferentes. El filtro ofrece también códigos con guion como `10-1` y el registro numérico `16` sin troncal asignada. Los códigos 1–8 aparecen, pero una clasificación de “rutas fáciles” requiere comprobar sus recorridos; no se ha deducido la categoría de todos los códigos numéricos.

Hay más de un registro con el mismo código. Por ejemplo, F23 aparece con destinos P. Américas y Banderas. Conservar IDs y comprobar si se trata de variantes, periodos, sentidos u otra distinción; no fusionarlos automáticamente. Las fechas `fechaDesde` y `fechaHasta` se preservan tal como llegan. La descarga no garantiza continuidad futura ni que los límites de fecha representen instantes UTC de operación.

El catálogo de troncales también enumera Avenida 68, Avenida Ciudad de Cali y TransMICable. **Aparecer en una lista no demuestra que una obra esté terminada, que toda una infraestructura esté habilitada ni que sea una vía para buses.** El objetivo jugable sigue siendo la operación de buses del sistema BRT y sus conexiones pertinentes.

## Próxima integración

1. Seleccionar un patrón que atraviese el piloto y consultar sus paradas ordenadas en ambos sentidos.
2. Contrastar fecha, variante y recorrido con mapa digital y comunicados.
3. Relacionar las paradas con estaciones, vagones y anclajes físicos revisados.
4. Vincular el itinerario al grafo de carriles habilitados para la fecha del escenario.
5. Ofrecerlo en el selector solo cuando su cobertura sea transitable; usar un nombre explícito de práctica si se habilita únicamente un fragmento.

Los candidatos están en `data/research/<fecha>/route_candidates.json`, con manifest y hashes. Son datos de investigación y el juego funciona sin consultarlos. La licencia de este endpoint aún no está establecida; no heredar automáticamente CC BY 4.0 de las capas geográficas ni incluir sus PDFs o imágenes en una futura distribución sin revisar su procedencia.
