# Cómo se obtuvieron los datos y cómo actualizarlos

Este documento es el procedimiento para mantener el simulador al día cuando cambie
la realidad: un trazado nuevo, una estación movida, una calzada reconstruida, un
semáforo distinto o un horario republicado. Explica de dónde sale cada dato, con qué
herramienta, y qué hay que ejecutar y revisar para reemplazarlo.

Complementa a [OPERACION_Y_DATOS.md](OPERACION_Y_DATOS.md), que describe el modelo y
sus hipótesis, y a [FUENTES.md](FUENTES.md), que registra procedencia y licencias.

## Reglas que no cambian

1. **La descarga y la curación están separadas.** Un script `fetch_*` solo guarda una
   instantánea cruda con su manifiesto y SHA-256. Un script `build_*` solo lee esa
   instantánea y produce el dato curado. Ningún script descarga por su cuenta al jugar.
2. **Las instantáneas no se sobrescriben.** Cada descarga crea una carpeta nueva
   `AAAAMMDDTHHMMSSZ` bajo `data/raw/`. Las anteriores se conservan: son la evidencia
   de lo que se afirmó en su momento.
3. **El nombre de la carpeta es un identificador, no la hora de consulta.** La hora
   real está en `queried_at` dentro del manifiesto.
4. **Nunca se inventa geometría.** Si la fuente no publica un trazado, el registro
   queda pendiente. No se unen paradas con líneas rectas ni se deducen recorridos por
   cercanía. Lo mismo aplica a plataformas: un punto de parada no se convierte en un
   polígono.
5. **Lo publicado y lo estimado se distinguen siempre**, en el dato y en la interfaz.
6. **Cada cambio de fuente se acompaña de pruebas.** Ver *Comprobación obligatoria*.

## Entorno

```sh
../../work/venv/bin/python --version   # Python con shapely y pyproj
node --version                         # Node en el PATH
```

El Python del sistema sirve la web pero no trae las bibliotecas geográficas. En este
equipo el intérprete con shapely/pyproj está en `../../work/venv/bin/python`, y así
aparece en los comandos de abajo. Las herramientas que no proyectan coordenadas
funcionan con `python3`. Todos los comandos se ejecutan desde la raíz del proyecto.

## La cadena de datos

```
fuente oficial  ──fetch_*──▶  data/raw/<instantánea>/  ──build_*──▶  data/curated/  ──▶  app/dist/
                              manifiesto + SHA-256                    + data/processed/ (auditorías)
```

`app/dist` es lo que sirve el navegador. Para los archivos que existen en los dos
lados, la copia de `app/dist` debe ser byte a byte idéntica a la de `data/curated`;
los `build_*` escriben ambas.

| Dato | Fuente | Descarga | Curación | Resultado |
|---|---|---|---|---|
| Rutas, paradas, horarios, trazados, colores | Mapa digital y API buscador de TransMilenio | `fetch_services.py`, `fetch_service_supplement.py` | `build_services.py` | `app/dist/services.json` |
| Paraderos de calle de los duales | Capa oficial de paraderos SITP | `fetch_dual_stops.py` | (lo consume `build_services.py`) | dentro de `services.json` |
| Contexto urbano: vías, parques, agua | OpenStreetMap / Overpass | (consulta registrada en `data/raw/context`) | `build_context.py` | `app/dist/context.json` |
| Geometría física de estaciones y portales | OpenStreetMap API 0.6 y Overpass | `fetch_station_layouts.py` | `build_station_layouts.py` | `app/dist/station_layouts.json` |
| Semáforos en calzada de buses | OpenStreetMap API 0.6 | `fetch_busway_signals.py` | `build_busway_signals.py` | `app/dist/busway_signals.json` |
| Calzada y carriles de TransMilenio | OpenStreetMap / Overpass | `fetch_busway_lanes.py` | `build_busway_lanes.py` | `app/dist/busway_lanes.json` |
| Demanda de pasajeros | Validaciones diarias SITP, Datos Abiertos Bogotá | descarga manual del ZIP | `aggregate_validations.py` y luego `import_passenger_profiles.py` | `app/dist/demand.json` |
| Three.js | npm oficial, versión fijada | `vendor_three.py` | — | `app/dist/vendor/` |

