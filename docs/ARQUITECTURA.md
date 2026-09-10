# Arquitectura de Transmi 2D

Dirección vigente desde el 10 de septiembre de 2026. El simulador 3D y su arquitectura anterior están en `archive/transmi3d`.

## Separación de responsabilidades

`data/raw` conserva instantáneas fechadas. `tools/fetch_services.py` descarga y filtra campos de transporte; conserva URL, método, fecha y hashes sin metadatos administrativos. `tools/geo.py` define AEQD local en metros. El normalizador produce un catálogo apto para el visor y un informe separado de problemas; nunca rellena una geometría ausente con segmentos rectos inventados.

La aplicación `app/dist` usa módulos JavaScript y Three.js local. El modelo operativo está separado de la cámara y los símbolos. El laboratorio previo de pasos fijos se mantiene para pruebas; el modelo de servicios puede usar perfiles analíticos de viaje y despachos/eventos, apropiados para avance y retroceso deterministas y miles de vehículos.

## Contratos principales

| Entidad | Campos esenciales |
|---|---|
| Snapshot | ID, fecha de consulta, fuentes, hashes, vigencia y licencias por fuente |
| RouteVariant | ID del proveedor, código, destino, zona, variante, calendario, geometría y estados de validación |
| Stop | ID/código, nombre, coordenadas, estación/paradero calle, estado de obra, procedencia |
| RouteStop | ID de parada, orden, distancia sobre trazado, punto/andén/vagón si se conoce, confianza |
| ServiceCalendar | Días, intervalos, excepciones, rango de fechas, interpretación de zona horaria |
| DispatchProfile | Intervalos pico/valle, headway, fase determinista, fuente o marca de estimación |
| Trip | ID estable, variante, día, despacho, vehículo, progreso, atención, finalización |
| DirectedEdge | Geometría métrica, sentido, nivel, conexiones explícitas, carril de paso/atención |
| StationOperation | Berths por sentido, asignación de servicio, capacidad, acceso y bypass |

Las rutas comparten paradas y, cuando esté validado, aristas. El modelo inicial fluido evita colas ficticias entre servicios independientes; la ocupación de berths y conflictos físicos se añaden como eventos locales cuando haya datos suficientes. La separación visual de iconos no modifica su posición lógica ni longitud del trazado.

## Tiempo reproducible

El reloj representa fecha/hora de Bogotá. La velocidad del reloj es independiente de m/s. Un estado se identifica por instantánea, selección, parámetros y tiempo. Los despachos tienen identidad determinista; un salto temporal reconstruye los viajes activos a ese instante. No acumular errores por invertir pasos físicos ni hacer depender la operación de si un bus está visible.

Calendarios y perfiles de frecuencia se mantienen separados. Si solo se conocen ventanas horarias, la frecuencia es una hipótesis rotulada. Fin de atención no equivale a fin de calendario; los últimos viajes pueden terminar después de la última salida.

## Geografía y dibujo

WGS84 → AEQD, origen lon −74.136, lat 4.63027; X este / Y norte. Guardar coordenadas fuente y doble precisión para cálculos. El redondeo del archivo no aumenta la precisión de la fuente. No se usa la compresión 3D.

Three.js: cámara ortográfica, mallas compartidas/instancias y geografía generalizada solo para representación. Los detalles a nivel de estación y el contexto urbano usan niveles de zoom. Todos los servicios permanecen en el modelo aunque se filtren o agrupen símbolos. La lista de selección debe seguir siendo usable cuando el mapa esté muy alejado.

## Validación

Comprobar IDs, procedencia, secuencia, geometrías vacías/discontinuas, extremos, fechas, horarios partidos, cruce de medianoche, festivos y variantes superpuestas. Comprobar desplazamiento por metros, coherencia 1×/acelerado, reconstrucción adelante/atrás, identidad de viajes y paso independiente de parada. Medir por separado normalización, núcleo, dibujo, memoria y legibilidad; no extrapolar FPS desde un benchmark de CPU.
