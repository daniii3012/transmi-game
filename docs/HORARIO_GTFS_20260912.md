# Horario publicado: del intervalo fijo a las salidas del GTFS

12 de septiembre de 2026. Sustituye dos invenciones por lo que TRANSMILENIO publica en su GTFS: la
regla de despacho de cuatro y ocho minutos, por las salidas reales; y el crucero único de 60 km/h,
por la velocidad que se despeja del tiempo que el horario da a cada tramo. Las dos mitades se pueden
apagar por separado desde la interfaz.

Para entender el simulador completo y de qué datos abiertos sale cada pieza, ver
[Cómo se simula](COMO_SE_SIMULA.md).

## Qué cambió

Antes, los 137 servicios del catálogo despachaban con la misma regla: 240 s en hora pico entre
semana, 480 s el resto y todo el fin de semana, con una variación opcional de ±12 % y refuerzos
ocasionales. Ahora 104 de los 117 servicios utilizables despachan a las horas publicadas, que no
son regulares: en un sábado cualquiera un servicio pasa de 3,75 a 8 minutos según el momento.

El interruptor «Salidas del horario publicado», activo por omisión, devuelve la regla a todos los
servicios; «Duración del recorrido publicada» hace lo propio con las velocidades. Se conservan para
poder construir escenarios a mano y para comparar contra lo anterior.

## De dónde sale

