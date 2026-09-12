# Geometría física de todos los portales — 2026-09-11

Se completó el inventario físico de los doce portales/estaciones presentes en
`app/dist/services.json`: nueve portales y las tres estaciones intermedias
Ricaurte, Avenida Jiménez y Banderas. El resultado conserva el esquema
`station_id`, `platforms`, `areas` e `internal_lines`; cada vector conserva el
enlace OSM, tipo/ID, etiquetas, relación de origen, centroide y medidas en
metros.

## Método y procedencia

La consulta Overpass del snapshot anterior no estaba disponible durante esta
captura. Para evitar sustituir geometría por estimaciones se usó la API OSM
0.6 (`relation/{id}/full` para relaciones de estación y `map?bbox=...` para
vías internas y nodos de plataforma), con User-Agent del proyecto, el
2026-09-11. Los miembros de relaciones se resolvieron por sus nodos OSM; un
nodo `stop_position` quedó como punto y nunca se convirtió en polígono.

Los elementos se proyectaron mediante la proyección AEQD de `tools/geo.py`.
Las vías internas se limitaron a 220 m del centro de cada portal, con
`highway=service|busway`, excluyendo `service=parking_aisle`; llevan
`confidence=high` cuando OSM identifica TransMilenio/busway y `medium` para
servicio sin esa etiqueta. Las cubiertas y los edificios de ingreso siguen
siendo `areas` y no se mezclan con las plataformas.

Snapshot reproducible:

- `data/raw/station_layouts/20260911T120000Z/overpass.json`
- SHA-256: `16b2e6bf16d78e4eabf50b1f20cf182e853d14abf34270037d2f5f3003ccf02d`
- 1.173 elementos OSM combinados (snapshot previo de seis layouts más las
  relaciones y vectores nuevos).
- Relaciones nuevas: [Portal Norte 19124486](https://www.openstreetmap.org/relation/19124486),
  [Portal 80 20085224](https://www.openstreetmap.org/relation/20085224),
  [Portal Eldorado 13621068](https://www.openstreetmap.org/relation/13621068),
  [Portal Tunal 20085223](https://www.openstreetmap.org/relation/20085223),
  [Portal Usme 20085222](https://www.openstreetmap.org/relation/20085222) y
  [Portal 20 de Julio 8237821](https://www.openstreetmap.org/relation/8237821).

## Conteos y fuentes físicas

| station_id | estación | elementos de parada/plataforma | áreas | líneas internas | plataformas/edificios corroborados |
|---|---|---:|---:|---:|---|
| 2000 | Portal Norte - Unicervantes | 5 | 1 | 19 | nodos `13111167400`, `13111232401`, `13111232403`, `13111232404`, `13111232405`; área `1386008597` |
| 4000 | Portal 80 | 7 | 1 | 37 | plataformas `500300855`, `500300848`; ingreso `944879700` |
| 7000 | Portal Sur - JFK Coop. Financiera | 27 | 1 | 38 | layout existente preservado |
| 3000 | Portal Suba | 11 | 1 | 23 | layout existente preservado |
| 5000 | Portal Américas | 27 | 4 | 31 | layout existente preservado |
| 5100 | Banderas | 13 | 1 | 9 | layout existente preservado |
| 6000 | Portal El Dorado – C.C Nuestro Bogotá | 7 | 2 | 19 | `1423708575` (Plataforma Alimentadores 2); áreas `1423708569`, `1423708572` |
| 7111 | Ricaurte | 0 | 9 | 2 | layout existente preservado; OSM no ofrece polígonos de plataforma corroborados |
| 8000 | Portal Tunal | 2 | 2 | 20 | `1423396691` (Plataforma 1), `1423396692` (Plataforma 2); ingreso `563911785`; cicloparqueadero `660551565` |
| 90004 | Portal Usme | 2 | 1 | 17 | `404795978` (Plataforma 1), `404795977` (Plataforma 2); ingreso `404795976` |
| 9110 | Avenida Jiménez | 0 | 5 | 8 | layout existente preservado; OSM no ofrece polígonos de plataforma corroborados |
| 10000 | Portal 20 de Julio | 2 | 4 | 23 | `394185448` (Plataforma Troncales), `509700109` (Plataforma Alimentadores); ingreso `183580319`; cubiertas `1385164918`, `1385164919`, `1385164920` |

Los polígonos nuevos están enlazados en los propios objetos de
`data/curated/station_layouts.json`. Como comprobación puntual, las etiquetas
OSM de las plataformas 80, Tunal y Usme son `building=bus_station` o
`building=yes`; la plataforma alimentadora de El Dorado y las dos de 20 de
Julio también están vinculadas a sus relaciones de estación. El área de Portal
Norte es la relación multipolígono OSM; allí la fuente abierta expone cinco
`stop_position` de TransMilenio, pero no una huella de plataforma nombrada.

## Límites conocidos

Portal Norte queda utilizable con cinco puntos de parada reales y un área OSM,
pero no se inventó una plataforma rectangular a partir de esos puntos. Para
Ricaurte y Avenida Jiménez se conserva el resultado previo, que documenta
áreas y ejes cercanos sin asignar artificialmente una plataforma. Las líneas
internas son las vías OSM disponibles dentro del radio; no representan
necesariamente cada carril operativo ni el sentido de circulación de la
operación real.

Artefactos generados:

- `data/curated/station_layouts.json` — SHA-256
  `361c4acb0ae079952779163d41d2921f1262e7f160c10996dee4a2df393db3f5`.
- `app/dist/station_layouts.json` — mismo contenido y SHA-256.


Los 103 elementos de `platforms` incluyen nodos y líneas de parada: no equivalen a 103 plataformas físicas. En la aplicación hay 191 de 201 visitas a estas doce estaciones que admiten una posición compatible con la geometría disponible. Las diez restantes conservan la referencia de la ruta; no se desvían buses ni se inventan conexiones para forzar el ajuste.
