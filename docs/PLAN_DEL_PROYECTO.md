# Plan de desarrollo de Bogotá Transmi

Versión 0.5 · 9 de septiembre de 2026 · Proyecto personal de Daniel.

## 1. Experiencia que construiremos

Un simulador arcade en primera y tercera persona donde sea agradable conducir buses reconocibles de TransMilenio por una Bogotá condensada. Toda la red BRT sigue siendo la meta; las estaciones, conexiones y lugares importantes conservan su identidad. Los tramos intermedios pueden acortarse mediante reglas documentadas. Anchos, vehículos, plataformas y maniobras usan metros jugables coherentes. La apariencia deberá hacer reconocible la ciudad desde la cabina: vías, estaciones, separadores, puentes, fachadas próximas, señalización y cerros cuando corresponda.

La dirección visual confirmada es **Bogotá cozy y condensada**: formas suaves con volumen, materiales mate, paleta contenida, luz cuidada y detalle selectivo. over the hill y las referencias de Nick y Givros orientan ese acabado; su análisis y límites de acceso están en [DIRECCION_VISUAL.md](DIRECCION_VISUAL.md). Daniel reconsideró el 1:1 global y autorizó continuar con la propuesta de compresión selectiva. La cartografía original permanece intacta; el mundo jugable tendrá su propia disposición y longitudes. La primera hipótesis aplica factor 0,5 únicamente en intervalos elegibles y conserva estaciones y cruces como zonas protegidas. El factor definitivo se decidirá por corredor tras validar las maniobras; no se establece una escala 1:2 universal. Ver [ESCALA_Y_COMPRESION.md](ESCALA_Y_COMPRESION.md).

El objetivo final es un **Bus Simulator centrado en Bogotá y en todo el sistema BRT de TransMilenio**. Prioridad: red reconocible, proporciones coherentes y operación de buses, con un acabado visual agradable y sostenible. El usuario contempla publicarlo en el futuro si alcanza un buen desarrollo; hoy seguimos construyendo el proyecto personal, sin lanzar una distribución. La primera plataforma será su Mac; el diseño conservará la posibilidad de exportar a Windows más adelante. El juego será exclusivamente para un jugador y funcionará sin conexión permanente. Otros buses recorrerán rutas mediante IA local. Multijugador queda fuera del alcance del proyecto; economía de operadores, interiores de toda la ciudad, simulación mecánica exhaustiva y todos los servicios zonales tampoco son requisitos.

## 2. Alcance geográfico acordado

| Orden de expansión propuesto | Zona | Propósito y dificultad |
|---|---|---|
| Prueba actual | Américas: Marsella–Av. Boyacá–Mandalay | Validar datos y escala en un recorte. Unos 1,24 km entre centros extremos en línea recta; medir el recorrido de carriles por separado. |
| Estudio de condensación | Eje del mismo piloto, con 180 m adicionales por extremo | Comparación implementada: 1.602,47 m de eje fuente y 1.285,94 m jugables propuestos; tres estaciones y reservas intactas. No habilita circulación por Boyacá. |
| Primera zona jugable | El mismo tramo, con una estación detallada y después las tres | Conducir, frenar, aproximarse al andén, abrir puertas y continuar. Revisar el cruce a desnivel de Boyacá antes de habilitarlo. |
| Expansión 1 | Américas hacia Pradera, Distrito Grafiti y Puente Aranda; después Banderas y Portal Américas | Conectar la base con el nodo de obras señalado por Daniel y ampliar el recorrido. |
| Expansión 2 | Calle 13 existente hacia el centro | Incorporar el nodo Carrera 50, Ricaurte y conexiones urbanas con una versión fechada de las obras. |
| Expansión 3 | NQS / Carrera 30 y Calle 26 | Conectar corredores; aumenta el trabajo de puentes, rampas, intersecciones y estaciones especiales. |
| Expansión 4 | Centro y Carrera Séptima | Añadir operación dual, accesos particulares y circulación en tráfico mixto. |

