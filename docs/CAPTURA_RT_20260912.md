# Captura del alimentador en vivo y qué se mide con ella

12 de septiembre de 2026. La tercera pieza, después de las salidas y las duraciones publicadas.
Las dos anteriores calibran el simulador contra **la programación**; esta empieza a acumular lo que
hace falta para calibrarlo contra **la operación**, que no es lo mismo y hoy no existe en ninguna
parte.

## Por qué hace falta observar

Tres cosas que el paquete publicado no puede responder, por cómo está hecho:

- **La atención en estación.** El feed da llegada y salida iguales en las 729.292 filas de paradas
  troncales y duales. El tiempo de atención existe, pero va dentro del tramo y no se puede separar.
- **Lo que de verdad tarda un trecho**, frente a lo que tenía asignado.
- **Cómo se agrupan los buses.** El horario publica cada cuánto *sale* uno; si se juntan por el
  camino, eso solo se ve mirando.

Y no hay archivo del que sacarlo: el bucket del alimentador guarda solo los archivos vigentes, que
se sobrescriben cada quince segundos. Los 310 paquetes estáticos históricos son horarios, no
posiciones. Cada día sin grabar se pierde para siempre.

Las direcciones que se probaron y quedaron descartadas —incluidas las del alimentador anterior, que
todavía se citan en artículos y catálogos— están en
[Endpoints de legado](ENDPOINTS_LEGADO_20260912.md), con su estado y el motivo. Ahí también se
explica por qué `alerts.pb` y `tripupdates.pb`, que sí responden, no se usan.

## Cómo se captura

```
python3 tools/capture_rt.py --once      # una lectura de prueba
python3 tools/capture_rt.py --days 8    # una semana
```

Lee `positions.pb`, que es dato abierto sin credencial y trae los 5.500 vehículos del sistema en una
petición de unos 700 kB. Por omisión toma una lectura cada 30 s entre las 04:00 y las 23:30, y el
detalle guarda solo troncal y dual. Ctrl+C la para sin perder nada; volver a arrancarla continúa los
mismos archivos.

En `data/raw/rt_capture/` deja:

| Archivo | Qué es |
|---|---|
| `rt.jsonl` | Una línea por reconstrucción del feed: conteo por agencia y por línea troncal |
| `rt_detalle_AAAAMMDD.csv.gz` | Una fila por vehículo y lote: `build, bus, etiqueta, placa, viaje, ruta, lat, lon, parada, secuencia` |
| `rt_detalle_AAAAMMDD.json` | A qué paquete publicado pertenece ese día de lecturas |
| `routes.txt` | El catálogo, bajado una vez al día por Range del paquete: 13 kB en vez de 121 MB |

Unos **50 MB al día**, 350 por semana. `--every 60` lo deja en la mitad y `--no-detail` solo guarda
el resumen. Con `--scope todo` se captura el sistema entero, pero son 2 GB por semana. **Nada de esto
se versiona**: lo que entra al repositorio es el informe que sale de ello.

El archivo de procedencia existe por una razón concreta: un día de capturas solo se puede comparar
contra el horario bajo el que circuló, y el paquete se vuelve a publicar cada madrugada. Sin esa nota
al lado, dentro de un mes nadie sabría contra qué cotejar.

## Las dos trampas del feed, y cómo se sortean

**La cabecera está congelada.** `FeedHeader.timestamp` lleva días clavado en el mismo valor. El
sello que sí avanza es el de los vehículos, y es el que se usa como reloj. Además la captura
descarta el lote repetido cuando el feed aún no se ha reconstruido, para que la cuenta de lecturas
no salga inflada.

**Las posiciones se repiten y luego saltan.** Ese sello es único para los 5.500 vehículos: es la hora
de construcción del lote, no la del GPS de cada bus. Cada vehículo refresca a su ritmo y el feed
repite mientras tanto su última posición conocida, así que entre dos lotes un bus puede aparecer
quieto y después dar un salto que es ponerse al día, no velocidad. En una toma real:

```
build       secuencia parada    desplazamiento
1789236526      4      61656    +119 m en 20 s =  21,5 km/h
1789236545      4      61656    +953 m en 19 s = 180,6 km/h   ← imposible
```

