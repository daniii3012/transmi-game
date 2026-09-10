# Bogotá cozy y condensada

Dirección acordada con Daniel · 9 de septiembre de 2026. Un Bus Simulator de Bogotá para un solo jugador, con toda la red BRT como meta, una geografía fuente conservada 1:1 y una apariencia cálida, suave y con volumen. El mundo jugable podrá condensar selectivamente tramos repetitivos; la escala y la operación siguen siendo prioritarias. Ver [escala y compresión](ESCALA_Y_COMPRESION.md).

## Lectura de las referencias

| Referencia | Qué se pudo revisar | Qué aporta al proyecto |
|---|---|---|
| [over the hill — galería oficial](https://store.steampowered.com/app/2929250/over_the_hill/) | Galería observada: vehículo rojo de silueta clara, pradera dorada, construcciones sencillas y montañas con menor contraste a distancia. | Separar bien vehículo y paisaje, usar masas de color coherentes y dar profundidad con luz y atmósfera. Bogotá conservará sus propios materiales, vegetación y clima. |
| [Maqueta ferroviaria de Nick](https://x.com/nickfromlater/status/2097355845524726084), [experiencia enlazada](https://alder-valley-rail-atelier.nickfromlater.chatgpt.site/) | Experiencia abierta e inspeccionada visualmente: paisaje ferroviario sobre una mesa, luz cálida, cubiertas diferenciadas, viaducto, vegetación en grupos y colores crema, oliva y tierra. | Sensación de objetos cuidados, espesor visible y detalle selectivo. Tomaremos esa cualidad de maqueta en materiales y siluetas, conservando cámara de conducción y metros reales. |
| [Proyecto de Givros](https://x.com/givros/status/2097343467026289039) | Se leyó la descripción pública de un lago con cabañas, vegetación de orilla, embarcación y pequeños elementos de vida. X pidió iniciar sesión al abrir el vídeo; no se verificaron su animación, iluminación ni acabado completos. | La descripción sugiere agrupar detalles alrededor de lugares con identidad. Su traducción a Bogotá es una decisión nuestra: estación, acceso, comercio próximo y vegetación como conjuntos reconocibles. Su evaluación visual completa sigue pendiente. |

La dirección siguiente es una propuesta propia basada en lo observado y en las preferencias de Daniel. ETS y Bus Simulator continúan como referencias de recorrido y operación; los tres proyectos anteriores orientan el estilo visual.

## Escala física y sensación del mundo

**Una unidad del motor seguirá siendo un metro jugable.** La geografía fuente mantiene sus posiciones y metadatos 1:1. En el mundo jugable, la separación entre estaciones y la longitud de un tramo podrán diferir solo cuando el estudio de [escala y compresión](ESCALA_Y_COMPRESION.md) lo clasifique como elegible y lo mida después de ensamblarlo. Anchura de carriles, radios de giro, tamaño de edificios, plataformas y proporciones de los buses mantienen medidas coherentes; estaciones, cruces, rampas, obras y conexiones quedan protegidos.

La sensación más íntima se buscará reduciendo ruido visual, agrupando elementos, suavizando siluetas y haciendo legibles los lugares cercanos. El fondo urbano tendrá menos contraste y detalle. No se escalarán edificios o estaciones arbitrariamente. La condensación selectiva no debe ocultar la distancia necesaria para leer señales, frenar, elegir carril o reconocer una conexión.

El mundo se cargará por sectores alrededor del bus. Esto permite conservar la cobertura de la red sin mantener cada edificio y cada vehículo simultáneamente en memoria. Los presupuestos definitivos dependerán de mediciones en conducción.

## Gramática visual de Bogotá

**Geometría.** Volúmenes simples con espesor, pequeñas cornisas, marcos, zócalos y cubiertas diferenciadas. Bordes ligeramente suavizados donde reciban luz; evitar polígonos que no aporten a la vista desde la cabina. Las huellas reales organizan el barrio y las referencias locales determinan las piezas particulares. Las estimaciones de altura se mantienen identificadas.

**Materiales.** Predominio mate y rugosidad moderada. Ladrillo, concreto y asfalto tendrán variación sutil a escala física, suficiente para percibir superficie sin ruido intenso durante el movimiento. Reutilizar materiales y texturas repetibles con pequeñas variaciones por edificio. Ventanas con profundidad y brillo contenido; los metales mantienen una respuesta distinta del concreto. Desgaste selectivo, sin cubrir cada objeto de suciedad.

**Paleta de trabajo.** Estos colores son puntos de partida propios, no mediciones de pintura oficial:

| Función | Colores base | Uso |
|---|---|---|
| Identidad de buses y estación | Rojo `#B53D38`, amarillo `#E2BE70` | Acentos reconocibles; conservar libreas y codificación de cada variante documentada. |
| Entorno construido | Terracota `#B78C70`, arena `#C6B296`, concreto `#A8AFA0` | Fachadas y volúmenes de fondo con variación contenida. |
| Vegetación | Salvia `#7C956B`, oliva `#8D9F76`, verde gris `#718568` | Copas en grupos, alturas y siluetas variadas según el lugar. |
| Cielo y elementos fríos | Azul gris `#9CBAC1`, ventanas `#577075` | Contraste suave frente al ladrillo y el bus. |
| Interfaz | Fondo verde oscuro, texto crema, acento amarillo | Lectura clara de velocidad, marcha, ruta y puertas. |

**Luz.** Empezar con una escena diurna estable: cielo suave, sombras legibles y calidez moderada. La identidad de Bogotá también debe funcionar bajo luz nublada; no depender de un atardecer anaranjado permanente. La atmósfera distante puede aportar profundidad, sin velar el andén ni las señales. Desenfoque y efectos intensos no serán requisitos para alcanzar el estilo.

**Vegetación y vida.** Copas orgánicas formadas por pocos grupos, variaciones discretas y vegetación ubicada en separadores o zonas observadas. Postes, cerramientos, accesos y comercio cercano dan ritmo al recorrido. Los buses NPC haciendo paradas y formando colas aportarán vida ligada al sistema de transporte. Su lógica local se desarrolla por etapas en [IA_DE_BUSES.md](IA_DE_BUSES.md).

## Dónde invertir el detalle

| Zona | Tratamiento |
|---|---|
| Cabina, bus, plataforma y carril inmediato | Proporciones cuidadas, puertas y fuelle animados, borde de plataforma visible, marcas legibles, materiales con relieve y cámara orientable. |
| Primera línea de edificios | Huellas reales, cubiertas y fachadas modulares, ventanas con profundidad y algunos elementos particulares contrastados. |
| Fondo urbano y cerros | Volúmenes agrupados, menos detalle, siluetas reconocibles y contraste atmosférico. |

Simplificar detalle visual no elimina niveles, colisiones, carriles, accesos o restricciones operativas. Tampoco transforma un tramo en obra en infraestructura terminada. Esos elementos siguen el escenario fechado.

## Aplicación y aceptación

La pista ficticia ya recibió una primera aplicación: pintura del bus menos brillante, colores del entorno más contenidos, copas agrupadas, variación suave del suelo y una interfaz en verde oscuro y crema. Las [capturas de práctica](preview_practica.png) documentan esa prueba; **aún no representan el acabado urbano objetivo**. El explorador de Américas conserva sus edificios de altura estimada y estaciones como marcadores.

El próximo hito visual será una sección métrica de Mandalay con plataforma, carriles y primera línea de contexto. Se revisará como conjunto desde cabina y exterior, después de resolver las medidas necesarias. Para aceptarlo:

1. La estación, el bus y los carriles conservan escala y permiten la maniobra.
2. Se distinguen borde de andén, señalización y puertas sin depender de una cámara fija.
3. Materiales, cubiertas y sombras dan profundidad durante el movimiento.
4. La escena comparte paleta y tratamiento, y mantiene rasgos reconocibles del sitio.
5. Se mide rendimiento en el M3 Pro, con objetivo provisional de 30 FPS sostenidos a 1080p y aspiración de 60; sin prometer aún una densidad de ciudad o tráfico.

Daniel pidió avanzar por hitos coherentes. Las correcciones puntuales se integran y comprueban internamente; las revisiones de usuario se concentran en recorridos y conjuntos completos.

## Procedencia

Modelos, materiales y código propios se conservan editables. Las referencias externas sirven para estudiar composición y acabado; no se incorporan sus recursos al juego. Fotografías y datos de Bogotá llevarán fuente, fecha, interpretación y licencia por separado. El cambio de estilo mantiene ese registro y la posibilidad de una publicación futura.
