# Simulador de buses de Bogotá: sistemas y entregas

Actualizado el 9 de septiembre de 2026. Dirección confirmada por Daniel: un Bus Simulator del sistema BRT, **exclusivamente para un jugador**, con toda la red troncal como meta final, escala espacial 1:1 y apariencia cozy. La extensión del mundo y la operación tienen prioridad sobre gráficos complejos. Otros buses realizarán rutas mediante IA local. Las etapas iniciales no reducen ese objetivo.

## La experiencia completa

Elegir una fecha del escenario, un bus y un servicio disponible → consultar origen, destino, sentido y paradas → iniciar en un punto de salida válido → conducir por los carriles reales → atender únicamente las paradas de ese servicio, en el vagón y lado compatibles → terminar el recorrido y consultar un resumen sencillo. También habrá conducción libre por las zonas habilitadas.

Una troncal es infraestructura; un servicio es una secuencia de paradas que puede atravesar varias troncales. El mapa, el grafo de carriles y el catálogo de servicios deben mantenerse separados. El juego no debe ofrecer una ruta completa si parte de su recorrido todavía no es transitable: podrá ofrecer un tramo de prueba identificado como tal, sin presentarlo como el servicio oficial completo.

## Orden de prioridades

1. Metros reales, conexiones correctas, niveles de vías y espacios de maniobra.
2. Conducción de un bus largo, puertas, parada y continuidad de un recorrido.
3. Crecimiento de la red, selección de servicios, actualización de obras y guardado.
4. Ciudad reconocible desde la cabina, sonido y vida urbana suficiente.
5. Detalle artístico adicional donde mejore la experiencia y el rendimiento lo permita.

## Inventario de sistemas

| Sistema | Primera entrega utilizable | Ampliación posterior | Depende de |
|---|---|---|---|
| Entrada y opciones | Teclado, ayuda, pausa, volumen y cámara | Reasignación, mando/volante, accesibilidad | Interfaz y controlador |
| Garaje y vehículos | Un articulado provisional con ficha de dimensiones | Vehículos reales, biarticulados, duales y variantes de pintura | Modelos y especificaciones verificadas |
| Conducción | Aceleración, freno, reversa, dirección y articulación; colisiones de todos los cuerpos | Pendientes, suspensión visual, ajustes por variante | Superficies y geometría del bus |
| Cabina e instrumentos | Velocidad, marcha, estado de puertas y cámaras | Espejos, luces, limpiaparabrisas y tablero de la variante | Modelo y rendimiento |
| Estaciones | Punto de detención, lado de puertas, tolerancias y ciclo de atención | Vagones, puertas de plataforma, accesos y portales especiales | Carriles, medidas y vehículo |
| Servicios y selector | Servicio de prueba, lista de paradas y sentido | Catálogo oficial, variantes, calendarios y horarios | Importador, carriles y cobertura comprobada |
| Navegación | Próxima parada, distancia y orientación | Mapa de red, instrucciones de desvío y señalización de servicio | Itinerario sobre carriles |
| Pasajeros | Tiempo de intercambio y conteo sencillo | Personas visibles, colas y demanda por parada | Ciclo de puertas y estación |
| Buses con IA local | Un NPC que sigue carriles, se detiene y abre puertas en ensayo | Colas, reservas de dársena/intersección, despachos reales y simulación lejana | Grafo dirigido, anclajes, controlador y vigencia |
| Tráfico mixto | Conflictos básicos con buses y semáforos | Adelantamiento permitido y vehículos de contexto en operación dual | IA de buses y prioridades verificadas |
| Mundo por sectores | Carga del entorno cercano, colisiones preparadas antes de entrar | LOD, precarga por itinerario y cambio de origen | Geografía estable y pruebas de bordes |
| Obras y fechas | Cierres y variantes de una zona, con evidencia | Actualizaciones de la 68 y otros nodos | Carriles, geometría y catálogo fechado |
| Guardado | Bus, posición válida, servicio y siguiente parada | Migraciones al cambiar mapa/rutas | Versiones estables e IDs persistentes |
| Sonido y ambiente | Motor/movimiento, puertas y aviso propio | Paisaje sonoro, clima, noche y anuncios con recursos autorizados | Audio original o licenciado |
| Resultado de viaje | Paradas atendidas y recorrido terminado | Regularidad y comodidad opcionales | Operación y telemetría local |
| Distribución | Proyecto reproducible y respaldo Git | Exportación e instalador si Daniel decide publicar | Licencias, rendimiento y pruebas |

Son sistemas planificados, no una afirmación de que ya existan. El estado implementado y sus límites se registran en CONTINUAR.md.

## Entregas que se pueden jugar y revisar

