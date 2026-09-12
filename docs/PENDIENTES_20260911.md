# Revisión de los 23 registros pendientes — 11 sep. 2026

Se consultó de nuevo el detalle oficial de cada registro pendiente y se contrastó con
la instantánea curada del 10 sep. La consulta es de solo lectura y no modifica el
catálogo: la evidencia queda en `data/research/pending_probe_20260912T003935Z`, con URL, SHA-256 y bytes de
cada respuesta. Reproducible con `python3 tools/probe_pending_routes.py`.

El endpoint `rutas/{id}/rutaDetalle` publica únicamente color, nombre, estaciones,
trazado y horario. No publica vigencia ni un indicador de ruta activa: esas fechas
provienen del catálogo de troncales, no de este detalle.

**Resultado: 2 registros pasan a ser verificables, 1 merece reimportarse y 20 siguen
sin evidencia suficiente.** Nada se activó; activar cualquiera exige una instantánea
nueva y una decisión explícita de curación.

## Sin trazado ni paradas publicadas — siguen pendientes

El detalle responde `trazado: null` y `estaciones: []`. Los doce vencieron además
entre el 14 y el 28 de agosto de 2026, antes de la instantánea. No hay nada que
verificar y no se inventa geometría.

| código | id | nombre publicado | coords. del trazado | paradas | horario publicado | vigencia hasta |
|---|---|---|---:|---:|---|---|
| 6 | 692 | Calle 76 | — | 0 | D-F 4:30 AM–10:00 PM · L-S 4:30 AM–11:00 PM | 2026-08-21 |
| A60 | 1187 | Calle 76 | — | 0 | D-F 4:00 AM–10:00 PM · L-S 4:30 AM–9:30 PM | 2026-08-21 |
| A61 | 1188 | Polo | — | 0 | S 4:30 AM–12:00 PM · L-V 4:30 AM–10:00 AM | 2026-08-14 |
| B46 | 386 | Portal Norte | — | 0 | L-S 4:00 AM–9:00 AM · L-S 3:00 PM–8:00 PM | 2026-08-28 |
| F61 | 1190 | Portal Américas | — | 0 | L-V 3:00 PM–8:00 PM | 2026-08-14 |
| G41 | 776 | San Mateo | — | 0 | L-V 5:00 AM–9:00 PM · S 5:00 AM–9:00 PM | 2026-08-28 |
| G42 | 1175 | San Mateo | — | 0 | D-F 5:00 AM–10:00 PM · S 5:00 AM–11:00 PM · L-V 4:30 AM–11:00 PM | 2026-08-28 |
| G43 | 389 | San Mateo | — | 0 | D-F 4:30 AM–10:00 PM · L-S 5:00 AM–11:00 PM | 2026-08-28 |
| G45 | 393 | San Mateo | — | 0 | L-S 5:00 PM–8:00 PM · L-S 5:00 AM–8:00 AM | 2026-08-28 |
| G46 | 387 | San Mateo | — | 0 | L-S 5:00 AM–9:00 AM · L-S 3:00 PM–8:00 PM | 2026-08-28 |
| G48 | 12611 | San Mateo | — | 0 | L-V 4:00 PM–9:00 PM | 2026-08-28 |
| K43 | 388 | Portal Eldorado | — | 0 | D-F 4:00 AM–10:00 PM · L-S 4:00 AM–11:00 PM | 2026-08-28 |

## Con paradas pero sin trazado — siguen pendientes

El orden de paradas está publicado, pero sin trazado no se puede situar el recorrido
sin inventar la geometría intermedia. Se mantienen pendientes.

| código | id | nombre publicado | coords. del trazado | paradas | horario publicado | vigencia hasta |
|---|---|---|---:|---:|---|---|
| J76 | 1214 | Universidades | — | 10 | L-V 5:00 AM–8:30 AM | 2026-09-14 |
| K86 | 1189 | Portal ElDorado Ciclovía | — | 27 | D-F 7:00 AM–2:00 PM | 2026-09-13 |
| L82 | 1242 | Portal 20 de Julio Ciclovía | — | 16 | S 4:00 AM–11:00 PM · D-F 2:00 PM–10:00 PM · L-V 4:00 AM–11:00 PM | 2026-09-13 |
| M82 | 12991 | CLL134 - KR 7 Ciclovía | — | 17 | L-S 4:00 AM–11:00 PM · D-F 4:30 AM–10:00 PM | 2026-09-13 |
| M86 | 5490 | KR 7 - CLL 107A Ciclovía | — | 22 | L-S 4:00 AM–10:00 PM · D-F 5:00 AM–9:00 PM | 2026-09-13 |

