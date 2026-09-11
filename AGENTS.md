# Transmi 2D — dirección vigente

Leer README.md, CONTINUAR.md y docs/PLAN_DEL_PROYECTO.md. Trabajar en español. Mantener notas de continuidad y guardar hitos comprobados en GitHub; push autorizado a daniii3012/transmi-game. No desplegar ni publicar una versión jugable sin solicitud.

**Proyecto principal: simulación 2D de todas las rutas troncales y duales de TransMilenio.** Incluye paradas en calle de Carrera Séptima, 68/P85/M85 y obras actuales cuando existan datos vigentes. Daniel confirmó que las zonales quedan para después. La conducción 3D está pausada hasta nuevo aviso en archive/transmi3d; no continuar modelado o física por inercia.

Geografía real de Bogotá en metros, proyección y origen explícitos, sin compresión ni disposición esquemática. El mapa debe conservar formas y recorridos, incluyendo enlaces por puentes/deprimidos/retornos; un cruce de líneas no implica conexión. Fuente, fecha, IDs y grado de verificación por dato. No inventar geometría entre estaciones ni afirmar actual una descarga sin vigencia.

Simulación para un jugador, reloj virtual 1× y acelerado, calendario de servicio, avance/retroceso temporal reproducible, oferta pico/valle, selección de una ruta, una o varias zonas por letra, o toda la red. No son posiciones GPS en vivo. Horarios publicados y frecuencias estimadas deben distinguirse. Tipos estables por vehículo: F63/Z63 dual articulado eléctrico de 160 publicado; padrón dual 80 y mezcla 160/240/250 estimados donde no se conoce asignación. Daniel autorizó dos carriles por sentido como abstracción (atención + paso), cantidad de vagones publicada si existe y asignación estimada visible. Frecuencias y demanda ajustables autorizadas. QA integral de navegador autorizado explícitamente; no volver a pedir permiso.

Aplicación principal: app/dist (fuentes estáticas editables), app/tests. Herramientas de datos: tools. Datos: data. Documentación activa: docs. web/transmi2d es solo enlace de compatibilidad con la primera prueba. Aplicar la guía Sites a la aplicación web; mantener el proyecto local. Conservar dependencias vendorizadas y sus licencias.

Daniel autorizó agentes ligeros gpt-5.6-luna para investigación/normalización acotada, contexto mínimo y archivos propios. Principal: arquitectura, integración, simulación y revisión. No prometer porcentajes de ahorro de cuota ni crear automatizaciones. Mantener revisiones por hitos y evitar pedir pruebas manuales después de cada ajuste.