Herramientas de solo lectura que no escriben en el catálogo: `audit_routes.py`
(contrasta el buscador público) y `probe_pending_routes.py` (revisa si los registros
pendientes ya tienen trazado publicado).

## Actualizar según lo que cambió

### Cambian rutas, horarios, paradas o trazados

Es el caso más frecuente: TransMilenio republica el catálogo con vigencias nuevas.

```sh
python3 tools/fetch_services.py
python3 tools/fetch_service_supplement.py
python3 tools/fetch_dual_stops.py
```

Cada uno crea su carpeta nueva bajo `data/raw/`. **La descarga no basta:** hay que
apuntar la curación a la instantánea nueva editando el puntero correspondiente.

```sh
cat data/raw/services/latest.json      # {"snapshot": "20260910T185326Z"}
cat data/raw/dual_stops/latest.json
```

Cambia el campo `snapshot` por el nombre de la carpeta nueva. Después revisa la
curación en `data/curated/services.json`, que es donde viven las decisiones humanas:

- `excluded`: registros que no entran y por qué. Hoy están la C15 zonal (366) y la
  F23 de Banderas (10082), ambas por indicación expresa de Daniel.
- `pairs`: qué identificadores son los dos sentidos de un mismo servicio. Nunca
  copian geometría ni activan registros pendientes.

Si el catálogo nuevo trae identificadores distintos, esas reglas hay que revisarlas
antes de reconstruir. Luego:

```sh
../../work/venv/bin/python tools/build_services.py
```

Escribe `app/dist/services.json` y la auditoría `data/processed/services_audit.json`.
Un registro queda `ready:false` cuando le falta trazado, cuando la secuencia de
paradas es insuficiente, cuando una referencia de parada queda a más de 1.200 m del
tramo publicado, o cuando una variante Ciclovía trae calendario ambiguo. Esos casos
**se dejan pendientes**: ver [PENDIENTES_20260911.md](PENDIENTES_20260911.md).

Como los semáforos se asocian a los recorridos, después de cambiar `services.json`
hay que recurar las señales y regenerar su auditoría (ver más abajo) aunque la descarga
de OSM no haya cambiado.

#### Reimportar unos pocos registros sin rehacer el catálogo

Cuando un registro concreto gana trazado, o llegó recortado, no hace falta —ni
conviene— volver a bajar el catálogo entero: eso cambiaría todos los demás al mismo
tiempo.

```sh
python3 tools/refresh_route_details.py 12444 1213 629 --reason "por qué"
../../work/venv/bin/python tools/build_services.py
```

Descarga el detalle publicado solo de esos identificadores a
`data/raw/services/refresh_<instantánea>/`, con manifiesto y SHA-256 por respuesta, y
deja el puntero `data/raw/services/refresh_latest.json`. `build_services.py` prefiere
ese detalle para esos identificadores y **toma el resto de la metadata, vigencia
incluida, de la instantánea base**. Cada ruta queda con `detail_snapshot`, que dice de
qué carpeta salió su detalle. Para volver atrás basta borrar el puntero.

### Cambia la ubicación o la geometría física de una estación o un portal

```sh
python3 tools/fetch_station_layouts.py --radius-m 450
../../work/venv/bin/python tools/build_station_layouts.py
```

La lista de estaciones a consultar está en el diccionario `STATIONS` dentro de
`fetch_station_layouts.py`, con su `station_id` y su coordenada. Para incluir una
estación nueva se agrega ahí, con el identificador que usa `services.json`. La
consulta filtra `public_transport=platform|stop_position|station|stop_area`, vías
`highway=busway|service` y `railway=platform|service`, y acota las relaciones de
estación por nombre para no arrastrar las del Metro.