## Trazado publicado que antes faltaba — verificables

Estos dos registros sí tienen ahora trazado y secuencia de paradas en la fuente
oficial, donde la instantánea del 10 sep. no traía ninguno. Son los únicos candidatos
reales a dejar de estar pendientes.

| código | id | nombre publicado | coords. del trazado | paradas | horario publicado | vigencia hasta |
|---|---|---|---:|---:|---|---|
| E48 | 12444 | CAD | 297 | 11 | S 4:30 AM–10:00 AM · L-V 4:00 AM–10:00 AM | 2026-09-19 |
| H76 | 1213 | Portal Usme | 710 | 10 | L-V 4:00 PM–10:30 PM | 2026-09-14 |

E48 es un servicio de madrugada hacia el CAD y H76 uno de tarde hacia Portal Usme;
ambos horarios son coherentes con servicios de refuerzo en un solo sentido.

## K86 completo — conviene reimportar antes de decidir

| código | id | nombre publicado | coords. del trazado | paradas | horario publicado | vigencia hasta |
|---|---|---|---:|---:|---|---|
| K86 | 629 | Portal ElDorado | 1294 | 26 | D-F 5:30 AM–10:00 PM · L-S 5:30 AM–11:00 PM | 2026-09-14 |

La instantánea local guarda 108 puntos y unos 3,19 km, y por eso sus referencias de
parada quedaban hasta a unos 44,7 km del trazado. La fuente devuelve hoy 1.294
coordenadas. La incompatibilidad parece un recorte de la captura y no un dato
contradictorio, pero eso solo se confirma reimportando el registro y volviendo a
correr las comprobaciones de distancia y orden. **Sigue pendiente hasta entonces.**
No se confunde con el ramal de aeropuerto (5316).

## Variantes con “Ciclovía” en el nombre — siguen pendientes

La Ciclovía de Bogotá opera domingos y festivos de 7:00 a 14:00, y durante esa
franja los servicios duales y zonales que cruzan su trazado operan con desvíos
([Bogotá.gov.co](https://bogota.gov.co/mi-ciudad/cultura-recreacion-y-deporte/horarios-y-rutas-de-la-ciclovia-bogotana-los-domingos-y-festivos),
[TransMilenio](https://www.transmilenio.gov.co/comunicaciones/noticias-de-transmilenio/boletines-informativos/desvios-servicios-zonales-duales-jornada-ciclovia-nocturna)).

Solo **K86/1189** declara exactamente ese patrón: `D-F 7:00–14:00`. Encaja con una
variante de desvío por Ciclovía, pero no tiene trazado publicado, así que sigue
pendiente por la razón de siempre.

Los demás llevan “Ciclovía” en el nombre y sin embargo declaran calendario de semana
completa, que no corresponde a un desvío dominical:

| código | id | nombre publicado | coords. del trazado | paradas | horario publicado | vigencia hasta |
|---|---|---|---:|---:|---|---|
| L81 | 5280 | Portal 20 de Julio Ciclovía | 698 | 24 | S 5:00 AM–10:30 PM · D-F 6:00 AM–10:00 PM · L-V 5:00 AM–11:00 PM | 2026-09-13 |
| M85 | 4596 | Museo Nacional Ciclovía | 769 | 10 | L-D 5:00 AM–9:00 PM | 2026-09-13 |
| P85 | 4595 | AV 68 Calle 9 Ciclovía | 769 | 8 | D-F 2:00 PM–9:00 PM · L-S 5:00 AM–9:00 PM | 2026-09-13 |

El importador los marca pendientes porque no puede decidir entre dos lecturas
igualmente posibles: que “Ciclovía” forme parte del destino publicado y el servicio
sea de semana completa, o que el calendario traiga el de la ruta base en lugar del de
la variante. Ninguna fuente consultada resuelve cuál es. **Se mantienen pendientes**;
activarlos suprimiría o duplicaría salidas de su familia regular según cuál lectura
resulte cierta. L82, M82 y M86 además no tienen trazado.

## Qué haría falta para cerrarlos

1. Una instantánea nueva con `tools/fetch_services.py` que incluya E48, H76 y K86/629,
   seguida de `build_services.py` y de las pruebas de distancia y orden de paradas.
2. Una fuente oficial que aclare si las variantes con “Ciclovía” en el nombre son
   desvíos dominicales o servicios de semana completa.
3. Para los veinte restantes, que la fuente publique el trazado. Doce de ellos están
   vencidos desde agosto y probablemente no vuelvan a publicarse.

La cifra **23** se conserva mientras no se tome esa decisión de curación.
