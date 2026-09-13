# La velocidad la pone el lugar; detenerse, solo el andén o el rojo

13 de septiembre de 2026. El simulador rodaba a 60 km/h en calzada segregada y gastaba el tiempo
sobrante del horario quedándose quieto en la aproximación a la estación siguiente. Se veía como
buses detenidos sin causa mientras otros les pasaban al lado. Esto lo sustituye por dos reglas que
salen de la captura del alimentador oficial:

1. **Cada trecho de corredor tiene su velocidad**, medida. Un trecho congestionado se ve como bus
   lento, no como bus plantado.
2. **Un bus troncal solo se detiene por dos razones**: hay cola para entrar al andén de su estación,
   o tiene un rojo. En mitad del corredor no se para, y el motor ya no lo hace.

## Lo que estaba mal, medido

Jueves simulado a las 6:40: 1.669 buses y **558 detenidos en tráfico (33 %)**, con la mitad de la
flota quieta contando atención y semáforos. En la captura del sábado la flota troncal real aparece
detenida el **28 %** del tiempo, y esa cifra está inflada porque un vehículo que no refresca su
posición repite la anterior y parece parado.

El presupuesto de tiempo no era el problema. La velocidad comercial que impone el horario publicado
—21,4 km/h entre paradas— coincide con la real medida por vehículo: **20,5 km/h de mediana y 21,1 de
media** sobre 1.033 buses con más de una hora de seguimiento. Lo que estaba mal era el reparto: el
motor rodaba al percentil 95 de la velocidad real y pagaba la diferencia parándose.

## La densidad, y por qué no se implementó

En bruto, sobre corredor abierto, un bus con seis vecinos a 330 m va a 16,2 km/h y uno sin vecinos a
31,0. Pero comparando **cada trecho consigo mismo**, el efecto se cae a 0,92 con seis vecinos y a
0,95 con cuatro; controlando además por hora, desaparece. La correlación fuerte es de composición:
los sitios con muchos buses son los sitios lentos, no al revés.

Lo que manda es el lugar. La velocidad de un trecho va de **10 km/h en el percentil 10 a 44 en el
percentil 90**, mientras el mismo trecho a distintas horas de la tarde del sábado solo varía entre
0,97 y 1,06 de su propia media. El campo por lugar ya contiene el efecto de densidad, así que no hay
término de densidad en vivo: por un 5–8 % no se mete el plan de despachos dentro del motor.

## El campo

`tools/build_speed_field.py` escribe `data/curated/speed_field.json`: por corredor, sentido y cubeta
de 100 m, **la velocidad de travesía** —lo que ese trecho le cuesta a un bus que pasa de largo— junto
con la parte del tiempo que ahí se está quieto, que viaja al lado como evidencia.

| | |
|---|---|
| Eje troncal cubierto | 113,8 km · 2.318 cubetas |
| Cubetas con medición propia | **2.194 (95 %)** · 82 suavizadas con vecinas · 42 por mediana del corredor |
| Pares de lecturas usados | 435.090 · 54.611 descartados por caer fuera del eje |
| Velocidad de travesía | p10 15,0 · mediana 29,9 · p90 45,5 km/h |
| Velocidad rodando, sin contar lo quieto | p10 16,6 · mediana 31,5 · p90 47,9 km/h |

**Qué se descuenta y por qué.** De las 2.638 h medidas, 1.988,7 h son marcha. Del resto:

| | |
|---|---|
| 170,0 h | atención en su propia parada destino, a menos de 60 m |
| 179,1 h | quieto en cualquier andén, a menos de 120 m de una estación |
| 151,6 h | quieto junto a un semáforo corroborado, a menos de 45 m |
| 148,7 h | quieto en mitad del corredor |

Las tres primeras salen del denominador de la velocidad: el motor ya modela la atención por embarque,
la cola por el vagón y las fases de los 723 semáforos corroborados, y contarlas aquí las cobraría dos
veces —se vio: los viajes salían siete minutos tarde—. La cuarta se queda dentro, y por eso un trecho
crónicamente atascado aparece como un trecho lento.

Sin esta separación un expreso de 15,5 km heredaba 19 minutos de espera que eran la atención de los
locales a los que adelanta.

Los corredores salen reconocibles: Autopista Norte 40,6 km/h rodando y 8 % de tiempo quieto, NQS
Central 41,2 y 10 %, Américas 30,4 y 13 %, **Caracas 20,9 km/h y 24 %**.

## Cómo lo usa el motor

`build_services.py` resuelve el campo a lo largo de cada ruta y escribe `app/dist/speed_profiles.json`
—117 servicios, cobertura mediana del **98 %**—. Por cada tramo entre paradas:

1. El bus rueda a la velocidad medida de cada trecho. El techo deja de ser plano: `travelProfile`
   acepta un límite por posición y las pasadas de aceleración y frenada que ya existían hacen
   progresivo el paso de un trecho al siguiente, como frente a una curva. El crucero del vehículo
   sigue siendo el techo absoluto.
2. **Un único factor por tramo** ajusta esa velocidad al tiempo publicado. Va de 0,45 a 3,0 en pasos
   de 0,05, se redondea siempre hacia arriba —para que el tramo no salga largo por el redondeo— y se
   corrige hasta tres veces con el tiempo ya medido, porque arrancar y frenar no escalan con la
   velocidad y el rojo que toca cambia al cambiarla. La variación de ±5 km/h por bus se pliega dentro
   del factor, así que el perfil de un tramo depende de un solo número y la caché no guarda cinco
   copias casi iguales.
3. **Todo el sobrante se gasta rodando más despacio.** Solo lo que no quepa ahí —el 0,5 % de los
   tramos, donde el factor toca su piso— se convierte en espera, y esa espera va entera a la
   aproximación a la estación siguiente, en trozos de 45 s, nunca por delante del último semáforo del
   tramo: si no queda aproximación libre, la cola se forma en el propio semáforo.
4. Las esperas se resuelven junto con los semáforos y no después: pararse antes de un rojo cambia la
   hora a la que se llega a él y por tanto su fase.

## Resultado

| | Antes | Ahora | Referencia real |
|---|---|---|---|
| Detenidos en tráfico, jueves 6:40 | 558 (33 %) | **106 (6 %)** | — |
| Flota quieta en total | 51 % | **25 %** | ≤ 28 % |
| Parte del tiempo entre paradas detenido | 39 % | **7 %** | — |
| Horas rodando / detenido | 10.891 / 7.673 | **17.237 / 1.467** | — |
| Espera por tramo: mediana · p90 · máximo | 77 · 257 · 1.883 s | **16 · 55 · 443 s** | — |
| Espera individual: mediana · p99 · máximo | bloques de 45 s | **21 · 44 · 80 s** | — |
| Velocidad comercial del simulador | 21,4 km/h | 21,4 km/h | 20,5–21,1 km/h |

Cada espera que queda está en la aproximación a una estación o en un semáforo, y ninguna pasa de 80
segundos.

**Puntualidad.** El viaje completo dura de mediana **2,1 minutos más** que el horario publicado
—antes eran 1,2— y ningún viaje se adelanta más de cinco minutos. El desfase se concentra en los
tramos cuyo tiempo publicado no se alcanza ni rodando al crucero, que son los mismos que ya se
quedaban cortos antes: un 19,5 % de los tramos pediría ir a más de 1,6 veces la velocidad medida el
sábado, y un 3,9 % a más de tres veces.

**Banco de referencia:** preparación 14,0 s (antes 11,0), muestreo **0,79 ms** por lectura (antes
1,32), caché de perfiles 128.229 entradas, heap 746 MB (antes 560). Ir y volver en el reloj devuelve
exactamente el mismo estado.

## Lo que asume, a sabiendas

1. **Un día, sábado, de 14:00 a 23:30**, aplicado a todas las horas y tipos de día. La punta de un
   laborable —justo donde se vio el problema— no está medida. Es la suposición grande.
2. La velocidad de travesía es distancia sobre tiempo y no le afecta el GPS que no refresca; el
   reparto entre lo que es marcha y lo que es parada sí lo arrastra, y por eso solo se usa como
   evidencia.
3. Las 124 cubetas sin medición propia heredan la mediana de su corredor y lo declaran en `source`.
4. Duales y calle conservan el modelo continuo anterior: el campo solo cubre corredor troncal.
5. La atención medida son 170 h, menos de lo esperable: cuando un bus abre puertas el alimentador ya
   puede apuntar a la parada siguiente. El descuento por andén, que no depende de eso, la cubre.
6. Sin término de densidad.
7. El factor llega hasta 3,0. En los tramos que lo tocan, la velocidad la marca el crucero del
   vehículo y el campo deja de decidir: son tramos cuyo tiempo publicado no cuadra con lo observado.

La semana que viene, con la captura completa, el trabajo es **volver a correr solo la fase del
campo**: el motor no cambia, cambia el archivo. Ahí se añaden hora y tipo de día, se mide si la punta
laborable justifica el término de densidad, y se revisa cuántos tramos siguen pidiendo más de lo que
el crucero da —si son los mismos, la conclusión es sobre el horario publicado y no sobre el motor.

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
