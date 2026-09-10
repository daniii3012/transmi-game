# Plan de Transmi 2D

Versión 1.0 · 10 de septiembre de 2026. Sustituye la dirección activa del proyecto 3D, archivada en `archive/transmi3d`.

## Alcance confirmado

Simular todas las rutas **troncales y duales** de TransMilenio, incluyendo estaciones, portales y paradas de calle sobre Séptima y Avenida 68. Daniel confirmó que las zonales quedan para después. Un solo jugador; experiencia de observación y selección de la operación existente. No se construyen nuevas líneas ni se exige conducir un bus.

Geografía de Bogotá **1:1**, con forma y distancias reales. La legibilidad se resuelve con zoom, símbolos y nivel de detalle, sin comprimir espacios entre estaciones. Se mantienen los recorridos de los enlaces: puentes, deprimidos, retornos y rotondas cuando estén publicados o verificados. No unir trazos solo porque se cruzan.

Todos los avances de Godot y Blender se conservan y quedan **en pausa hasta nuevo aviso**. No invertir trabajo en nuevos modelos, cabinas o física 3D. El repositorio y la planificación principal se dedican a 2D.

## Qué puede hacer el usuario

- Elegir una ruta y su variante/sentido, una o varias zonas por letra, o toda la red disponible.
- Observar buses, próxima parada, recorrido y estaciones. Filtrar la vista no debe borrar vehículos de una simulación en marcha.
- Elegir fecha y hora, pausar, avanzar a 1× o acelerar; adelantar y retroceder la hora con reconstrucción consistente del estado.
- Observar diferencias entre lunes–viernes, sábado, domingo/festivo y horas pico/valle.
- Distinguir rutas disponibles, inactivas para ese momento y pendientes por falta de datos. Ninguna ruta se considera completa solo por aparecer en el catálogo.

«Tiempo real» significa un segundo simulado por segundo de reloj en 1×. No se solicitan posiciones GPS en vivo. Los datos se descargan al preparar una instantánea y el juego funciona localmente.

Selección por zona: inicialmente rutas cuyo destino/troncal de catálogo pertenece a cualquiera de las letras seleccionadas. La opción de rutas que **atraviesan** una zona necesita intersección con aristas del recorrido; no inferirla solo por el código del destino. La interfaz debe expresar qué criterio usa.

## Simulación híbrida adoptada

Daniel delegó la decisión y pidió evitar atascos artificiales. Se conservan unidades y posiciones reales. Se simplifica la interacción de circulación, no la geografía:

1. **Modelo operativo fluido como base.** Recorrido métrico, velocidad coherente, parada/atención y despacho con reloj. La oferta produce la flota necesaria; no llenar todos los corredores con un número fijo de buses.
2. **Paso y atención independientes.** Un bus que no sirve una estación pasa por el carril correspondiente sin heredar su cola. Las estaciones, accesos y paradas en calle no comparten automáticamente el mismo perfil de dos carriles.
3. **Detalle progresivo de vagones y carriles.** Punto de atención y capacidad por sentido cuando haya asignación verificada. Hasta entonces, atención simplificada y agregación visual de coincidencias; no inventar A/B/C ni bloquear toda la troncal con un andén ficticio.
4. **Conflictos locales solo con topología suficiente.** Reservas y colas cortas en accesos o cruces verificados; una falta de datos no debe crear bloqueos permanentes. La simulación lejana puede usar eventos y perfiles de tiempo/distancia.
5. **Nada de eliminar buses para ocultar congestión.** Conservar identidades, despachos y viajes. Al alejarse se pueden agrupar símbolos, manteniendo los estados de operación. Un modo congestionado detallado no es requisito actual.

Velocidades, tiempos de atención y frecuencias son parámetros distintos. Los valores de ensayo no son mediciones de TransMilenio. Calibrar velocidad comercial por corredor con tiempos de recorrido o indicadores publicados; limitar aceleración/velocidad por perfiles coherentes. Acelerar el reloj no cambia km/h ni kilómetros.

## Datos y cobertura

El mapa digital consultado devuelve **116 registros y 100 códigos distintos**: incluye destinos y versiones repetidas. Se ha descargado una instantánea de **132 registros seleccionados**, los 116 del mapa más 16 candidatos complementarios de familias duales, con sus 132 respuestas de detalle. **19 carecen de trazado** en esa descarga. El catálogo candidato amplio contiene más registros y no es un inventario ya validado de rutas del alcance.

El detalle oficial publica trazado, paradas ordenadas y ventanas horarias por tipo de día. Se conservan IDs, códigos, nombres, geometría, posiciones de recorrido y fechas. La API de cartografía del mapa aporta colores, estado y número de vagones de estaciones, pero no asignación servicio→vagón. La API de planos usa posiciones relativas de una imagen: no convertir porcentajes en coordenadas de Bogotá.

M85/P85 sí tienen detalles publicados, incluyendo paradas en AK 68. Hay variantes de Ciclovía que no deben circular simultáneamente con la base por asumir que todos sus horarios se acumulan. Hay geometrías ausentes o inconsistentes en algunas variantes duales; deben quedar pendientes, como autorizó Daniel, hasta resolverlas.

