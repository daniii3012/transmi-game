# Transmi 2D

Simulación para un jugador de **todas las rutas troncales y duales de TransMilenio**, sobre la geografía real de Bogotá a escala 1:1. Incluye como alcance las paradas de calle de Carrera Séptima y Avenida 68. Las rutas zonales del SITP quedan para una etapa posterior.

**El simulador 3D está en pausa hasta nuevo aviso**, conservado en [archive/transmi3d](archive/transmi3d/README.md). La nueva dirección se confirmó el 10 de septiembre de 2026. No se comprimen distancias en el proyecto 2D.

## Abrir

Doble clic en **ABRIR_SIMULACION_2D.command**. Funciona localmente; mantener abierta su Terminal. La aplicación vive en `app/dist/`. El enlace `web/transmi2d` conserva compatibilidad con la primera prueba.

Ya existe el laboratorio geográfico con paradas, reloj acelerado y flota de ensayo. La nueva línea incorpora servicios publicados, calendario y selección por ruta/zona. Ver [estado y continuidad](CONTINUAR.md) para distinguir lo implementado de lo pendiente.

## Dirección de la simulación

Distancias reales, tiempo virtual a ritmo real o acelerado y avance/retroceso reproducible. Enfoque híbrido: movimiento y atención de paradas, con circulación simplificada para evitar atascos artificiales. Los buses que no paran deben poder pasar. La flota se derivará de despachos y frecuencias; frecuencias, velocidades y asignaciones de vagón estimadas se mostrarán como tales.

La referencia visual principal es Subway Builder, con la claridad de Mini Metro: ciudad reconocible, mapa ligero, líneas y símbolos legibles, sin transformar Bogotá en un diagrama esquemático. No se construye ni rediseña la red; se observa y configura qué parte se simula.

## Estructura

| Carpeta | Contenido |
|---|---|
| `app/` | Aplicación 2D principal y pruebas JavaScript |
| `tools/` | Importación, normalización y servidor local |
| `data/raw/` | Instantáneas originales fechadas y metadatos |
| `data/processed/` | Auditorías y resultados derivados |
| `data/vehicles/` | Parámetros compartidos del bus provisional |
| `docs/` | Plan, arquitectura, fuentes y decisiones vigentes |
| `archive/transmi3d/` | Juego 3D, Blender, generadores, pruebas y documentación en pausa |

## Documentación

- [Plan y alcance](docs/PLAN_DEL_PROYECTO.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Dirección visual](docs/DIRECCION_VISUAL.md)
- [Estado para continuar](CONTINUAR.md)
- [Primer laboratorio y sus límites](docs/SIMULACION_2D_LOCAL.md)
- [Fuentes](docs/FUENTES.md)

Respaldo autorizado: [daniii3012/transmi-game](https://github.com/daniii3012/transmi-game). El uso actual es local; no se ha publicado una versión jugable. La procedencia y licencia de cada fuente se conservan por separado; una API pública no hereda automáticamente la licencia de otra capa GIS.