`build_station_layouts.py` toma la instantánea más reciente de
`data/raw/station_layouts/` salvo que se le pase `--raw`. Proyecta a metros con la
AEQD de `tools/geo.py`, limita las vías internas a 220 m del centro de cada estación,
descarta `service=parking_aisle`, y separa lo que es plataforma de lo que es cubierta
o edificio de ingreso. Marca `confidence=high` cuando OSM identifica TransMilenio o
busway, y `medium` para servicio sin esa etiqueta.

En la aplicación, `station-layouts.mjs` sitúa cada visita de una ruta sobre la
geometría disponible. Si una visita no admite una posición compatible, conserva la
referencia oficial del servicio: no se desvía la ruta para forzar el ajuste.

### Cambian las calzadas de TransMilenio o sus semáforos

```sh
python3 tools/fetch_busway_signals.py --services app/dist/services.json
../../work/venv/bin/python tools/build_busway_signals.py --raw data/raw/busway_signals/<instantánea>
node tools/build_signal_associations.mjs
```

El último comando regenera `data/processed/signal_associations.json` reutilizando el
emparejador del motor, `matchSignals`, para no tener dos definiciones de qué cuenta como
coincidencia. **Hay que ejecutarlo también cuando cambien las rutas y no los semáforos**,
porque la asociación depende de las dos cosas. Ese archivo nació sin generador y quedó
desactualizado en silencio hasta el 11 sep. 2026.

`build_busway_signals.py` acepta `--docs` para emitir un resumen generado, pero por
defecto **no escribe documentación**: `SEMAFOROS_20260911.md` se mantiene a mano y el
generador solo produce un esbozo corto que lo reemplazaría entero. Si usas `--docs`,
apúntalo a un archivo aparte.

La descarga cubre la red en celdas de 0,005° derivadas de los puntos de
`services.json`, y amplía la evidencia pidiendo el `way/full` de cada vía candidata y
el nodo de cada semáforo, porque la tangente local se calcula con los nodos vecinos
reales de la vía, no uniendo semáforos lejanos.

Un semáforo se acepta por uno de dos caminos, que se registran por separado en el campo
`carriageway` de cada señal:

- **`busway`**: el nodo pertenece directamente a una vía `highway=busway`, o a una
  `highway=service` con identificación explícita de TransMilenio o acceso exclusivo de
  buses.
- **`street`**: el nodo pertenece a una vía ordinaria abierta a buses y cae dentro de la
  tolerancia de un tramo de calle de un servicio dual. Solo aplica donde el servicio deja
  la troncal; en un corredor troncal los carriles mixtos van paralelos a pocos metros y
  aceptarlos sumaría semáforos que no controlan la calzada del bus.

Las reglas están en `tools/busway_criteria.py`, compartido por el descargador y el
curador para que no se desincronicen. **La cercanía no basta** y los rechazados quedan en
la auditoría del JSON curado. Para activarlo en un recorrido se exige además
distancia ≤12 m (`--max-distance-m`), coseno de tangente ≥0,87 en valor absoluto, y
respeto de `oneway` y `traffic_signals:direction` cuando existen.

OSM no publica fases ni coordinación: el ciclo de 90 s (52 verde, 3 amarillo, 35 rojo)
es un parámetro de escenario declarado como estimado, con desfase reproducible por ID.
Si algún día hay fases oficiales, se cambian ahí y se documenta la fuente.

Detalle completo en [SEMAFOROS_20260911.md](SEMAFOROS_20260911.md).

### Cambia el contexto urbano del mapa

```sh
../../work/venv/bin/python tools/build_context.py
```

Conserva los polígonos reales y las etiquetas explícitas `bridge`, `tunnel`, `layer`
y `junction`. Un cruce de líneas nunca crea una conexión ni un giro.

**Limitación conocida:** este es el único dato sin descarga automatizada. No existe un
`fetch_context.py`; la consulta Overpass del 10 sep. 2026 se hizo a mano y quedó
archivada en `data/raw/context/20260910/osm_overpass_raw.json`. Peor aún, esa ruta está
escrita directamente dentro de `build_context.py`, así que para usar una instantánea
nueva hay que crear la carpeta, guardar la respuesta con su manifiesto y editar la ruta
en el script. Antes de la próxima actualización del contexto conviene escribir el
`fetch_context.py` que falta y cambiar la ruta fija por el mismo puntero `latest.json`
que usan servicios y paraderos.

