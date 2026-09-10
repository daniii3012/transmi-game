# Continuidad del proyecto

Leer README.md, CONTINUAR.md y docs/PLAN_DEL_PROYECTO.md antes de modificar el proyecto. Mantener CONTINUAR.md al día al cerrar una sesión. Las decisiones explícitas del usuario prevalecen sobre propuestas del plan.

Trabajar en español. Proyecto personal con publicación futura posible. Está autorizado guardar los avances en https://github.com/daniii3012/transmi-game; no desplegar ni publicar una versión jugable sin que se solicite. Priorizar escala y operación de Bus Simulator; la meta final es todo el sistema BRT. No confundir el explorador geográfico existente con un simulador terminado. Preservar los datos originales fechados y sus metadatos; separar mediciones, estimaciones y elementos pendientes de verificar.

Usar metros y conservar un origen geográfico explícito. La ciudad objetivo incluye obras actuales, con fechas de vigencia. No interpretar CONELEVACI como metros ni extruir a partir de capturas del visor. Validar los giros, niveles y envolventes de articulación antes de ampliar el mapa.

Dirección vigente: Bogotá cozy y condensada, conservando toda la red como meta. Daniel autorizó continuar con compresión selectiva después de reconsiderar el 1:1 global. Datos geográficos fuente intactos a escala real; una unidad del motor = un metro jugable. Se pueden acortar tramos intermedios, manteniendo medidas coherentes de vehículos, plataformas, carriles y maniobras. Factor 0,5 solo como ensayo en intervalos elegibles, no regla global. Consultar docs/ESCALA_Y_COMPRESION.md y docs/DIRECCION_VISUAL.md. No transformar todas las mallas catastrales ni resolver cada arista de una red por separado: las conexiones requieren una disposición común verificada.

Juego exclusivamente para un jugador, con buses NPC que harán rutas mediante IA local. La IA está planificada, no implementada. Mantener el trabajo independiente de servicios de red durante la ejecución normal del juego.

Daniel autorizó delegar tareas acotadas a agentes ligeros para aprovechar la sesión. Usar gpt-5.6-luna para fichas de fuentes y normalización delimitada, con contexto mínimo y archivos propios; revisar sus resultados antes de integrarlos. Física, arquitectura e integración quedan a cargo del agente principal. Ver docs/TRABAJO_CON_AGENTES.md. No prometer ahorros concretos de cuota ni crear automatizaciones implícitas.

Integrar y comprobar internamente correcciones puntuales; Daniel pidió revisiones por hitos coherentes, evitando ciclos continuos de pequeñas pruebas manuales.