Por eso **el análisis no deriva velocidades de dos lotes consecutivos**. Lo que sí es sólido es la
parada a la que el bus se dirige: `secuencia` y `parada` cambian cuando deja la anterior, y ese
cambio no depende de si el GPS refrescó. Todas las medidas se construyen sobre esos cambios.

Esto también matiza una medición anterior: los percentiles de velocidad instantánea que trae
`rt.jsonl` arrastran ese ruido y no deben leerse como velocímetro.

## Qué mide el análisis

```
python3 tools/analyse_capture.py
```

Escribe `data/processed/rt_capture_analysis.json` con cuatro bloques:

- **cobertura** — cuántos lotes, en qué intervalo, con qué paso y dónde están los huecos. Una media
  sobre una serie rota miente, así que los huecos se informan en vez de alisarse.
- **flota** — vehículos por hora y componente. Es la curva que la regla de 4 y 8 minutos suplía.
- **tramos** — el tiempo observado de parada a parada contra el publicado, emparejado por ruta y por
  los dos identificadores de parada, no por posición en la lista: un patrón corto cambia la
  numeración y compararía trechos distintos.
- **intervalos** — separación entre buses consecutivos de una ruta al dejar la misma parada.

Lo observado va de **dejar** una parada a **dejar** la siguiente; lo publicado, de una parada a la
otra. Difieren en a qué extremo se atribuye la atención, no en cuánto incluyen: ambos son un trecho
más una atención.

## Primera lectura, y por qué no se actúa sobre ella

Con **1,32 h de un sábado por la tarde** —157 lotes, paso mediano 19 s, sin huecos ni fallos—,
17.266 observaciones emparejadas sobre 1.295 tramos distintos:

| Duración publicada del tramo | tramos | p10 | mediana | p90 |
|---|---:|---:|---:|---:|
| < 90 s | 150 | 0,74 | 1,19 | 1,83 |
| 90–150 s | 357 | 0,60 | 0,95 | 1,47 |
| 150–240 s | 307 | 0,59 | 0,85 | 1,47 |
| > 240 s | 461 | 0,52 | 0,85 | 1,34 |

La razón se reparte por duración porque **la medición no vale igual en todas**. El instante de cada
transición se conoce con la resolución del muestreo, así que en un tramo de minuto y medio el error
es una fracción grande de lo medido; la banda de menos de 90 s, con mediana 1,19, está midiendo sobre
todo su propio error.

En los tramos largos, donde sí se puede leer, el sábado por la tarde los buses tardaron alrededor de
**el 85 % de lo programado**. Es decir: el horario lleva holgura, y la calibración de la fase 2
—que apunta al tiempo publicado— deja la simulación algo más lenta de lo que fue la realidad en esa
ventana.

Intervalos entre buses consecutivos en la misma parada: troncal mediana 5,3 min (p10 1,6, p90 10,1),
con un 6 % a menos de un minuto; dual mediana 3,8 min, con un 13 %. Ese porcentaje es agrupamiento
medido, no supuesto.

**Nada de esto se ha aplicado al simulador, y no debería aplicarse todavía.** Es hora y media de un
sábado a mediodía, sin punta, sin día laborable y sin lluvia. Para que estas cifras signifiquen algo
hacen falta de 7 a 14 días con al menos laborables y fin de semana, separando huecos de captura,
posiciones inmóviles, viajes incompletos y desvíos. Una cola se puede observar; su causa no se
identifica solo por velocidades bajas.

## Lo que falta

- **La atención en estación no se mide todavía.** Requiere las coordenadas de las paradas —por eso
  `stops.txt` ya entra en la reducción del paquete— y muestreo más fino que 30 s, porque una atención
  típica dura menos que el intervalo actual.
- **El retraso contra el horario** por viaje, que exige guardar los tiempos programados parada a
  parada de cada viaje y no solo la mediana por tramo.

La vista general en vivo sobre este mismo alimentador sí está hecha, y se describe más abajo.

## Verificación