**Meta final: toda la red troncal**, sus portales, conexiones y servicios pertinentes. Los corredores elegidos son el orden de trabajo inicial, no el límite del juego. La ampliación a los demás corredores se planifica con un inventario de cobertura por sectores y estaciones, sin declarar operativa una zona no comprobada. La selección del recorte inicial es técnica y reversible. La extensión final de cada corredor y las conexiones exactas se fijarán cuando recorramos los datos y el primer tramo jugable. La Nueva Calle 13 en construcción no debe aparecer completa ni operativa por asumir que forma parte de la red futura.

## 3. Herramientas y decisión inicial

| Herramienta | Uso | Decisión |
|---|---|---|
| Godot 4.7.2 | Juego, cámara, vehículos, interacción, carga de sectores y exportación | Base inicial instalada de forma local. Su proyecto de texto y ejecución por comandos facilitan mantenerlo y comprobarlo. |
| Blender 5.2.1 para Apple Silicon | Modelado de buses, cabinas, estaciones, puentes y materiales; exportación glTF/GLB | Instalado por Daniel; primer articulado de ensayo generado. |
| Python + pyproj + Shapely + Earcut | Descargar, recortar, reproyectar y triangular datos | Entorno ya preparado; versiones fijadas. |
| QGIS | Inspección visual de datos, medidas y edición geográfica manual cuando aporte valor | Opcional; la descarga y conversión actuales no dependen de instalarlo. |
| Git + GitHub | Versionar código, decisiones y progreso | Repositorio autorizado: daniii3012/transmi-game. Guardar hitos pequeños; separar datos pesados y binarios al crecer. |