**A. Escuela de conducción.** Pista de dimensiones conocidas, un articulado, maniobras de aproximación y reversa, puertas y una plataforma de ensayo. Sirve para comprobar controles y articulación. Su geometría es diseñada para la prueba y no representa una estación real.

**B. Mandalay y primer tramo de Américas.** Sustituir la plataforma de ensayo por una estación verificada; construir calzada, carriles y separadores. Confirmar alturas y niveles antes de habilitar Av. Boyacá. Completar parada y salida desde la cabina.

**C. Marsella–Boyacá–Mandalay.** Recorrido continuo, tres estaciones reconocibles, indicadores de siguiente parada y un servicio de prueba. Introducir guardado y selector mínimo antes de ampliar varios kilómetros. Medir rendimiento durante conducción, no solo desde cámara aérea.

Con el pequeño grafo de C disponible, probar primero un NPC en circuito y luego varios buses con colas en una dársena. No esperar a completar toda Bogotá para comprobar esos conflictos. Los servicios oficiales de los NPC llegarán cuando la cobertura y los patrones estén verificados. La [ficha de IA](IA_DE_BUSES.md) define las fases, el estado que se guarda y los criterios de aceptación; la implementación sigue pendiente.

**D. Américas ampliada y Calle 13.** Carga por sectores, portales y conexiones que correspondan, capa de obras de Carrera 50 y 68 cuando se alcance cada zona. Primer patrón de servicio real únicamente al verificar su recorrido, paradas, sentido y fecha.

**E. Red prioritaria conectada.** NQS, Calle 26, centro y Séptima, con vehículos duales donde corresponda. El orden fino depende de qué conexiones desbloquean recorridos completos. Pasajeros y tráfico básicos se añaden sin esperar a modelar la ciudad entera.

**F. Toda la red.** Mantener una matriz por troncal, sector, estación y conexión: datos localizados → geometría generada → niveles revisados → conducción comprobada → servicios habilitados → entorno mejorado. Expandir por paquetes de recorridos útiles. No es necesario modelar todas las calles de Bogotá para simular todo el sistema BRT.

**G. Madurez y publicación opcional.** Pruebas largas, configuración de controles, calidad visual consistente y empaquetado. El respaldo en GitHub está autorizado ahora; una publicación del juego se decidirá después.

## Criterios que evitan rehacer el proyecto

- Una actualización de obra puede cerrar un carril, habilitar otro o mover una parada; no debe sobrescribir la cartografía original. Mantener fecha, evidencia y escenario anterior.
- Separar posición geográfica global de coordenadas locales de físicas. No comprimir distancias para que quepan en memoria: cargar sectores alrededor del bus.
- Cada vehículo declara sus puertas, ejes y articulaciones. Las estaciones usan puntos de parada compatibles; no codificar todas las medidas para un solo bus.
- Un servicio incluye ambos sentidos y variantes cuando existan, con vigencia. El nombre visible no es el identificador del registro.
- Las partidas guardan versión de mapa y servicio. Si cambia una zona, recuperar en una parada o patio seguro y explicar el ajuste; no reaparecer dentro de una obra.
- Los modelos originales, configuraciones y herramientas de generación se versionan. Los datos y texturas grandes tendrán manifiestos y descargas separadas cuando el tamaño deje de ser razonable para Git.

## Qué queda fuera de la prioridad

Multijugador queda fuera del alcance por decisión explícita de Daniel. Economía empresarial, gestión exhaustiva de baterías/mecánica, interiores de todos los edificios, ciudad fotogramétrica completa y simulación individual de toda la población tampoco condicionan el objetivo de conducir servicios troncales por una Bogotá grande y reconocible.

## Organización del trabajo

La [dirección visual](DIRECCION_VISUAL.md) fija materiales, siluetas y reparto de detalle conservando metros reales. La [guía de agentes ligeros](TRABAJO_CON_AGENTES.md) define investigación acotada y normalización delegables. El principal integra sus resultados y comprueba física, escenas y datos. Las revisiones de Daniel se concentrarán en hitos completos, incorporando las correcciones puntuales con validación interna.

## Referencias operativas

- [Buscador oficial de rutas](https://buscador-rutas.transmilenio.gov.co/rutas): aportado por Daniel. La página carga mediante JavaScript; validar datos y actualización antes de importar.
- [Mapa digital del sistema](https://mapadigital.transmilenio.gov.co): contraste visual de estaciones y servicios.

Las rutas fáciles, troncales, duales y zonales deben clasificarse por información oficial. No asumir que una letra y dos números identifica todos y únicamente los servicios de interés ni fijar sin verificar que las rutas fáciles actuales terminan en el 8.