**Del análisis**, 12 pruebas sobre lecturas construidas a mano: que repetir la misma parada no es un
evento, que el detalle se ordena antes de leerlo, que cada vehículo y viaje se siguen aparte —un bus
encadena viajes y mezclarlos inventaría un tramo del final de uno al principio del otro—, que un
tramo sin equivalente publicado se cuenta aparte en vez de desaparecer, y que la razón se reparte por
duración en vez de promediarse de golpe.

**Del adaptador de la vista general**, 10 pruebas sobre un alimentador construido byte a byte, para
ejercitar el decodificador contra lo que tiene que sobrevivir y no contra un buen día en Bogotá: que
el reloj es el sello de los vehículos y no la cabecera congelada, que una entidad sin vehículo se
salta en vez de adivinarse, que una posición ausente se lee como ausente, que fuera de Bogotá se
descarta diciéndolo, que una ruta fuera del catálogo se dibuja y se cuenta aparte, que dos lecturas
seguidas no preguntan dos veces, y que sin catálogo local responde «no disponible» en vez de caerse.

30 pruebas Python en total, y las 74 Node siguen pasando.

## La vista general en vivo sale del mismo alimentador

`tools/live_network.py` sirve `/api/en-vivo/red` leyendo `positions.pb`. Sustituye a la instantánea
que antes venía de un servicio configurado en local, y la mejora en tres cosas: **no necesita
credencial**, **no puede truncar** —una lectura trae el sistema entero— y **coincide con el
simulador por construcción**, porque decide qué es troncal y qué dual con el mismo `routes.txt`
sobre el que se construyó el horario, no consultando otra vez al portal.

El servidor responde `Access-Control-Allow-Origin: null`, así que el navegador no puede pedirlo
directo: el proxy local es quien lo lee. Lo que se publica sigue siendo estático y el panel lo dice.

Sobre las posiciones se publican dos señales para no confiar de más:

- **`build_age_s`**, la antigüedad del lote. El alimentador se reconstruye cada quince segundos, así
  que un número grande significa que el feed se quedó atrás, no que los buses se hayan detenido. El
  panel lo avisa a partir de minuto y medio, seis veces lo que tarda una reconstrucción normal.
- **`unmatched`**, los vehículos troncales o duales cuya ruta no está en el catálogo local: unos 120
  de 1.010. Se dibujan igual, rotulados «fuera del catálogo», y se cuentan aparte. Circulan de
  verdad; son en su mayoría los registros de vuelta completa que el horario aparta a propósito.

**Ningún bus se dibuja dos veces.** Las dos fuentes comparten los identificadores de vehículo —se
comprobó: de los 18 buses que «Por servicio» devuelve para C15, los 18 están en la instantánea
general con el mismo id—, así que con un servicio en foco la vista de red omite los que ya están
dibujados en primer plano.

Lo que la lectura por servicio sigue aportando, y el alimentador abierto no trae: ocupación,
accesibilidad, destino depurado y los metros recorridos sobre la ruta. Por eso se conserva, para un
servicio a la vez, y por eso la pestaña ofrece las dos vistas.

Al quedar sin uso, se retiró del repositorio la instantánea de red que consultaba el servicio
configurado en local, con las dos pruebas que la cubrían. Si alguna vez hace falta contrastar las
dos fuentes de nuevo, el camino corto es la vista «Por servicio», que sigue ahí.

Una precisión que salió de las pruebas: el alimentador codifica latitud y longitud en coma flotante
de 32 bits, así que las posiciones traen del orden de **un metro de cuantización**. Un bus queda
donde el feed puede decir que está, no más fino que eso.

## La etiqueta de flota

El `VehicleDescriptor` trae tres campos y la captura guarda los tres desde el 12 de septiembre de
2026. El segundo es la etiqueta que el bus lleva pintada —`E0067`, `K10657`— y de ella sale el tipo
de carrocería de cada servicio: ver [tipo de bus por servicio](TIPOS_DE_BUS_20260912.md). Un día que
empezó a escribirse sin esa columna no se mezcla con las nuevas: la captura aparta lo ya escrito en
`rt_detalle_AAAAMMDD_esquema9.csv.gz`, con su cabecera intacta, y sigue en un archivo nuevo. Los
lectores recorren `rt_detalle_*.csv.gz` y encuentran los dos.
