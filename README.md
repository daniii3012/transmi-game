# Transmi · Bogotá en movimiento

Simulador 2D local de TransMilenio, sobre Bogotá a **escala geográfica 1:1**. Permite explorar servicios troncales y duales, seguir buses, consultar paradas, cambiar fecha y hora y ajustar oferta y demanda. La interfaz toma como referencia la claridad de Mini Metro y los paneles flotantes de Subway Builder. No incluye construcción de líneas ni GPS en vivo.

## Abrir y usar

Doble clic en **ABRIR_SIMULACION_2D.command**. Mantén abierta su Terminal y abre [el simulador local](http://127.0.0.1:8766/). No requiere instalar paquetes JavaScript ni descargar mapas al jugar. También puedes ejecutar `python3 tools/serve_network_2d.py --open` desde esta carpeta.

1. En **Red y rutas**, busca C15, H15, F63, una estación o un destino. Elegir una fila destaca el recorrido; «Simular solo este servicio» cambia la operación. La pestaña Ruta solo cambia la exploración; elegir otra fila tampoco reconstruye el escenario.
2. **Troncal** permite combinar letras y aplicar la selección. Incluye servicios que atienden estaciones de esas zonas o terminan en ellas. **Toda la red** restaura el conjunto disponible.
3. Usa el reloj para pausar, avanzar o retroceder 15 minutos, elegir fecha/hora, deslizar el día y acelerar a 1×, 8×, 32× o 120×. La velocidad del reloj no cambia los kilómetros ni los km/h de los buses.
4. Abre una parada para ver vagones, pasajeros esperando y próximas llegadas. Sigue un bus para consultar velocidad, capacidad y próxima parada. **Terminales** muestra regulación y disponibilidad de flota; **Operación** ajusta frecuencias, velocidades y pasajeros.
5. **Guardar** conserva fecha, hora, selección y parámetros en este navegador. Al volver a abrir se restaura pausado. No se guarda una partida en la nube.

Para abrir desde otros dispositivos del mismo Wi-Fi, usa **ABRIR_EN_RED_LOCAL.command** o `python3 tools/serve_network_2d.py --lan --open`. La Terminal muestra la dirección de este computador, con puerto 8767. Cada navegador ejecuta y guarda su propio escenario; mantén abierta la Terminal. No se publica en internet.

El botón **Ahora** usa fecha/hora de Bogotá. El botón de luna/sol cambia el tema y recuerda la preferencia. **Fuentes** y **Datos** enlazan la documentación y los 23 pendientes.

## Qué está implementado

- Recorridos oficiales proyectados en metros, paradas ordenadas, aceleración, frenado y menor velocidad en curvas y tramos de calle.
- Calendarios publicados, ventanas partidas, servicios nocturnos, fines de semana, festivos colombianos y control de vigencia.
- Cruceros iniciales de 60 km/h en troncal y 50 en calle, variación fija de ±5 por bus y tipos fijos por ruta.
- Despachos estimados pico/valle con variación de ±12% y refuerzos limitados por presión de demanda; carril de paso independiente y reservas locales de atención. Vagones y colas pequeñas en la operación de referencia.
- Pasajeros agregados: perfiles de entrada por estación/hora, abordaje, descenso, capacidad, espera y orientación matutina/vespertina estimada.
- Articulados de 160, biarticulados de 240, duales convencionales estimados de 80 y F63/Z63 eléctricos articulados de 160 publicados.
- Flota reutilizable en terminales, cálculo en un trabajador separado y agrupación visual al alejarse, conservando los buses del modelo.
- Plataformas, cubiertas y vías internas OSM para Portal Sur, Suba, Américas, Banderas, Ricaurte y Avenida Jiménez. Los demás andenes siguen siendo esquemáticos y estimados.
- Troncales coloreadas permanentemente y corredores de calle grises punteados; el recorrido exacto se destaca al seleccionar una ruta o bus.
- Colores publicados, calles/parques/agua de OpenStreetMap y marcas de puentes/túneles con etiquetas explícitas. Los cruces de líneas no crean giros o conexiones.

## Cobertura y límites

La descarga del mapa contiene **116 registros y 100 códigos distintos**, no 116 rutas únicas. El catálogo ampliado y depurado tiene **137 servicios/variantes: 114 utilizables y 23 pendientes**. En la fecha inicial, 112 variantes tienen ventanas de salida. F23 conserva únicamente el destino Portal Américas según la corrección de Daniel. C15 Chapinero Ciclovía está excluida por ser zonal; C15/H15 troncales tienen 19 paradas por sentido. F63/Z63 y los duales complementarios están incorporados.

El panel **Datos** explica cada pendiente. Algunos registros están vencidos; otros carecen de geometría o presentan calendarios ambiguos. El K86 completo no se sustituye por su ramal de aeropuerto. Los datos pendientes no se rellenan con líneas rectas.

La referencia ajustable 1× aplica un factor de 2,25 a las entradas del modelo anterior, solicitado por Daniel; es calibración de escenario, no un nuevo conteo oficial. La referencia histórica es el archivo oficial del **9 de septiembre de 2026**, con 1.920.298 validaciones; se enlazan 1.920.297 a 142 estaciones lógicas y se excluye una de cable. Se conserva únicamente el agregado. Frecuencias, reparto por sentido, destinos, tipos no publicados, asignación de vagón y patios son estimaciones explícitas. Las dimensiones solo siguen OSM en las seis estaciones detalladas. No hay una matriz real origen-destino ni tráfico mixto microscópico. Ver [modelo y fuentes](docs/OPERACION_Y_DATOS.md).

Three.js se mantiene para dibujar el mapa 2D con cámara ortográfica y muchos buses en pocos envíos a la GPU. La simulación funciona en módulos independientes; no depende de un motor de física 3D. El proyecto de conducción anterior permanece en `archive/transmi3d`, pausado.

## Desarrollo y continuidad

`app/dist/` contiene fuentes editables y dependencias vendorizadas; `tools/`, los importadores; `data/`, instantáneas, curación y auditorías. Pruebas: `node --test app/tests/*.test.mjs` y `python3 -m unittest discover -s tests` usando el Python geográfico indicado en [continuidad](CONTINUAR.md).

[Arquitectura](docs/ARQUITECTURA.md) · [Plan y pendientes](docs/PLAN_DEL_PROYECTO.md) · [Validación actual](docs/VALIDACION_20260911.md) · [Continuar](CONTINUAR.md)

Respaldo: [daniii3012/transmi-game](https://github.com/daniii3012/transmi-game). Uso local; no se ha desplegado una versión jugable pública.
