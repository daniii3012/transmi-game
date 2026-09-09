# Plan de desarrollo de Bogotá Transmi

Versión 0.1 · 8 de septiembre de 2026 · Proyecto personal de Daniel.

## 1. Experiencia que construiremos

Un simulador arcade en primera y tercera persona donde sea agradable conducir buses reconocibles de TransMilenio por corredores reales de Bogotá. Distancias, anchos y tamaño de los vehículos deben conservar escala métrica. La apariencia deberá hacer reconocible la ciudad desde la cabina: disposición de vías, estaciones, separadores, puentes, fachadas cercanas, señalización y cerros cuando corresponda.

La fidelidad geométrica y el acabado visual son objetivos diferentes. Mantendremos las distancias reales sin exigir que cada fachada o negocio de toda Bogotá se modele individualmente. Los edificios cercanos al recorrido reciben más atención; los del fondo pueden generarse con reglas y niveles de detalle.

El usuario no quiere publicar el proyecto. La primera plataforma será su Mac; el diseño conservará la posibilidad de exportar a Windows más adelante. La experiencia inicial será para una persona, sin conexión permanente. No incluimos de inicio multijugador, economía de operadores, interior de toda la ciudad, simulación mecánica exhaustiva ni todos los servicios del SITP.

## 2. Alcance geográfico acordado

| Orden de expansión propuesto | Zona | Propósito y dificultad |
|---|---|---|
| Prueba actual | Américas: Marsella–Av. Boyacá–Mandalay | Validar datos y escala en un recorte. Unos 1,24 km entre centros extremos en línea recta; medir el recorrido de carriles por separado. |
| Primera zona jugable | El mismo tramo, con una estación detallada y después las tres | Conducir, frenar, aproximarse al andén, abrir puertas y continuar. Revisar el cruce a desnivel de Boyacá antes de habilitarlo. |
| Expansión 1 | Américas hacia Pradera, Distrito Grafiti y Puente Aranda; después Banderas y Portal Américas | Conectar la base con el nodo de obras señalado por Daniel y ampliar el recorrido. |
| Expansión 2 | Calle 13 existente hacia el centro | Incorporar el nodo Carrera 50, Ricaurte y conexiones urbanas con una versión fechada de las obras. |
| Expansión 3 | NQS / Carrera 30 y Calle 26 | Conectar corredores; aumenta el trabajo de puentes, rampas, intersecciones y estaciones especiales. |
| Expansión 4 | Centro y Carrera Séptima | Añadir operación dual, accesos particulares y circulación en tráfico mixto. |

Es una secuencia de construcción, no una reducción del alcance pedido. La selección del recorte inicial es técnica y reversible. La extensión final de cada corredor y las conexiones exactas se fijarán cuando recorramos los datos y el primer tramo jugable. La Nueva Calle 13 en construcción no debe aparecer completa ni operativa por asumir que forma parte de la red futura.

## 3. Herramientas y decisión inicial

| Herramienta | Uso | Decisión |
|---|---|---|
| Godot 4.7.2 | Juego, cámara, vehículos, interacción, carga de sectores y exportación | Base inicial instalada de forma local. Su proyecto de texto y ejecución por comandos facilitan mantenerlo y comprobarlo. |
| Blender para Apple Silicon | Modelado de buses, cabinas, estaciones, puentes y materiales; exportación glTF/GLB | Instalar en la fase de modelado. |
| Python + pyproj + Shapely + Earcut | Descargar, recortar, reproyectar y triangular datos | Entorno ya preparado; versiones fijadas. |
| QGIS | Inspección visual de datos, medidas y edición geográfica manual cuando aporte valor | Opcional; la descarga y conversión actuales no dependen de instalarlo. |
| Git local | Versionar código, decisiones y progreso | Guardar puntos de avance; los datos grandes requerirán una política separada al crecer. |

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

