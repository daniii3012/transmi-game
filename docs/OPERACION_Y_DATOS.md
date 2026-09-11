# Operación, datos y reproducción

Entrega local revisada el 11 de septiembre de 2026. Los archivos de la aplicación incluyen origen, fecha, identificadores y hashes. Las fuentes oficiales no incluyen todos los parámetros necesarios para una simulación; las siguientes distinciones son parte del modelo.

## Fuentes incorporadas

| Fuente | Uso y evidencia |
|---|---|
| [Mapa digital de TransMilenio](https://mapadigital.transmilenio.gov.co/) y API buscador | 116 registros/100 códigos en el mapa, detalles por ID, horarios, vigencia, trazados, colores y estaciones. Instantánea `data/raw/services/20260910T185326Z`; catálogo ampliado original de 132. |
| Suplemento del buscador | 7 registros adicionales D81/L81, H83 y F63/Z63 en `data/raw/services/supplement_20260910`; no se sobrescribe la instantánea base. |
| [C15, paraderos, ID 3915](https://ms-transmiapp-rm2xahnybq-uk.a.run.app/api/v1/rutas/3915/C15/paraderos), [H15, ID 367](https://ms-transmiapp-rm2xahnybq-uk.a.run.app/api/v1/rutas/367/H15/), [H15, paraderos](https://ms-transmiapp-rm2xahnybq-uk.a.run.app/api/v1/rutas/367/H15/paraderos) | Contraste solicitado por Daniel, 19 paradas por sentido. Evidencia en `data/research/c15_h15_20260910`. La C15 Chapinero Ciclovía ID 366 es zonal y queda excluida mediante `data/curated/services.json`. |
| Capa oficial de paraderos SITP | Solo coordenadas de paraderos usados por duales, sin añadir rutas zonales. Endpoint, respuesta, consulta y hashes en `data/raw/dual_stops`. |
| [Validaciones diarias SITP, Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/validaciones-diarias-sitp) | La ficha declara CC BY 4.0. [Archivo oficial utilizado](https://storage.googleapis.com/validaciones_tmsa/ValidacionTroncal/validacionTroncal20260909.zip): 1.920.298 filas de validación y 151 códigos de recaudo. 1.920.284 tienen fecha 9 sep. y 14 son posteriores a medianoche, del 10 sep.; se conserva este desglose. |
| [Capacidades generales del sistema](https://www.transmilenio.gov.co/transmichiquis/la-entidad/servicios-del-sistema) | Referencia articulado 160 y biarticulado 250. [Modelo histórico de 240](https://www.transmilenio.gov.co/comunicaciones/publicaciones/2015/nuevo-modelo-de-bus-para-el-sistema-transmilenio); esta publicación es de 2015, aunque el sitio tenga fechas de actualización posteriores. |
| [Duales eléctricos articulados en 2026](https://bogota.gov.co/mi-ciudad/movilidad/bogota-pone-rodar-50-buses-duales-articulados-electricos-en-2026) y [operación de Ciudad de Cali](https://www.transmilenio.gov.co/comunicaciones/noticias-de-transmilenio/boletines-informativos/entra-operacion-extension-av-ciudad-cali) | Perfil publicado de F63/Z63 con capacidad 160. No se infiere que todos los duales sean padrones ni que todas las rutas tengan biarticulados. |
| [OpenStreetMap](https://www.openstreetmap.org/copyright), Overpass | Contexto fechado, ODbL 1.0, 15.573 elementos proyectados: vías principales, parques y agua. Etiquetas explícitas bridge/tunnel/layer/junction se conservan. `data/raw/context/20260910` contiene consulta y respuesta. |
| [Geometría de estaciones OSM](ESTACIONES_OSM_20260911.md) | Seis estaciones detalladas, consulta Overpass 11 sep. 2026, timestamp base del servidor 1 jun. 2026. Fuente y hashes conservados. [Plano secundario de Portal Sur](https://sitp-bogota.com/portal-del-sur-transmilenio/) consultado, sin extraer geometría de su imagen. |
| [Ley 51 de 1983](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=4954) | Festivos y traslados de descanso al lunes. Calendario implementado con Pascua y fechas civiles. |

La licencia de los endpoints de rutas y cartografía del mapa no está establecida en las respuestas consultadas; no se les asigna automáticamente la licencia de las capas GIS antiguas. Se conservan atribución y procedencia. La aplicación funciona localmente sin consultar esas APIs durante el juego.

## Normalización y cobertura

`tools/build_services.py` lee fuentes inmutables y curación explícita. Proyecta, ordena paradas, contrasta sus referencias con puntos cercanos y recorta la polilínea entre origen y destino. Busca la proyección local en ±650 m de la referencia para no saltar al otro sentido de un bucle. Solo ajusta al punto publicado si está a ≤250 m del tramo; diferencias mayores se documentan o bloquean según el umbral. Redondeo milimétrico de salida no implica precisión milimétrica del dato.

Los paraderos sin coordenada contrastada se interpolan sobre la ruta y se rotulan aproximados. Los trazados ausentes, referencias fuera de rango y calendarios Ciclovía ambiguos no se activan. M85 recorre su tramo real de unos 11,37 km, empezando a unos 9,65 km de su geometría bruta bidireccional. K86/629 tiene referencias hasta unos 44,7 km, incompatibles con un trazado de unos 5,94 km; se mantiene pendiente. El ramal de aeropuerto tiene identidad propia.

Tras excluir la zonal y F23/10082 Banderas (corrección de Daniel, 11 sep.) y añadir el suplemento: 137 registros, 114 utilizables, 103 códigos utilizables distintos, 23 pendientes. Los 114 son elegibles por fecha el 10 de septiembre; 112 tienen ventanas para ese jueves. Doce pendientes estaban vencidos. Las ventanas de una variante Ciclovía explícita reemplazan las coincidentes de su familia regular; las variantes ambiguas no suprimen silenciosamente un servicio regular.

## Hipótesis operativas

| Parámetro | Referencia inicial |
|---|---|
| Intervalo entre salidas | 4 min pico, 8 min valle; ajustable, con variación determinista de ±12% opcional |
| Pico entre semana | 06–09 y 16–20, o modo forzado |
| Crucero troncal / calle | 60 / 50 km/h ajustables; cada bus conserva una variación de −5, −2, 0, +2 o +5; calle en pico factor 0,82 |
| Aceleración / frenado | 0,8 / 1,1 m/s²; desaceleración por curvas estimada |
| Atención | Base 13 s troncal, 9 s calle; +4 s pico; abordajes a 2,5 personas/s y descensos a 3 personas/s |
| Regulación en terminal | 240 s; patio abstracto en el extremo, sin acceso físico inventado |
| Vagones | Cantidad publicada si existe, 2 como respaldo; asignación determinista estimada |
| Carriles y posiciones | Atención y paso independientes por sentido; 2 posiciones por vagón y 1 en calle |
| Flota | Sin un contador fijo de buses activos: resultado de salidas y duración; reutilización compatible por terminal/tipo |

Los horarios publicados se interpretan como ventanas de despacho, no como instante de desaparición del último bus. Un viaje puede terminar después del cierre.

## Pasajeros y clases de bus

La importación agrupa accesos equivalentes y temporales en 142 estaciones lógicas, mediante alias revisables en `data/curated/validation_stations.json`. No afirma que una estación temporal comparta coordenadas exactas con la permanente. Se enlazan 1.920.297 validaciones; una corresponde a Tunal Cable y se excluye. Los artefactos versionados no contienen tarjetas, dispositivos ni transacciones individuales.

El nuevo nivel de demanda 1× multiplica por 2,25 las entradas calculadas con el modelo anterior, tanto históricas como de respaldo. Se aplica después el control 0,25×–3×. El total histórico mostrado permanece sin multiplicar: las validaciones son entradas registradas por recaudo, no personas esperando ahora.

El perfil por hora se divide inicialmente entre dos sentidos y se modifica según orientación respecto a Centro Internacional como centro de empleo aproximado. Se aplica más demanda hacia el centro de 06–10 y hacia afuera de 16–20. Es una hipótesis de escenario, no una encuesta de empleo. Los sábados usan 0,7 y domingos/festivos 0,55 del perfil de referencia; otros días laborales reutilizan el único día observado. Paraderos sin observaciones usan pesos estimados.

Los pasajeros comparten una cola agregada por estación/sentido. La selección de una parte de la red recibe una proporción de la demanda según servicios atendidos, sin asignación OD individual ni transbordos explícitos. El destino de descenso es estimado; hay control de capacidad y abandono de espera con media de 30 min. La interpretación de estación/sentido único, patios y cierre de jornada requiere calibración posterior.

La capacidad es fija: padrón 80, articulado 160 y biarticulado 240, por decisión de Daniel. F63/Z63 conservan su tipo publicado de 160; demás duales usan padrón estimado. Las fáciles 1–8 son articuladas y M51/F51 biarticuladas según el usuario. Para servicios restantes se usa un criterio provisional estable: recorridos de al menos 18 km reciben biarticulados y los más cortos articulados. La longitud del recorrido no prueba el tipo real: esta asignación debe contrastarse, y no se deduce compatibilidad de puertas. No existe mezcla aleatoria ni selector de 250. El tipo no cambia al reutilizar un bus. Las longitudes de representación son 12, 18,5 y 27,2 m; requieren ficha por modelo antes de usarlas como ingeniería de andenes.

## Ajustes de la revisión del 11 de septiembre

Los refuerzos son una hipótesis opcional: en horas pico, para intervalos base de al menos 210 s, una minoría determinista de salidas (semilla módulo 7) puede recibir un bus adicional a los 120 s si la presión horaria por servicio supera 90% de su capacidad. No se añaden fuera de la ventana publicada ni cuando el intervalo ya es 2 min. El despacho normal continúa; pueden formarse grupos de dos o tres buses. La presión usa entradas históricas repartidas entre servicios, no una orden real del centro de control. No se fuerza que todos los pasajeros esperen cierto número de buses.

[Estaciones OSM y procedencia](ESTACIONES_OSM_20260911.md) documenta plataformas de Portal Sur, Suba, Américas y Banderas, y cubiertas/accesos de Ricaurte/Jiménez. Cada objeto conserva URL y etiquetas. Las áreas de estación no se presentan como plataformas verificadas. Una selección geométrica estima el punto de atención sobre la ruta existente: ventana de ±400 m, distancia lateral máxima 28 m y compatibilidad de eje cuando existe. Se limita además por las paradas vecinas. No se redirige el bus por una vía interna de OSM ni se cambia la polilínea oficial. Los puestos físicos encontrados tienen reservas separadas; la numeración de vagón y la ruta asignada a cada puesto siguen estimadas. En una visita a Jiménez no hay candidato compatible y se mantiene la referencia oficial. Otros portales y estaciones usan el respaldo esquemático de andenes, sin afirmar un plano real.

El mapa permanente usa colores de troncales. Los tramos tipo_tra=2 del mapa (incluida la Séptima exterior) se consideran corredores de calle de contexto, conservando esa clasificación de origen. Para los demás segmentos de calle se resta una franja de 18 m alrededor de los corredores ya dibujados a los trazados duales; el resultado se dibuja gris discontinuo. Las rutas seleccionadas conservan todos sus giros y su geometría exacta. Esta capa de contexto no cambia longitudes ni autoriza conexiones nuevas.

Los 23 registros de datos pendientes se mantienen por petición expresa. Los semáforos quedan pendientes: incorporar ciclos, coordinación y detenciones sin información suficiente añadiría una precisión aparente; el movimiento actual incluye curvas, paradas y congestión de atención, pero no fases semafóricas. También siguen pendientes OD, asignaciones reales de flota/vagones, planos de otras estaciones, patios e inventarios oficiales y recorridos en vacío.

## Reproducir sin volver a descargar

Desde la raíz del proyecto, con Python y shapely/pyproj instalados. En el equipo actual existe `../../work/venv/bin/python`:

```sh
../../work/venv/bin/python tools/build_services.py
../../work/venv/bin/python tools/build_context.py
../../work/venv/bin/python tools/build_station_layouts.py
python3 tools/import_passenger_profiles.py
node --test app/tests/*.test.mjs
../../work/venv/bin/python -m unittest discover -s tests
node app/tests/operation-benchmark.mjs --save
node app/tests/operation-benchmark.mjs --stress --save
```

Para regenerar el agregado de pasajeros, descarga el ZIP enlazado a un directorio de trabajo fuera de Git y ejecuta `python3 tools/aggregate_validations.py /ruta/validacionTroncal20260909.zip`. Después ejecuta el importador de perfiles. El agregador solo exporta estación, hora, totales y procedencia; valida formato y fechas antes de escribir. No añadir el ZIP ni el CSV crudo a Git.

Las nuevas descargas se hacen con `fetch_services.py`, `fetch_service_supplement.py` y `fetch_dual_stops.py`. Revisar sus manifests y actualizar el selector de instantánea y las reglas curadas antes de sustituir los datos de una versión. Los scripts de suplemento y perfiles reflejan expresamente esta fecha de entrega; no son un proceso automático de actualización diaria.