### Llegan datos nuevos de pasajeros

Descarga los ZIP oficiales a un directorio de trabajo **fuera del repositorio**. La
demanda vigente se mide sobre 17 días; para actualizarla conviene bajar semanas completas
de lunes a domingo, para que cada tipo de día tenga varios representantes:

```sh
python3 tools/aggregate_validation_period.py /ruta/validacionTroncal*.zip
python3 tools/import_passenger_profiles.py
```

El agregado de periodo produce un perfil horario por estación **y tipo de día**, con la
media de los días observados, su desviación, mínimo y máximo. El importador lo prefiere
automáticamente; si no existe, vuelve al agregado de un solo día que produce
`tools/aggregate_validations.py`, y en ese caso el motor retoma los factores estimados de
fin de semana. Detalle y límites en [DEMANDA_MULTIDIA_20260911.md](DEMANDA_MULTIDIA_20260911.md).

Un archivo diario trae unas pocas transacciones con fecha del día anterior o del
siguiente, de servicio que cruza medianoche. Se cuentan bajo el día de servicio del
archivo y el reparto queda registrado en `transaction_dates`.

El agregador valida formato y fechas antes de escribir, y solo exporta estación,
hora, totales y procedencia. **Nunca se añaden el ZIP ni el CSV crudo a Git**; el
agregado versionado basta para reproducir.

### Revisar si un registro pendiente ya se puede activar

```sh
python3 tools/probe_pending_routes.py
```

Consulta el detalle oficial de cada registro pendiente y archiva la evidencia en
`data/research/pending_probe_<instantánea>/`. No toca el catálogo: dice cuáles tienen
ya trazado y paradas publicados. Activarlos sigue exigiendo una instantánea nueva de
servicios y una decisión explícita de curación.

## Comprobación obligatoria después de cualquier actualización

```sh
node --test app/tests/*.test.mjs
../../work/venv/bin/python -m unittest discover -s tests
node app/tests/operation-benchmark.mjs --save
node app/tests/operation-benchmark.mjs --stress --save
git diff --check
```

Además, a mano:

1. **Paridad**: `shasum -a256 data/curated/X.json app/dist/X.json` debe coincidir para
   `station_layouts.json` y `busway_signals.json`.
2. **Hashes de las fuentes crudas** contra su manifiesto, incluidos los XML de detalle.
3. **Conteos**: registros totales, utilizables y pendientes; señales aceptadas y
   asociadas; elementos de plataforma, áreas y líneas internas. Si un conteo cambia,
   se actualiza en la documentación que lo cite. No dejar cifras viejas.
4. **Versión de caché**: subir el sufijo `?v=` en `app/dist/*.mjs` e `index.html` si
   cambió código, para que los navegadores no sirvan una mezcla de versiones.
5. **Navegador**: abrir con `ABRIR_SIMULACION_2D.command`, comprobar que no hay errores
   de consola y que las cifras coinciden con el benchmark de Node.
6. **Vigencias**: si la instantánea nueva trae vigencias que vencen pronto, recordar
   que el simulador sigue operando después de esa fecha y lo rotula como *horario
   vencido*. El control está en Operación y el detalle en
   [PLANIFICADOR.md](PLANIFICADOR.md).

## Qué sigue siendo decisión humana

Ningún script decide estas cosas; se revisan y se anotan en la documentación:

- Qué registros se excluyen y por qué.
- Qué identificadores son dos sentidos del mismo servicio.
- Si una variante con calendario ambiguo reemplaza o no las salidas de su familia.
- Qué tipo de vehículo se asume donde no hay asignación publicada.
- Qué se considera evidencia suficiente para activar un registro pendiente.

Mantener esas decisiones visibles es lo que permite que dentro de un año se sepa qué
se midió, qué se supuso y qué cambió.