El catálogo oficial permite descargar geometría de construcciones. El visor 3D no equivale a un paquete completo de ciudad texturizada listo para un videojuego: la implementación examinada utiliza extrusión de polígonos. Nuestra prueba confirma que podemos reconstruir volumen a partir de datos; aún faltan superficies y detalles que se ven a nivel de calle. [Catastro](https://datosabiertos.bogota.gov.co/dataset/construccion), [visor 3D](https://mapas.bogota.gov.co/3d/).

## 5. Estaciones, vagones y paradas

Separar cinco conceptos: **estación**, **vagón o módulo**, **plataforma por sentido**, **punto físico de detención** y **parada de un servicio**. A/B puede identificar un vagón según la estación; no debe convertirse en una regla automática de articulado frente a biarticulado.

Cada módulo tendrá dimensiones, altura de plataforma, puertas, accesos, sentido atendido y referencias. Cada punto de detención almacenará orientación, posición longitudinal, separación al andén, compatibilidad de vehículo y puertas que deben alinearse. Las estaciones especiales requerirán modelos propios.

La capa descargada de estaciones incluye campos de longitud, ancho y número de vagones, además de otros atributos operativos. Hay valores que necesitan interpretación y algunos anchos nulos/cero; no bastan para generar automáticamente una estación exacta. En el explorador se muestran únicamente posiciones. [Conjunto oficial](https://datosabiertos.bogota.gov.co/dataset/estaciones-troncales-de-transmilenio1).

Primera mecánica: detectar aproximación, detenerse dentro de una tolerancia, permitir abrir las puertas del lado correcto, esperar un tiempo sencillo de intercambio y cerrar antes de salir. Pasajeros visibles y filas se añaden después de que la conducción y la parada funcionen.

## 6. Rutas y operación

No necesitamos copiar manualmente toda la red. Diseñaremos un importador GTFS para rutas, viajes, paradas ordenadas, trazados y calendarios. Antes de usar un paquete se verificarán su fecha de servicio, archivos completos, identificadores, horas posteriores a medianoche y variantes por sentido. El paquete probado aún no se pudo descargar y su ficha antigua no garantiza vigencia. [Catálogo GTFS](https://datosabiertos.bogota.gov.co/en/dataset/especificacion-gtfs-general-transport-feed-specification-sitp).

La red física de carriles será independiente de las rutas comerciales. GTFS puede describir un itinerario, pero no sustituye la geometría de puertas, vagones, carriles de adelantamiento o maniobras de acceso. Los datos que falten se guardarán como anotaciones por estación, sin inventarlos.

Primero habrá conducción libre por el tramo; después un servicio de prueba entre las estaciones verificadas. Incorporar un servicio con nombre real exigirá comprobar su secuencia de paradas y vigencia. Los horarios estrictos, despachos y tráfico de buses son ampliaciones posteriores.

## 7. Vehículos y conducción

Modelo de datos por vehículo: carrocería, chasis, propulsión, largo/ancho/alto, ejes, distancia entre ejes, articulaciones, puertas por lado, altura de acceso, pintura y generación. Busscar/Marcopolo son fabricantes de carrocerías; Volvo/Scania/BYD pueden corresponder a chasis o tecnología. No combinar piezas por semejanza visual sin verificar la variante.

Propuesta de dos vehículos iniciales: un articulado troncal reconocible y uno de los nuevos articulados eléctricos duales, útiles para las conexiones en tráfico mixto que pidió Daniel. El biarticulado llegará al extender y validar el sistema de articulaciones. La variante concreta del primer modelo definitivo queda abierta; comenzar con una geometría de prueba permite evaluar el manejo antes de invertir en acabado.

Las físicas incluirán aceleración y frenado progresivos, resistencia al avance, dirección que se modera con la velocidad, marcha atrás, límites de articulación, detección de colisiones y un comportamiento estable sobre pendientes. Se comprobará el espacio que barre la cola al girar y al retroceder. Animar visualmente un fuelle sin que el remolque siga una trayectoria coherente no es suficiente.

Controles iniciales: teclado y ratón; después mando si se desea. Cámaras: conductor, seguimiento y exterior libre. Puertas izquierda/derecha cuando corresponda, interbloqueo de movimiento con puertas abiertas, luces, reversa y sonido básico. Suspensión compleja, daños, baterías exhaustivas y simulación de cada componente mecánico quedan fuera de la primera versión.

## 8. Bogotá actual y obras

La fecha objetivo inicial es **8 de septiembre de 2026**, con una ficha de vigencia por zona. Cuando no haya evidencia suficiente se indicará “pendiente de verificar”. No se afirmará que una captura antigua, un mapa catastral o una noticia prueban por sí solos el estado de un desvío ese día.

El nodo prioritario señalado por Daniel es Carrera 50–Américas–Calle 13–Calle 6. La noticia del 28 de agosto distingue una glorieta de tráfico mixto, un nivel exclusivo de TransMilenio y dos puentes superiores. Para recrear el momento de obra hacen falta los pasos provisionales, cierres y estructuras efectivamente construidas; los niveles proyectados no se habilitarán por adelantado. [Fuente aportada por Daniel](https://bogota.gov.co/mi-ciudad/movilidad/asi-van-obras-de-puentes-calle-13-con-avenida-las-americas-en-bogota).

Separaremos la geometría duradera de la capa de obra: barreras, carriles habilitados, tramos cerrados, paradas temporales, estructuras en construcción y señalización. Cada cambio tendrá fecha de inicio, fecha final si se conoce y evidencia. Consultar PMT y comunicados de SDM/IDU/TransMilenio; referencias de calle aportadas por Daniel pueden ayudar a resolver detalles visuales.

## 9. Hitos y condiciones de aceptación

| Hito | Entregable | Se considera terminado cuando… |
|---|---|---|
| 0. Investigación y base | Este plan, fuentes, datos y explorador | Datos descargados, escala comprobada y vista revisada. La última corrección visual aún debe verificarse. |
| 1. Conducción de prueba | Bus articulado provisional sobre pista métrica | Acelera, frena, gira y retrocede de forma estable; cámaras y puertas funcionan; remolque no atraviesa barreras. |
| 2. Primer tramo | Calzadas transitables y una estación del piloto | Se puede completar aproximación, alineación, apertura, cierre y salida en ambos sentidos; niveles y anchos están verificados. |
| 3. Recorrido reconocible | Tres estaciones y edificios cercanos del recorte | Se conduce de extremo a extremo sin huecos de colisión ni bloqueos; los accesos y señales corresponden al tramo. |
| 4. Primer bus definitivo | Carrocería, cabina, materiales y audio | Dimensiones y disposición de puertas/ejes contrastadas con referencias de una variante; manejo aprobado por Daniel. |
| 5. Américas y obras | Extensión hacia el nodo Carrera 50 y Calle 13 | Obras y desvíos documentados; conexiones transitables; carga por sectores sin pausas graves. |
| 6. Red prioritaria | NQS, Calle 26, centro y Séptima; segundo bus | Continuidad entre corredores y operación dual comprobada en las zonas correspondientes. |
| 7. Pulido personal | Tráfico ligero, audio, pasajeros y opciones | El recorrido es agradable y estable en el equipo objetivo. |

Trabajaremos por resultados comprobables, sin prometer que un corredor detallado cabe en una sesión. La mayor incertidumbre está en referencias actuales, puentes y estaciones especiales; dibujar volumen general a partir de datos es más automatizable. Primero medir tiempo y rendimiento del tramo, después estimar las expansiones con esa experiencia.

## 10. Rendimiento, calidad y riesgos

Objetivo provisional: 1080p con al menos 30 FPS sostenidos en conducción y aspiración de 60 FPS. No es un resultado alcanzado: las cifras de una captura estática del explorador no son un benchmark del futuro juego. Medir tiempo de carga, memoria, mínimos de FPS y pausas al cambiar de sector.

Los riesgos principales son datos de épocas distintas, falta de detalle de estaciones, alturas estimadas, cruces a varios niveles, colisiones de buses largos y carga simultánea de demasiada ciudad. Las respuestas son fechas por capa, referencias por objeto, validación geométrica, pruebas de maniobra y carga por sectores. También se necesita separar las correcciones manuales de los modelos generados para no perderlas al importar datos nuevos.

## 11. Reparto de trabajo y continuidad

El asistente se encarga de investigación, herramientas, código, conversión de datos, modelado, pruebas y documentación. Daniel aporta criterio sobre la experiencia de conducción y el reconocimiento de lugares y buses. No necesita aprender Blender o descargar datos manualmente para empezar. Si aparece un permiso del sistema o un detalle que no pueda verificarse con fuentes disponibles, se pedirá únicamente lo necesario en ese momento.

Al cerrar cada sesión: actualizar CONTINUAR.md con decisiones, resultado comprobado, problemas abiertos, archivos y próxima tarea; conservar una versión recuperable. Las referencias nuevas del usuario se incorporan al alcance existente. El trabajo continúa en sesiones activas; no se ha configurado ejecución automática ni publicación.