Godot es compatible con Apple Silicon y se distribuye como una aplicación independiente. Es una elección inicial adecuada para probar este alcance en el M3 Pro con 18 GB, no una garantía de que cualquier tamaño de ciudad funcionará sin optimización. [Descarga oficial](https://godotengine.org/download/macos/) y [requisitos](https://docs.godotengine.org/en/stable/about/system_requirements.html).

Unity también es viable y ofrece un ecosistema amplio de herramientas; Unreal tiene recursos potentes para mundos grandes y renderizado, pero su recomendación de memoria para macOS es de 32 GB o más. Para este proyecto empezamos con una base más ligera y comprobamos rendimiento antes de comprometernos con toda la ciudad. No hay motivo para instalar los tres motores ahora. [Unity](https://docs.unity3d.com/6000.0/Documentation/Manual/system-requirements.html), [Unreal en macOS](https://dev.epicgames.com/documentation/unreal-engine/macos-development-requirements-for-unreal-engine?lang=en-US).

Blender complementa al motor: genera objetos y animaciones; el motor los convierte en una experiencia interactiva. Los recursos propios se conservarán en formatos transportables. Cambiar de motor seguiría costando trabajo en la lógica del juego. [Blender para Apple Silicon](https://www.blender.org/download/lts/4-2/).

## 4. Cómo construir la ciudad

1. **Adquirir y fechar los datos.** Descargar vectores de Catastro/IDECA y TransMilenio por sectores. Guardar URL, licencia, fecha del dato, consulta y hash. La fecha de descarga no demuestra actualidad de todos los objetos.
2. **Trabajar en metros.** Transformar coordenadas a un sistema local documentado. Evitar usar grados o coordenadas geográficas enormes directamente en las físicas.
3. **Construir el suelo y los niveles.** Para el juego, reemplazar el plano provisional por un terreno con alturas; reconstruir rampas, puentes y deprimidos como estructuras específicas. Un cruce visto desde arriba no necesariamente conecta dos vías.
4. **Generar las superficies viales.** Partir de polígonos de calzada y andenes. Añadir carriles dirigidos, bordillos, separadores, marcas y colisiones. El trazado general de una troncal sirve para localizar el corredor; no describe cada carril ni su ancho.
5. **Generar edificios de contexto.** Extruir huellas reales usando alturas verificadas cuando existan; si se estima por pisos, conservar ese indicador. Añadir una biblioteca de materiales de ladrillo, concreto, comercio y cubiertas, y modelos particulares para edificios visibles o emblemáticos.
6. **Modelar las piezas reconocibles.** Estaciones y sus accesos, mobiliario, señalización, puentes y zonas de obra necesitan geometría dedicada. Reutilizar módulos, con medidas y configuración por sitio.
7. **Dividir en sectores.** Objetivo inicial: celdas de aproximadamente 250–500 m, cargadas alrededor del bus. Mantener más detalle cerca y mallas simplificadas a distancia. Usar instancias para elementos repetidos.
8. **Validar desde la cabina.** Contrastar alineación, ancho, visibilidad de señales, altura del andén y espacio de giro con referencias fechadas. La vista aérea por sí sola no valida una calle para conducir.

Entre reproyección y construcción se añade una **capa de disposición jugable**: identifica zonas protegidas, acorta conectores elegibles y registra distancias reales/jugables por ID. Los edificios se seleccionan o reorganizan como módulos con dimensiones propias; no se aplastan polígonos catastrales. Estaciones y cruces requieren espacio para sus accesos y maniobras. Una red con ramificaciones o ciclos necesitará resolver todos los nodos compartidos en conjunto: el transformador de un solo corredor no resuelve esa tarea. La carga por sectores sigue siendo necesaria aunque el mapa se condense.

El catálogo oficial permite descargar geometría de construcciones. El visor 3D no equivale a un paquete completo de ciudad texturizada listo para un videojuego: la implementación examinada utiliza extrusión de polígonos. Nuestra prueba confirma que podemos reconstruir volumen a partir de datos; aún faltan superficies y detalles que se ven a nivel de calle. [Catastro](https://datosabiertos.bogota.gov.co/dataset/construccion), [visor 3D](https://mapas.bogota.gov.co/3d/).

## 5. Estaciones, vagones y paradas

Separar cinco conceptos: **estación**, **vagón o módulo**, **plataforma por sentido**, **punto físico de detención** y **parada de un servicio**. A/B puede identificar un vagón según la estación; no debe convertirse en una regla automática de articulado frente a biarticulado.

Cada módulo tendrá dimensiones, altura de plataforma, puertas, accesos, sentido atendido y referencias. Cada punto de detención almacenará orientación, posición longitudinal, separación al andén, compatibilidad de vehículo y puertas que deben alinearse. Las estaciones especiales requerirán modelos propios.

La capa descargada de estaciones incluye campos de longitud, ancho y número de vagones, además de otros atributos operativos. Hay valores que necesitan interpretación y algunos anchos nulos/cero; no bastan para generar automáticamente una estación exacta. En el explorador se muestran únicamente posiciones. [Conjunto oficial](https://datosabiertos.bogota.gov.co/dataset/estaciones-troncales-de-transmilenio1).

Primera mecánica: detectar aproximación, detenerse dentro de una tolerancia, permitir abrir las puertas del lado correcto, esperar un tiempo sencillo de intercambio y cerrar antes de salir. Pasajeros visibles y filas se añaden después de que la conducción y la parada funcionen.

Daniel probó la pista y pidió más margen de alineación. La práctica ya acepta separación al andén de 0,025 a 0,90 m y error longitudinal de hasta 1,20 m por puerta, verificando todas las puertas. Son parámetros de accesibilidad del ensayo, no una norma real de abordaje. Al construir estaciones verificadas pasarán a configuración por punto de parada. [Mandalay](ESTACION_MANDALAY.md) ya tiene una ficha de datos publicados y cotas pendientes; ya tiene una primera sección conducible con huellas oficiales y arquitectura vertical provisional. [Estado de Mandalay](MANDALAY_JUGABLE.md).

## 6. Rutas y operación

No necesitamos copiar manualmente toda la red. Diseñaremos un importador GTFS para rutas, viajes, paradas ordenadas, trazados y calendarios. Antes de usar un paquete se verificarán su fecha de servicio, archivos completos, identificadores, horas posteriores a medianoche y variantes por sentido. El paquete probado aún no se pudo descargar y su ficha antigua no garantiza vigencia. [Catálogo GTFS](https://datosabiertos.bogota.gov.co/en/dataset/especificacion-gtfs-general-transport-feed-specification-sitp).

La red física de carriles será independiente de las rutas comerciales. GTFS puede describir un itinerario, pero no sustituye la geometría de puertas, vagones, carriles de adelantamiento o maniobras de acceso. Los datos que falten se guardarán como anotaciones por estación, sin inventarlos.

Conservar longitudes y horarios reales como referencia. Navegación, frenado e IA usarán las distancias jugables; los tiempos objetivo de juego se calibrarán después de construir el recorrido y no se obtienen multiplicando todos los horarios por 0,5. Guardados y viajes incluirán la versión de disposición, para poder migrar cuando cambie la compresión.

El [buscador oficial de rutas](https://buscador-rutas.transmilenio.gov.co/rutas) aportado por Daniel se añade como referencia de consulta y contraste. No clasificar servicios solo con una expresión regular de letra y dos dígitos: distinguir troncales, servicios fáciles, duales y zonales mediante datos oficiales y vigencia. La enumeración actual de rutas fáciles está pendiente de verificar. No tratar toda ruta SITP como parte del alcance jugable.

Primero habrá conducción libre por el tramo; después un servicio de prueba entre las estaciones verificadas. Incorporar un servicio con nombre real exigirá comprobar su secuencia de paradas y vigencia. La IA de otros buses es parte del alcance final: seguirá carriles y servicios, hará paradas, operará puertas, mantendrá separación y formará colas. Primero se comprobará un NPC en un circuito, después varios buses y finalmente despachos reales sobre la red validada. La simulación lejana conservará estados de viaje para limitar el coste. Arquitectura, recuperación de bloqueos y aceptación: [IA_DE_BUSES.md](IA_DE_BUSES.md). Está planificada, no implementada todavía.

## 7. Vehículos y conducción

Modelo de datos por vehículo: carrocería, chasis, propulsión, largo/ancho/alto, ejes, distancia entre ejes, articulaciones, puertas por lado, altura de acceso, pintura y generación. Busscar/Marcopolo son fabricantes de carrocerías; Volvo/Scania/BYD pueden corresponder a chasis o tecnología. No combinar piezas por semejanza visual sin verificar la variante.

Propuesta de dos vehículos iniciales: un articulado troncal reconocible y uno de los nuevos articulados eléctricos duales, útiles para las conexiones en tráfico mixto que pidió Daniel. El biarticulado llegará al extender y validar el sistema de articulaciones. La variante concreta del primer modelo definitivo queda abierta; comenzar con una geometría de prueba permite evaluar el manejo antes de invertir en acabado.

Las físicas incluirán aceleración y frenado progresivos, resistencia al avance, dirección que se modera con la velocidad, marcha atrás, límites de articulación, detección de colisiones y un comportamiento estable sobre pendientes. Se comprobará el espacio que barre la cola al girar y al retroceder. Animar visualmente un fuelle sin que el remolque siga una trayectoria coherente no es suficiente.

Controles iniciales: teclado y ratón; después mando si se desea. Cámaras: conductor, seguimiento y exterior libre. Puertas izquierda/derecha cuando corresponda, interbloqueo de movimiento con puertas abiertas, luces, reversa y sonido básico. Suspensión compleja, daños, baterías exhaustivas y simulación de cada componente mecánico quedan fuera de la primera versión.

Se incorporó el comentario de Daniel sobre contacto con el andén: los roces laterales permiten deslizar sin un frenado artificial completo; los impactos frontales siguen bloqueando y toda posición aceptada se comprueba contra obstáculos. Las tres cámaras de conducción admiten orientación con ratón, zoom y centrado, con mirada lateral rápida en cabina. Son mejoras comprobadas en la pista plana; no equivalen aún a una física de suspensión o pendientes.

## 8. Bogotá actual y obras

La fecha objetivo inicial es **8 de septiembre de 2026**, con una ficha de vigencia por zona. Cuando no haya evidencia suficiente se indicará “pendiente de verificar”. No se afirmará que una captura antigua, un mapa catastral o una noticia prueban por sí solos el estado de un desvío ese día.

El nodo prioritario señalado por Daniel es Carrera 50–Américas–Calle 13–Calle 6. La noticia del 28 de agosto distingue una glorieta de tráfico mixto, un nivel exclusivo de TransMilenio y dos puentes superiores. Para recrear el momento de obra hacen falta los pasos provisionales, cierres y estructuras efectivamente construidas; los niveles proyectados no se habilitarán por adelantado. [Fuente aportada por Daniel](https://bogota.gov.co/mi-ciudad/movilidad/asi-van-obras-de-puentes-calle-13-con-avenida-las-americas-en-bogota).

La **Avenida 68 y el nodo 68–Américas** deben representar sus obras mientras continúen. La apertura futura del deprimido se incorporará como otra versión del escenario, únicamente después de comprobar habilitación y trazados. Mantener el escenario anterior recuperable; una actualización de obras no debe romper rutas ni partidas.

Separaremos la geometría duradera de la capa de obra: barreras, carriles habilitados, tramos cerrados, paradas temporales, estructuras en construcción y señalización. Cada cambio tendrá fecha de inicio, fecha final si se conoce y evidencia. Consultar PMT y comunicados de SDM/IDU/TransMilenio; referencias de calle aportadas por Daniel pueden ayudar a resolver detalles visuales.

## 9. Hitos y condiciones de aceptación

| Hito | Entregable | Se considera terminado cuando… |
|---|---|---|
| 0. Investigación y base | Este plan, fuentes, datos y explorador | Completado: datos descargados, escala comprobada y vistas general/cercana revisadas. |
| 1. Conducción de prueba | Bus articulado provisional sobre pista métrica | Implementada, probada por Daniel y ajustada con sus observaciones: roce lateral, cámara orientable y mayor tolerancia. 19 comprobaciones base, 12 de ajustes e integración aprobadas. Las pendientes pertenecen a la integración posterior. Ver PRUEBA_DE_CONDUCCION.md. |
| 1b. Disposición condensada | Transformación reversible y comparación 3D del eje piloto | Estudio de eje implementado y medido; protege intervalos y conserva IDs. La aceptación como mundo conducible depende de los niveles, accesos y maniobras del hito 2. |
| 2. Primer tramo | Calzadas transitables y una estación del piloto | **En curso:** Mandalay permite completar aproximación, alineación, apertura, cierre y salida en ambos sentidos. Faltan cotas verticales, accesos y validación del borde real; no declarar terminado el hito solo por superar las pruebas del prototipo. Ver MANDALAY_JUGABLE.md. |
| 3. Recorrido reconocible | Tres estaciones y edificios cercanos del recorte | Se conduce de extremo a extremo sin huecos de colisión ni bloqueos; los accesos y señales corresponden al tramo. Se introduce un NPC en ensayo sobre el pequeño grafo ya validado. |
| 4. Primer bus definitivo | Carrocería, cabina, materiales y audio | Dimensiones y disposición de puertas/ejes contrastadas con referencias de una variante; manejo aprobado por Daniel. |
| 5. Américas y obras | Extensión hacia el nodo Carrera 50 y Calle 13 | Obras y desvíos documentados; conexiones transitables; carga por sectores sin pausas graves. |
| 6. Red prioritaria | NQS, Calle 26, centro y Séptima; segundo bus | Continuidad entre corredores y operación dual comprobada en las zonas correspondientes. |
| 7. Operación de red | Selección de bus, servicio, sentido y fecha; pasajeros básicos, buses NPC y guardado | Jugador y NPC completan servicios verificados; colas e intersecciones sin solapes, estado persistente y simulación lejana coherente. No se atraviesan sectores pendientes. |
| 8. Sistema completo | Expansión por paquetes al resto de troncales, portales y conexiones | Inventario de cobertura y rutas comprobado por zona; mundo cargado por sectores, no simultáneamente. |
| 9. Calidad y posible distribución | Rendimiento, accesibilidad, instaladores y revisión de recursos | Recorridos estables; recursos con procedencia y permisos claros. Publicación sujeta a una decisión posterior del usuario. |

Trabajaremos por resultados comprobables, sin prometer que un corredor detallado cabe en una sesión. La mayor incertidumbre está en referencias actuales, puentes y estaciones especiales; dibujar volumen general a partir de datos es más automatizable. Primero medir tiempo y rendimiento del tramo, después estimar las expansiones con esa experiencia.

Daniel pidió evitar ciclos constantes de prueba manual y corrección puntual. Los cambios pequeños se integrarán y comprobarán internamente; las revisiones con él se concentrarán en hitos completos de conducción, entorno y operación.

## 10. Rendimiento, calidad y riesgos

Objetivo provisional: 1080p con al menos 30 FPS sostenidos en conducción y aspiración de 60 FPS. No es un resultado alcanzado: las cifras de una captura estática del explorador no son un benchmark del futuro juego. Medir tiempo de carga, memoria, mínimos de FPS y pausas al cambiar de sector.

Los riesgos principales son datos de épocas distintas, falta de detalle de estaciones, alturas estimadas, cruces a varios niveles, colisiones de buses largos y carga simultánea de demasiada ciudad. La condensación añade posibles conflictos entre nodos, pérdida de espacio de frenado o colas y desajustes de horarios. Las respuestas son fuentes fechadas, zonas protegidas, revisión de conexiones, pruebas de maniobra y carga por sectores. También se necesita separar las correcciones manuales de los modelos generados para no perderlas al importar datos nuevos.

## 11. Reparto de trabajo y continuidad

El asistente se encarga de investigación, herramientas, código, conversión de datos, modelado, pruebas y documentación. Daniel aporta criterio sobre la experiencia de conducción y el reconocimiento de lugares y buses. No necesita aprender Blender o descargar datos manualmente para empezar. Si aparece un permiso del sistema o un detalle que no pueda verificarse con fuentes disponibles, se pedirá únicamente lo necesario en ese momento.

Está autorizado repartir investigación delimitada, fichas y normalización a agentes ligeros, con contexto mínimo y revisión del principal. Física, arquitectura, modelado e integración central permanecen bajo responsabilidad del principal. La guía [TRABAJO_CON_AGENTES.md](TRABAJO_CON_AGENTES.md) define paquetes, límites de escritura y criterios de entrega. Ya se aplicó a la ficha de Mandalay; no se promete un ahorro porcentual de la cuota de cinco horas.

Al cerrar cada sesión: actualizar CONTINUAR.md con decisiones, resultado comprobado, problemas abiertos, archivos y próxima tarea; conservar una versión recuperable. Las referencias nuevas del usuario se incorporan al alcance existente. El trabajo continúa en sesiones activas; no se ha configurado ejecución automática ni publicación.

## 12. Diseño ampliado

Ver [SISTEMAS_Y_HOJA_DE_RUTA.md](SISTEMAS_Y_HOJA_DE_RUTA.md) para el ciclo de juego, dependencias y entregas. Ver [DIRECCION_VISUAL.md](DIRECCION_VISUAL.md) y [ESCALA_Y_COMPRESION.md](ESCALA_Y_COMPRESION.md) para el acabado y la nueva disposición. Estas decisiones incorporan las aclaraciones del 9 de septiembre: Bogotá condensada, fuente geográfica intacta, Bus Simulator para un solo jugador, otros buses con IA local y trabajo por hitos.