[`https://gtfs.transmilenio.gov.co/`](https://gtfs.transmilenio.gov.co/) publica datos abiertos sin
credencial, con un `manifest.json` que declara sus archivos y frecuencias. El paquete estático se
regenera a diario hacia las 04:19 de Bogotá.

No confundirlo con `gis.transmilenio.gov.co/gtfs/`, el alimentador anterior que todavía citan
artículos y catálogos: devuelve 500 y está abandonado. Ver
[Endpoints de legado](ENDPOINTS_LEGADO_20260912.md).

`tools/fetch_gtfs.py` descarga el paquete, guarda su SHA-256 y recorre los 580 MB de `stop_times.txt`
en una sola pasada, dejando una fila por viaje troncal o dual y otra por cada tramo entre dos paradas
consecutivas. `tools/build_schedule.py` empareja catálogos y escribe `app/dist/schedule.json`
(310 kB) y `data/processed/schedule_audit.json`. Con `--archive` se rehace la reducción sobre un
paquete ya descargado, recalculando su SHA-256 de esos mismos bytes en vez de copiarlo.

El paquete pesa 121 MB y se vuelve a publicar cada día: **no se versiona**. Lo que acredita de qué
bytes salió todo lo demás es su SHA-256 en el manifiesto. El del paquete leído aquí es
`43c0c82de709e8bd1e3c6a170084ee696e5283553bb38b1235fe59551586a14d`, 121.251.822 bytes, con 45.614
viajes troncales y duales.

## Las tres decisiones del emparejamiento

**Exacto, nunca aproximado.** La correspondencia se hace sobre código y destino, normalizados NFC
porque los dos catálogos escriben los acentos descompuestos —lo mismo que ya documenta `live.mjs`—.
Sin normalizar, 13 servicios parecían no existir. No hay emparejamiento difuso: un servicio que no
casa queda pendiente y conserva la regla sintética, rotulado, en vez de adivinarse.

**Varios registros publicados pueden ser un servicio.** 19 servicios locales apuntan a más de un
`route_id`; son cortes por calendario o por patrón del mismo servicio —uno para días laborables,
otro para el sábado— y sus salidas se suman. Se comprobó que no se solapan en el mismo día.

**Las vueltas completas se apartan.** 20 registros del paquete llevan `||` en el nombre o unen dos
códigos en uno (`M82 CLL134 KR 7 || L82 Portal 20 de Julio`, `MK86`, `P85-M85`). Un viaje de esos es
**un** bus que cubre dos servicios locales; atarlo a ambos inventaría un segundo. Nunca se emparejan
y se listan aparte en la auditoría.

## Los 13 pendientes

| Servicio | Motivo |
|---|---|
| K16 P ElDorado | el paquete escribe el destino `PElDorado`, sin espacio |
| C84, L82, M84, M85, P85 | el código no aparece solo: únicamente dentro de una vuelta completa |
| K86 (×3), M82, M86, D81 (×2), L81 | existe el código, pero su destino publicado no equivale al local |

Doce son duales. Mientras no se resuelvan, esos servicios siguen con la regla de minutos y la
interfaz lo dice. Resolverlos exige decidir cómo se reparte una vuelta completa entre dos códigos,
que es un problema de modelo, no de emparejamiento.

El paquete además trae viajes y trazado para **A61, J76 y L81**, que el catálogo local conserva como
pendientes por falta de geometría publicada. No se activaron aquí: activarlos es revisar el trazado
contra el catálogo, no solo comprobar que existe una fila.

## El calendario no se traduce

`schedule.json` lleva el calendario GTFS tal como se publica: banderas por día de la semana,
vigencia y las fechas añadidas o retiradas una a una. Los festivos colombianos vienen ahí como
excepciones —el 17 de agosto de 2026 se retira del servicio laborable y se añade al dominical—, así
que resolver sobre la fecha real conserva exactamente lo que el operador trata aparte. Traducirlo a
los tres tipos de día del proyecto lo perdería.

## Segunda mitad: la duración del recorrido

Despachar a la hora correcta no basta si el viaje dura dos tercios de lo que debe. Los buses en
recorrido son, aproximadamente, las salidas por hora por la duración del viaje: con la duración corta
el mapa queda medio vacío aunque no falte ninguna salida.

### Qué se descompuso antes de tocar nada

Repartiendo el tiempo de los 91 servicios comparables del sábado, con crucero fijo de 60 km/h:

| | minutos | fracción |
|---|---:|---:|
| Movimiento | 29,9 | 78 % |
| Atención en estación | 4,8 | 13 % |
| Semáforos | 3,6 | 9 % |
| Cola en andén | 0,0 | 0 % |
| **Total simulado** | **38,5** | |
| **Programado** | **56,8** | |

El desajuste no estaba en la atención ni en los semáforos: estaba en que el movimiento era demasiado
rápido. La velocidad de solo movimiento salía a 40,0 km/h de mediana.

### Qué se hizo

El paquete publica el tiempo de cada tramo entre dos paradas consecutivas. Ese tiempo **lleva dentro
la atención y los rojos**, porque el feed da llegada y salida iguales en todas las paradas. Así que
para cada tramo se descuenta primero lo que el motor ya modela aparte —la atención aplicada y el
coste esperado de los semáforos de ese tramo, deducido del mismo ciclo de 90 s que usa el
simulador— y el resto es el presupuesto de movimiento. Sobre él se despeja la velocidad de crucero:

```
t(v) = distancia/v + (v/2)(1/a + 1/b)(1 + n·p)
```

El primer término es el crucero; el segundo, lo que cuestan arranque y frenada, una vez en las
paradas y otra en cada semáforo en que toque parar. Igualar `t(v)` al presupuesto deja una ecuación
de segundo grado y se toma la raíz menor, que es la de ir más despacio y no la de correr
desperdiciando el tiempo en acelerar.

Tres límites explícitos: el crucero del escenario sigue siendo el techo, así que **esto nunca acelera
un bus**; hay un suelo de 3 m/s; y si el presupuesto no alcanza ni yendo al máximo, se va al máximo y
el tramo sale más corto que el horario, que es preferible a inventar una velocidad imposible. En el
sábado completo eso pasa en el 10 % de los tramos.

Descontar los semáforos **sube** la velocidad de crucero, no la baja: el tiempo que se van en rojos
hay que recuperarlo rodando para llegar a la misma hora. Es justamente lo que evita contarlos dos
veces, y hay una prueba que lo fija.

Los tiempos se separan en cuatro cubos —punta, resto del laborable, sábado y festivo—, porque un
tramo no dura lo mismo un martes a las siete que un domingo: la razón mediana entre punta y valle es
1,14. Agrupar sábado y domingo en un solo cubo «valle» dejaba 18 de 53 servicios dominicales por
encima de su banda; separarlos los bajó a 7.

### Resultado

| | Movimiento | Atención | Semáforos | Total | Programado |
|---|---:|---:|---:|---:|---:|
| Crucero fijo 60 km/h | 29,9 | 4,8 | 3,6 | 38,5 | 56,8 |
| Tiempos publicados | 46,8 | 4,8 | 4,2 | 55,8 | 56,8 |

Velocidad comercial simulada 21,3 km/h frente a 21,1 programada.

Servicios cuya duración mediana cae dentro de su propia banda p10–p90, que es el criterio de
aceptación:

| Día | Antes | Después |
|---|---:|---:|
| Viernes | — | **99 / 104** |
| Sábado | 1 / 91 | **77 / 91** |
| Domingo | — | **39 / 53** |

Los 14 que siguen fuera el sábado están casi todos a menos de dos minutos de su banda. El residuo
tiene causa conocida: la ecuación que despeja la velocidad no conoce los límites por curvatura que
el perfil sí aplica, de modo que el recorrido real sale algo más lento que el objetivo; y el tiempo
publicado de un tramo lleva una atención, mientras que el viaje completo tiene una más que tramos.
No se ajustó nada para cerrar esa diferencia: hacerlo sería calibrar contra un contador.

C17 se queda corto por otro motivo, declarado: es el único servicio sin tiempos por tramo, porque los
dos catálogos no cuentan las mismas paradas —22 contra 21— y alinear por índice dos secuencias de
distinto largo emparejaría trechos de vía que no son el mismo.

### Coste

| | Referencia previa | Ahora |
|---|---:|---:|
| Preparación | 12,01 s | 11,00 s |
| Muestreo | 1,30 ms | 1,17 ms |
| Memoria | 560 MB | 650 MB |
| Flota máxima muestreada | 1.113 | 1.667 |

La flota sube porque los viajes ahora duran lo que deben. El presupuesto de cada tramo se redondea a
diez segundos antes de despejar la velocidad: sin redondear, cada viaje pedía su propio perfil por
diferencias de décimas en el embarque, la caché se cuadruplicaba y la preparación subía a 13,8 s.

El banco de estrés apaga el horario a propósito: con él, sus intervalos de 2 y 3 minutos solo
afectarían a los servicios sin horario publicado y dejaría de cargar el motor. Su techo pasó de 3.303
a 3.231 buses, y eso **no** es una regresión del motor —el camino sintético da exactamente lo mismo
que antes— sino el efecto de cargar en el banco los vagones publicados, que la aplicación ya usaba.

## Lo que esto arregla y lo que no

Reconstruyendo el sábado 12 de septiembre a las 12:30, red completa:

| | Activos 12:30 | Salidas del día |
|---|---:|---:|
| Regla de 4/8 min y crucero fijo | 477 | 12.503 |
| Solo salidas publicadas | 634 | 16.038 |
| Salidas y duraciones publicadas | **873** | 16.038 |
| Viajes GTFS en curso, troncal y dual | 975 | 15.845 |
| …de ellos, en servicios que el simulador despacha | 850 | |

La comparación justa es la última fila: **873 simulados frente a 850 publicados, +2,7 %**. Los 125
restantes pertenecen a los servicios pendientes, que siguen con la regla sintética.

Con solo las salidas corregidas quedaban 341 buses de diferencia, y el motivo estaba medido: **los 91
servicios comparables terminaban su recorrido antes de lo programado, sin excepción.** La razón
mediana entre duración simulada y programada era 0,67; el p10 0,62 y el p90 0,77.

```
ruta  destino                 simulado  programado  razón
 Z63  Tibanica                    23.5        41.0   0.57
 L18  PORTAL 20 DE JULIO          46.9        77.2   0.61
 A60  Calle 72                    40.0        65.0   0.62
   1  Universidades               19.8        23.2   0.86
```

Como los buses en recorrido son aproximadamente las salidas por hora por la duración del viaje,
corregir la duración por ese factor predecía unos 945; la corrección efectiva dio 873. **El crucero de
60/50 km/h no se tocó**: sigue siendo el techo, y ningún semáforo se recalibró.

La regla que se respetó en todo momento: no bajar la velocidad hasta que cuadre un contador. Se parte
del tiempo objetivo de cada tramo y se reparte entre movimiento, atención y señales con supuestos
explícitos, sin volver a sumar sobre el tiempo programado los rojos y descensos que ya lleva dentro.

## Advertencias sobre el dato

- Es **programación, no operación**. El GTFS dice a qué hora debía salir un bus, no si salió.
- Las 729.292 filas de paradas troncales y duales tienen `timepoint=0`: tiempos aproximados.
- Llegada y salida son iguales en todas las paradas: el feed **no separa el tiempo de atención**.
  Una espera en estación con base empírica solo puede salir de observar, no de este archivo.
- `trips.txt` no trae `direction_id` ni `block_id`: ni el sentido normalizado ni la vinculación de
  viajes a un bus físico o a un patio. La reutilización de vehículos sigue siendo la del modelo.
- `routes.txt` trae 1.104 filas con 1.101 identificadores: hay tres repetidos, todos fuera del
  recorte troncal/dual. Un importador general no debe sobrescribirlos sin diagnóstico.
- Los colores del paquete son genéricos por componente —rojo toda troncal, verde todo dual—. **Se
  conservan los del mapa**, que distinguen corredor.
- `shape_dist_traveled` está en metros en este paquete, comprobado contra la longitud del trazado de
  C15. No suponerlo para otros componentes ni para otros feeds.
- El código C15 también existe en zonal: siempre se filtra primero por componente.

## Actualizarlo

```
python3 tools/fetch_gtfs.py      # ~3 min: descarga 121 MB y recorre stop_times.txt
python3 tools/build_schedule.py  # segundos
```

El primero deja una carpeta fechada en `data/raw/gtfs/` con su manifiesto y actualiza `latest.json`;
el segundo lee siempre la última. Conviene revisar en la auditoría si cambió el número de pendientes
antes de dar por buena una actualización.

## Verificación

74 pruebas Node y 10 Python del proxy en vivo pasan. Seis son nuevas y cubren: que el calendario
GTFS se resuelva sobre la fecha real incluida una excepción de festivo; que un servicio despache
exactamente a las horas publicadas y que esos intervalos no sean constantes; que apagar el
interruptor y no tener archivo produzcan la misma operación de reserva; y que ninguna ruta apunte a
un registro de vuelta completa; que la velocidad despejada reproduzca exactamente el tiempo objetivo
del tramo y nunca supere el crucero; y que con tiempos publicados el recorrido dure lo programado
mientras que a crucero fijo se queda corto. `tests/test_network_2d.py` no corre en este equipo por
falta de `shapely`, igual que antes de este cambio.

Cómo funciona el simulador en conjunto, y de qué datos abiertos sale cada pieza, está en
[Cómo se simula](COMO_SE_SIMULA.md).
