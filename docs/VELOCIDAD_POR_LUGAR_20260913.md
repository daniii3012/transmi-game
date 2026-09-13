# La velocidad la pone el lugar; el horario sigue poniendo el total

13 de septiembre de 2026. El simulador rodaba a 60 km/h en calzada segregada y gastaba el tiempo
sobrante del horario quedándose quieto en la aproximación a la estación siguiente. Se veía como
buses detenidos sin causa mientras otros les pasaban al lado. Esto lo sustituye por lo que el
alimentador oficial dice que ocurre en cada trecho de corredor.

## Lo que estaba mal, medido

Jueves simulado, a las 6:40: 1.669 buses, **558 detenidos en tráfico (33 %)** y la mitad de la flota
quieta contando atención y semáforos. En la captura del sábado, la flota troncal real aparece
detenida el **28 %** del tiempo, y esa cifra está inflada porque un vehículo que no refresca su
posición parece parado.

Sobre el día: de las 19.863 h entre paradas, 7.673 h eran el bus quieto —el 39 %—, con mediana de 77 s
por tramo y un máximo de **1.883 s**. Los peores eran los expresos: un S46 se plantaba 28 minutos en
los últimos 440 m antes de Bosa.

La causa no era el presupuesto de tiempo. La velocidad comercial que impone el horario publicado
—21,4 km/h de mediana entre paradas— coincide con la real medida por bus, **20,5 km/h de mediana y
21,1 de media** sobre 1.033 vehículos con más de una hora de seguimiento. Lo que estaba mal era el
reparto: el motor rodaba al percentil 95 de la velocidad real y pagaba la diferencia parándose.

## Lo que dice la captura sobre la densidad

Antes de construir nada se probó la hipótesis de que un bus va más lento cuando tiene más buses
cerca. En bruto, sobre corredor abierto, se cumple de forma espectacular:

| Buses a ~330 m | ninguno | 1 | 2 | 3 | 4 | 6 o más |
|---|---|---|---|---|---|---|
| Velocidad | 31,0 | 28,5 | 25,7 | 23,0 | 20,6 | **16,2 km/h** |

Pero comparando **cada trecho de 110 m consigo mismo**, el efecto casi desaparece: 0,98 con un
vecino, 0,95 con cuatro, 0,92 con seis o más. Controlando además por hora, se va del todo. La
correlación fuerte es de composición: los sitios con muchos buses son los sitios lentos, no al revés.

Lo que sí manda es el lugar. La velocidad media de un trecho va de **10,2 km/h en el percentil 10 a
44,3 en el percentil 90**, y el mismo trecho a distintas horas de la tarde del sábado solo varía
entre 0,97 y 1,06 de su propia media.

Por eso no se implementó un término de densidad en vivo: el campo por lugar ya lo contiene, y el
apiñamiento por sí solo vale un 5–8 % que no justifica meter el plan de despachos dentro del motor.

## El campo

`tools/build_speed_field.py` recorre las capturas y escribe `data/curated/speed_field.json`: por
corredor, sentido y cubeta de 100 m, a qué velocidad se rueda ahí y qué parte del tiempo se está
quieto ahí.

| | |
|---|---|
| Eje troncal cubierto | 113,8 km · 2.318 cubetas |
| Cubetas con medición propia | **2.194 (95 %)** · 82 suavizadas con sus vecinas · 42 por mediana del corredor |
| Pares de lecturas usados | 435.090 · 54.611 descartados por caer fuera del eje |
| Velocidad rodando | p10 16,6 · mediana 31,5 · p90 47,9 km/h |
| Parte del tiempo detenido | p10 0 % · mediana 8 % · p90 36 % |

Reparto de las 2.638 h medidas: **1.988,7 h rodando**, 417,0 h detenido por el corredor, 62,3 h en
cola por su propio andén y 170,0 h de atención.

**La distinción que hace que esto funcione.** Un bus quieto en una estación puede estar atendiendo
pasajeros o estar atascado. El alimentador trae la parada a la que cada vehículo se dirige, así que
el tiempo quieto a menos de 60 m de su destino se cuenta como atención, y hasta 250 m como cola por
su propio andén. `stop_share` se queda solo con lo que detiene a cualquiera que pase por ahí. Sin
esa separación un expreso de 15,5 km heredaba 19 minutos de espera que eran la atención de los
locales; con ella, el B26 baja de 1.324 s a 701 s en ese tramo.

Los corredores salen reconocibles: Autopista Norte 40,6 km/h y 8 % detenido, NQS Central 41,2 y 10 %,
Américas 30,4 y 13 %, **Caracas 20,9 km/h y 24 % detenido**.

## Cómo lo usa el motor

`build_services.py` resuelve el campo a lo largo de cada ruta y escribe `app/dist/speed_profiles.json`
—117 servicios, cobertura mediana del 98 %—. Por cada tramo entre paradas, el motor:

