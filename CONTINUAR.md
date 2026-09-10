# Continuidad — Transmi 2D

Actualizado el 10 de septiembre de 2026. Leer README.md y docs/PLAN_DEL_PROYECTO.md. Las nuevas decisiones de Daniel sustituyen la dirección previa de conducción 3D.

## Decisiones vigentes

- **Principal: simulación 2D de todas las rutas troncales y duales**, con geografía real de Bogotá 1:1. Incluye calle/paraderos de Séptima y 68, P85/M85, obras actuales según fuentes. Confirmó **zonales para después**.
- **3D pausado hasta nuevo aviso**, conservado en archive/transmi3d. No continuar modelado/Blender/Godot por inercia. Último estado antes del cambio: e18c8d6ba7c6a3568f61c3c9bdbdaea9a2d1a99a.
- Elegir una ruta, varias zonas por letras o toda la red; calendario, días, pico/valle, reloj 1×/acelerado y saltos adelante/atrás. Un solo jugador; sin GPS en vivo ni construcción de red.
- Última aclaración: evitar atascos artificiales. Adoptado **modelo híbrido fluido**: metros y velocidades coherentes, despacho por oferta estimada/verificada, paso independiente de paradas y conflictos locales solo con datos suficientes. No reducir distancias ni introducir miles de buses por un contador fijo como operación real.
- Buses homogéneos hasta verificar tipo por ruta. No inventar asignaciones a vagones. Horarios oficiales separados de frecuencias/velocidades/atención estimadas.
- Visual: Subway Builder + claridad de Mini Metro; geografía exacta, contexto urbano tenue por zoom. La referencia Wikimedia tiene última actualización del archivo en 2019, no sirve para vigencia 2026.
- Push a daniii3012/transmi-game autorizado. No desplegar. Agentes ligeros permitidos para investigación acotada; el principal integra. Revisiones por hitos, no microensayos constantes con Daniel.

## Estructura y ejecución

Raíz: `/Users/daniel/Documents/Codex/2026-09-08/ho/outputs/BogotaTransmi`.

- `app/dist`: fuente estática editable de la aplicación 2D; `app/tests`: pruebas Node. Three.js 0.186.0 vendorizado con licencia/hash.
- `web/transmi2d` es enlace de compatibilidad a `../app`; conserva el antiguo servidor si Daniel lo abrió.
- `tools`: importadores y servidor; `data/raw`: fuentes inmutables; `data/processed`: auditorías; `data/vehicles`: ficha provisional compartida; `docs`: documentación activa.
- `archive/transmi3d`: recursos, generadores, pruebas y documentos históricos 3D. Datos raw y research compartidos mediante enlaces relativos. Lanzadores Godot ajustados a la ubicación nueva. **14 pruebas Python del archivo pasan tras moverlo**.
- Abrir `ABRIR_SIMULACION_2D.command`: servidor solo local 127.0.0.1:8766. No detener servidores o terminales iniciados por Daniel.
- Python geográfico: `../../work/venv/bin/python`. Node: /opt/homebrew/bin/node v26.4.0. Godot/Blender quedan instalados, sin nuevo desarrollo.

## Datos nuevos comprobados

`tools/fetch_services.py` produjo `data/raw/services/20260910T185326Z/` y `latest.json`:

- POST oficial `/api/v1/rutas/troncales` devuelve **116 objetos, 100 códigos distintos**.
- Consulta del catálogo amplio y selección de **132 registros**: 116 del mapa más 16 candidatos complementarios de familias duales. Se obtuvieron **132 detalles, sin fallos de descarga**.
- **113 con LineString, 19 sin trazado**. Algunas versiones antiguas del mapa no tienen paradas ni geometría. No ofrecerlas como simuladas.
- `rutaDetalle`: color, nombre, estaciones ordenadas (id/código/nombre/dirección/posicion/sistema/color), horario por tipo de día y trazado geográfico. No trae frecuencia, tipo bus ni servicio→vagón.
- Calendarios observados L-S, L-V, D-F, S, L-D. Fechas metadata vigentes hasta días distintos (incluye entradas ya vencidas); preservar sin convertir medianoche UTC al día anterior por accidente. Variantes Ciclovía requieren resolución específica para no duplicarlas.
- M85/P85 tienen tramos/paradas de calle y geometrías publicadas. Ciertos trazados contienen ambos sentidos en una sola polilínea; primer `posicion` de M85 ronda 9,6 km. No recorrer todo el trazado bruto antes de su primera parada. K86/629 tiene una geometría claramente incompatible con su cadena; bloquear hasta corregir.
- `posicion` aproxima distancia métrica, pero no equivale a coordenada exacta. En ruta690 se contrastó con estaciones fuente: diferencias de decenas de metros y extremo Avenida Jiménez problemático. Evitar interpolación presentada como medición.
- API `/arcgis/estaciones`: 157 puntos con coordenadas, zona, color, estado y número de vagones (incluye cable fuera del alcance). `/arcgis/trazados_troncal`: 25 registros, incluye tres de cable. Son fuentes aparte de las capas CC BY previas; licencia de estos endpoints no establecida.
- API de planos: un agente reportó 156 marcadores con porcentajes sobre imagen y colores. Reconsulta principal dio 403; **no se verificó íntegramente esa respuesta**. No son coordenadas geográficas ni asignaciones ruta-vagón.

Sondeos auxiliares en data/research/routes_detail_probe_20260910 y station_api_probe_20260910. Las fechas/horas y hashes declarados en sondeos no sustituyen la instantánea principal con respuestas conservadas. Un agente se quedó sin cuota durante el seguimiento; no queda trabajando.

## Estado de implementación al reorganizar

El laboratorio anterior funciona tras el traslado: piloto de paradas 8/24/64 buses y carga de100/1.000/3.000 sobre componentes aislados. **3 pruebas Python activas y 7 Node pasan**. El benchmark anterior de núcleo (0,084 ms/paso con3.000) no es FPS ni operación real. El juego 3D tenía las pruebas y capturas descritas en archive/transmi3d/HISTORICO_CONTINUAR.md.

Los servicios publicados se descargaron; integrar ahora el catálogo, auditoría geométrica, calendario y operación híbrida. La vista actual todavía conserva los ensayos hasta que se complete ese hito. No afirmar cobertura de todas las rutas ni validación visual de navegador. La guía Sites permite QA de navegador solo cuando se pide explícitamente; Daniel ha revisado el prototipo por su cuenta.

## Siguiente trabajo concreto

1. Normalizar los132 detalles: fuentes, código/ID/variante, calendario, fechas, geometría recortada al sentido, paradas y anomalías. Mantener19 sin geometría como pendientes. No rellenar con líneas rectas.
2. Geolocalizar paradas duales: fuente oficial por ID/código; investigar catálogo de Paraderos Zonales del SITP solo para paraderos utilizados por duales. No ampliar alcance a buses zonales.
3. Implementar perfiles de viaje métricos y despachos estimados por pico/valle, calendario, selección y reconstrucción temporal. Congestión física entre servicios pendiente; modo fluido explícito.
4. Vincular capas de contexto cartográfico y actualizar interfaz con colores oficiales y lista de servicios disponible/pending.
5. Verificar puntos/vagones y conexiones con topología compartida donde sea necesario; medir dibujo/rendimiento sin inventar datos.

No reiniciar investigación ni volver a instalar herramientas. Guardar un checkpoint tras la reorganización y otro tras la próxima integración; verificar HEAD remoto. No se creó automatización, goal ni tarea separada.
