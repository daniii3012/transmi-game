# Contexto cartográfico OSM para Transmi 2D

Descarga puntual de Overpass API (`osm_overpass_raw.json`) realizada el 2026-09-10, con el filtro reproducible en `overpass_query.txt`. Bbox consultado: sur 4.45, oeste -74.27, norte 4.84, este -73.99.

`app/dist/context.json` (generado con `tools/build_context.py`) es el derivado consumible por la aplicación: coordenadas proyectadas en metros mediante AEQD WGS84, origen `(-74.136, 4.63027)`, vértices redondeados a 0.1 m y simplificación Douglas–Peucker de 10 m. Incluye únicamente ways con `highway` motorway/trunk/primary/secondary, `waterway` river/canal, `natural=water` y geometrías disponibles de `leisure=park`; las relaciones sin geometría utilizable se omiten. No contiene edificios ni teselas.

La base es © OpenStreetMap contributors, disponible bajo ODbL 1.0. El contexto es visual y aproximado para escala/ambiente; no debe usarse para validar trazados de TransMilenio, sentidos legales, accesos, vigencia operativa, límites catastrales ni nombres completos. Los nombres vacíos reflejan etiquetas ausentes en la respuesta de OSM.