Cada ruta tendrá estado de validación separado para catálogo, calendario, geometría, paradas, frecuencias y plataforma. Una fuente oficial consultada no acredita por sí sola cada desvío actual. Guardar fecha de escenario, fechas declaradas por el proveedor, fecha de consulta y evidencia de excepciones.

No se encontró frecuencia/headway ni tipo de bus por ruta en el contrato inspeccionado. Usar buses homogéneos hasta verificarlo. Para pico/valle, guardar un perfil de despachos **estimado y configurable**, distinto del horario oficial. Nunca rotularlo como frecuencia real. La cobertura final se mide por IDs/variantes elegibles para una fecha, no solo por códigos ni por flota sintética.

## Estaciones, paradas y cruces

Separar estación, vagón, plataforma/sentido, punto de atención y visita de un servicio. Respetar que no todas las rutas paran en todas las estaciones y que una misma estación puede tener puntos de atención distintos. Los buses expresos usan paso independiente.

Mantener todos los puntos publicados, incluidos los que estén en obras o no tengan servicios activos. Las paradas de calle requieren coordenadas contrastadas: la cadena `posicion` del detalle de ruta aproxima distancia sobre el trazado, pero no es una coordenada levantada. Si se usa para un marcador provisional debe indicarse su procedencia y limitación.

La geometría de cada ruta conserva sus giros. Para compartir carriles se necesita una red dirigida con nivel, sentido y conexión permitida; un dibujo cenital no basta para inferir un giro legal. Cambios de obra y variantes tendrán versiones y vigencia. No abrir la troncal 68 completa porque exista P85/M85 parcial.

## Reloj y calendario

Hora civil de Bogotá, UTC−05 sin cambio estacional, con fecha de servicio explícita. Admitir horarios partidos, fin al día siguiente, cambios de día y festivos. Separar ventanas en que se despacha un viaje de la finalización del último bus; documentar esa interpretación si la fuente no define ambos.

Retroceder reconstruye el estado a partir de despachos/eventos o un punto de control determinista; no integrar movimiento con tiempo negativo. Cambiar el conjunto simulado reconstruye solo con la configuración confirmada y mantiene fecha/hora. Los viajes y puntos de control identifican versión de datos y parámetros.

Las fechas UTC a medianoche del proveedor requieren tratarse como etiquetas de vigencia según el contrato verificado; no desplazarlas al día anterior por conversión automática. Las variantes de Ciclovía y festivos son excepciones explícitas, no reglas adivinadas desde un nombre.

## Hitos

| Hito | Entrega y aceptación | Estado |
|---|---|---|
| 0 · Reorganización | 2D principal, 3D conservado en pausa, fuentes comunes y pruebas recuperables | Integración actual |
| 1 · Inventario publicado | Catálogo del mapa más duales, detalle/fechas/horarios/trazados, auditoría de huecos | Descarga inicial completa; validación en curso |
| 2 · Operación de servicios | Primeros servicios con trazado real, atención de paradas, calendario, despachos estimados y selección | Siguiente implementación |
| 3 · Reloj de escenario | Fecha, saltos adelante/atrás, fines de semana y excepciones, estados reproducibles | Por integrar |
| 4 · Cobertura del alcance | Todos los servicios elegibles que tengan datos suficientes y lista explícita de pendientes | Por ampliar |
| 5 · Estaciones e intercambio | Paso independiente, vagones/berths verificados, carriles compartidos y giros donde corresponda | Por ampliar |
| 6 · Contexto y escala visual | Mapa urbano tenue, calles/agua/verde a distintas escalas, símbolos y colores legibles | Dirección definida; contexto por incorporar |
| 7 · Calidad | Rendimiento de mapa y flota, guardados, recuperación, accesibilidad y empaquetado local | Pendiente |

No se considera terminada la simulación completa por animar 132 recorridos: faltan vigencia, extremos, conflictos y calibración. El laboratorio anterior queda como herramienta de regresión, no como operación real.

## Documentación y forma de trabajo

Documentar cómo se descargan, filtran, proyectan y validan los datos; cómo se calculan despachos, perfiles de viaje y reconstrucción temporal; y las decisiones de fidelidad frente a simplificación. Actualizar CONTINUAR.md por hito y respaldar en GitHub. Mantener fuentes crudas inmutables, hashes y resultados reproducibles.

Agentes ligeros pueden investigar una fuente o normalizar un conjunto acotado; arquitectura e integración siguen con el principal. No depende de ejecución automática cuando la sesión esté cerrada. Revisiones con Daniel por hitos coherentes; no pedir ensayos manuales tras cada ajuste.

## Referencias

- [Mapa digital oficial](https://mapadigital.transmilenio.gov.co/) y [detalle de ruta 690](https://api.buscador-rutas.transmilenio.gov.co/api/v1/rutas/690/rutaDetalle).
- [Buscador de rutas](https://buscador-rutas.transmilenio.gov.co/rutas) y [API de planos](https://tramites.transmilenio.gov.co/station-maps/api/map).
- [Subway Builder](https://www.subwaybuilder.com/) orienta la presentación cartográfica, no el alcance de construcción de red.
- [Mapa de Wikimedia](https://commons.wikimedia.org/wiki/File:TransMilenio_Bogota_Map.png): última versión de archivo indicada, 21 de diciembre de 2019; referencia histórica, no prueba de vigencia 2026.