1. Rueda a la velocidad medida de cada trecho. El techo deja de ser plano: `travelProfile` acepta un
   límite por posición y las pasadas de aceleración y frenada que ya existían hacen progresivo el
   paso de un trecho al siguiente.
2. Calcula lo que el campo dice que ese tramo pasa detenido.
3. **Un único factor por tramo** estira o encoge esa forma hasta que el tramo dura exactamente lo que
   el horario publicado le da. El factor va entre 0,60 y 1,60 y se cuantiza en pasos de 0,05; la
   variación de ±5 km/h por bus se pliega dentro de él, de modo que el perfil de un tramo depende de
   un solo número y la caché no guarda cinco copias casi iguales.
4. Reparte la espera donde el campo dice que se para, en trozos de 120 s como mucho —una cola avanza
   a trozos—, y con 6 posiciones por tramo como máximo.
5. **Las esperas se resuelven junto con los semáforos, no después.** Pararse antes de un rojo cambia
   la hora a la que se llega a él y por tanto su fase; calcularlos por separado daba un rojo que no
   correspondía. El ajuste final de décimas se hace en la última espera, que no tiene nada detrás.

La hora de llegada a cada parada no se mueve: sigue siendo la publicada.

## Resultado

| | Antes | Ahora | Referencia real |
|---|---|---|---|
| Detenidos en tráfico, jueves 6:40 | 558 (33 %) | **213 (12 %)** | — |
| Flota quieta en total | 51 % | **30 %** | ≤ 28 % |
| Parte del tiempo entre paradas detenido | 39 % | **14 %** | — |
| Horas rodando / detenido | 10.891 / 7.673 | **16.143 / 2.829** | — |
| Espera por tramo: mediana · p90 · máximo | 77 · 257 · 1.883 s | **30 · 111 · 933 s** | — |
| Espera individual: mediana · p99 · máximo | bloques de 45 s | **11 · 92 · 263 s** | — |
| Velocidad comercial del simulador | 21,4 km/h | 21,4 km/h | 20,5–21,1 km/h |

Los peores tramos expresos bajan mucho pero no desaparecen: S46 Calle 100 → Bosa pasa de 1.673 s a
436 s de espera por paso, y B26 de 1.324 a 701. Lo que queda es lo que el campo mide como detención
del corredor en 12 y 20 km de recorrido, ya repartida en varias esperas y no en un plantón único.

Banco de referencia: preparación 13,6 s (antes 11,0), muestreo **0,80 ms** por lectura (antes 1,32),
caché de perfiles 73.229 entradas (antes 76.507), heap 787 MB (antes 560). El techo del escenario de
estrés sube de 3.303 a 4.517 buses simultáneos: sin horario publicado el campo también manda, los
viajes duran lo que el corredor permite y coinciden más buses en la calle. Ir y volver en el reloj
sigue devolviendo exactamente el mismo estado.

## Lo que asume, a sabiendas

1. **Un día, sábado, de 14:00 a 23:30**, aplicado a todas las horas y tipos de día. La punta de un
   laborable —justo donde se vio el problema— no está medida. Es la suposición grande.
2. El reparto entre rodar y estar quieto arrastra el sesgo del GPS que no refresca; la velocidad de
   travesía, que es distancia sobre tiempo, no.
3. Las 124 cubetas sin medición propia heredan la mediana de su corredor y lo declaran en `source`.
4. Duales y calle conservan el modelo continuo anterior: el campo solo cubre corredor troncal.
5. Los semáforos se modelan aparte y el campo también los lleva dentro, así que en los trechos con
   semáforo hay algo de doble conteo. El factor lo absorbe en el total; en el reparto se traduce en
   algo más de peso cerca de los cruces, que es donde de todos modos se para.
6. La atención medida en el campo son 170 h, menos de lo esperable: cuando un bus abre puertas el
   alimentador ya puede apuntar a la parada siguiente, así que parte de la atención se cuela en
   `stop_share`.
7. Sin término de densidad.

La semana que viene, con la captura completa, el trabajo es **volver a correr solo la fase del
campo**: el motor no cambia, cambia el archivo. Ahí se añaden hora y tipo de día, se mide si la punta
laborable justifica el término de densidad, y se revisa si el factor toca sus topes a menudo —si los
toca, la conclusión es sobre el horario publicado y no sobre el motor.

## Cómo se reproduce

```
.../venv/bin/python tools/build_speed_field.py     # data/curated/speed_field.json
.../venv/bin/python tools/build_services.py        # app/dist/speed_profiles.json
node --test app/tests/*.test.mjs && .../venv/bin/python -m unittest discover -s tests
node app/tests/operation-benchmark.mjs
```

`build_speed_field.py --dry-run` resume sin escribir. Antecedente y por qué se retira la regla
anterior, en [velocidad y detenciones](VELOCIDAD_Y_DETENCIONES_20260912.md); límites del alimentador,
en [captura del alimentador](CAPTURA_RT_20260912.md).
