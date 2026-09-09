# IA local de buses NPC

Plan actualizado el 9 de septiembre de 2026. Petición explícita de Daniel: ver otros buses realizando rutas en un juego exclusivamente para un jugador.

## Alcance

El juego tendrá un solo jugador. Los buses NPC ejecutarán rutas dentro del juego mediante una IA local determinista o reproducible, sin un LLM, sin una API por bus y sin dependencia de servicios de red durante la partida. La IA debe seguir carriles y servicios, detenerse en paradas, operar puertas, mantener distancia, reservar espacios de conflicto y recuperarse de bloqueos.

Esta ficha describe arquitectura y criterios de aceptación; **no afirma que estas funciones ya estén implementadas**.

## Responsabilidades del agente

Cada bus NPC mantiene un estado pequeño y observable:

- servicio, viaje, sector y sentido actuales;
- segmento de grafo, carril objetivo y siguiente maniobra;
- velocidad objetivo, distancia de seguimiento y causa de detención;
- parada siguiente, estado de arribo, puertas y tiempo de servicio;
- reservas activas de dársena, intersección u otra zona exclusiva;
- reloj de recuperación si el bus se desvía o encuentra un bloqueo.

El agente usa el grafo validado y sus restricciones. No inventa conexiones cuando falta geometría o fecha de vigencia. El jugador comparte el mismo espacio y reglas de colisión, pero la simulación de buses lejanos puede reducirse a estados de viaje y tiempos acumulados.

## Flujo de decisión

En cada actualización de simulación, el bus:

1. valida el tramo y la fecha de vigencia del servicio;
2. busca el carril o trayectoria permitida hacia el siguiente nodo;
3. consulta reservas y distancia de seguridad;
4. calcula una velocidad objetivo con límites del tramo y del estado de parada;
5. solicita, mantiene o libera reservas antes de entrar en una zona conflictiva;
6. ejecuta llegada, cola, apertura de puertas, abordaje simulado y salida;
7. registra desviaciones, espera y bloqueos para diagnóstico.

Una solicitud de reserva no utilizada puede caducar; una zona ocupada permanece reservada hasta confirmar que todo el bus y su remolque la han liberado. Un tiempo de espera excesivo activa diagnóstico, no la liberación ciega de esa zona. El planificador puede esperar o elegir una conexión alternativa validada. Una maniobra de reversa exige espacio libre comprobado y protección de la cola. La recuperación mediante recolocación solo se considerará fuera de la vista del jugador, sobre un punto libre validado y dejando registro; nunca debe atravesar geometría ni saltarse restricciones para alcanzar un horario.

## Fases de desarrollo

### 1. Un NPC en circuito de ensayo

Un único bus recorre un circuito corto y validado, mantiene el carril, llega a una parada y usa las puertas. El jugador puede observarlo y provocar una detención sin que el bus atraviese obstáculos.

### 2. Varios buses, detención y colas

Se añaden varios buses en el circuito. Deben mantener separación, formar una cola en la parada, ocupar y liberar una dársena y evitar el bloqueo mutuo en una intersección.

### 3. Servicios reales sobre grafo validado

Los buses se instancian desde servicios y viajes normalizados. Las rutas respetan sentido, paradas, carriles disponibles y vigencia de las obras. Un servicio sin geometría o con fecha incompatible queda fuera del despacho y genera un diagnóstico.

### 4. Streaming por sectores

Los sectores cercanos al jugador usan simulación completa. Los sectores lejanos conservan posición lógica, próxima parada, reservas relevantes y tiempo estimado. Un único gestor será responsable de cada bus durante el cambio de representación, para evitar duplicados. Al volver a estar cerca, el bus se materializa fuera de la vista, en un punto libre válido; si no hay espacio, espera. Los buses visibles permanecen en simulación completa y no desaparecen al cruzar un límite de sector.

## Criterios de aceptación

- Un bus de prueba completa al menos 20 vueltas sin salirse del corredor ni atravesar obstáculos.
- En una parada, el bus llega a la dársena correcta, se detiene antes de abrir puertas, espera el tiempo configurado, cierra puertas y libera la reserva.
- Con al menos 10 buses, una cola de parada conserva el orden y no produce solapes persistentes ni bloqueo circular durante una prueba de 10 minutos.
- Dos buses que solicitan la misma intersección reciben reservas compatibles o esperan; ninguno entra en una zona reservada por otro.
- Si se bloquea una ruta, el bus informa el motivo y ejecuta una recuperación válida; no crea una conexión nueva.
- Un servicio cuya geometría u obra no está vigente para la fecha de escenario no se despacha.
- El jugador puede circular mientras los NPC mantienen colisiones, distancias y prioridades reproducibles.
- Al descargar y recargar un sector, el bus conserva servicio, sentido, próxima parada y estado de puertas dentro de las tolerancias definidas.

## Rendimiento y medición

El objetivo inicial es medir, no asumir, el coste. Cada prueba registrará buses activos y abstractos, frecuencia de actualización, tiempo de CPU de IA, memoria, FPS y percentiles de tiempo por cuadro en el M3 Pro. Aumentar la densidad de forma escalonada: 1, 5, 10 y, como estrés posterior, 25 y 50 buses. Estas cantidades no prometen capacidad de producción. El objetivo global provisional es 30 FPS sostenidos a 1080p y aspiración de 60; se fijará un presupuesto de CPU para IA tras medir el recorrido base y un NPC.

La prueba debe repetirse con jugador quieto, jugador conduciendo, parada saturada, intersección con reservas y streaming de sectores. Guardar resultados y configuración junto con cada medición para que las regresiones sean comparables.

## Dependencias y orden de integración

El siguiente hito sigue siendo una estación y una sección BRT transitables. Una vez que el controlador, los anclajes y un pequeño grafo de carriles estén definidos, introducir un NPC en ensayo antes de expandir toda la red. La cola de varios buses debe probarse antes de conectar numerosos servicios. El despachador de servicios reales y la simulación lejana requieren IDs persistentes, cobertura validada y guardado de estado. Ver [hoja de ruta](SISTEMAS_Y_HOJA_DE_RUTA.md).

## Obras y fechas

Toda restricción de obra debe tener geometría, estado y fechas de vigencia. El despachador consulta la fecha del escenario antes de construir el viaje. Una obra que cierre un carril o una parada debe cambiar la red disponible, las reservas y las paradas accesibles; no basta con ocultar visualmente el tramo. Cuando no exista una fecha o geometría verificable, el servicio se marca pendiente y no se presenta como operación confirmada.
