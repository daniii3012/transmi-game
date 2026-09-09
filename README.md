# Bogotá Transmi

Simulador de buses de Bogotá para un solo jugador: meta final de todo el sistema BRT de TransMilenio, ciudad condensada, conducción accesible y dirección visual cozy. Los datos fuente conservan escala 1:1; el mundo jugable estudia compresión selectiva entre lugares importantes. Buses, plataformas y carriles mantienen proporciones coherentes. Primera sesión: 8 de septiembre de 2026, hora de Bogotá.

**Respaldo del proyecto:** [daniii3012/transmi-game](https://github.com/daniii3012/transmi-game). Para continuar, leer primero [CONTINUAR.md](CONTINUAR.md). El documento principal es [PLAN_DEL_PROYECTO.md](docs/PLAN_DEL_PROYECTO.md).

## Qué existe hoy

- **Primera pista conducible:** articulado de 18 m provisional, reversa, puertas, cámaras orientables, deslizamiento al rozar el andén y ciclo de parada con tolerancia ampliada. Modelo editable de Blender incluido.
- **Comparación 3D de escala:** eje del piloto de 1.602,47 m frente a una propuesta de 1.285,94 m, preservando tres estaciones y reservas de espacio. Generación reproducible; es un estudio de disposición, todavía sin carriles transitables.
- Proyecto nativo de Godot 4.7.2 y explorador de cámara libre de un recorte de Américas: Mandalay, Av. Américas–Av. Boyacá y Marsella.
- Descarga reproducible de seis capas oficiales, con licencias, metadatos, identificadores y comprobaciones SHA-256.
- Conversión de polígonos reales de calzadas, andenes, separadores y construcciones a una escena 3D de unas 301.000 caras triangulares.
- Coordenadas locales en metros y pruebas de escala y conservación de patios interiores.
- Plan de mapa, buses, estaciones, rutas, obras y continuidad entre sesiones.

**El bus se conduce en una pista de ensayo ficticia.** El mapa real de Américas continúa como explorador geográfico. Los edificios usan alturas estimadas; las estaciones son marcadores; el terreno es plano. Los puentes, las obras actuales y sus desvíos requieren modelado específico. Su apariencia es provisional.

## Abrir

En Finder, abrir **ABRIR_SIMULADOR.command** con doble clic para conducir. Controles y límites: [Prueba de conducción](docs/PRUEBA_DE_CONDUCCION.md). Abrir **ABRIR_EXPLORADOR.command** para inspeccionar Américas. Usa la copia de Godot que está en `../../work/tools/Godot.app`, relativa a esta carpeta. No requiere descargar nada para explorar la muestra ya preparada. También puede abrirse `game/project.godot` con Godot 4.7.2.

**ABRIR_ESTUDIO_ESCALA.command** abre la comparación entre referencia y versión condensada. **1** vista conjunta, **2/3** detalle de Mandalay en cada versión, clic derecho para orbitar y rueda para acercar. Las bandas arena son reservas de diseño; los edificios ilustran la reducción de contexto y no reproducen fachadas reales. [Resultados y límites](docs/ESCALA_Y_COMPRESION.md).

Controles: **1** vista general; **2/3/4** estaciones; **WASD o flechas** mover; **Q/E** bajar/subir respecto a la cámara; **Shift** acelerar; **clic derecho mantenido** mirar; **B** mostrar/ocultar edificios; **Esc** liberar cursor. Es una cámara de inspección, sin colisiones.

## Documentos

- [Primera prueba de conducción](docs/PRUEBA_DE_CONDUCCION.md)
- [Investigación del buscador de rutas](docs/RUTAS_INVESTIGACION.md)
- [Plan del proyecto](docs/PLAN_DEL_PROYECTO.md)
- [Sistemas y hoja de ruta hacia toda la red BRT](docs/SISTEMAS_Y_HOJA_DE_RUTA.md)
- [Dirección visual y prioridades](docs/DIRECCION_VISUAL.md)
- [Escala y compresión selectiva](docs/ESCALA_Y_COMPRESION.md)
- [IA local de buses y etapas de tráfico](docs/IA_DE_BUSES.md) — planificada
- [Investigación de Mandalay](docs/ESTACION_MANDALAY.md)
- [Trabajo con agentes ligeros](docs/TRABAJO_CON_AGENTES.md)
- [Fuentes y límites de los datos](docs/FUENTES.md)
- [Buses y referencias visuales](docs/BUSES_Y_REFERENCIAS.md)
- [Arquitectura propuesta](docs/ARQUITECTURA.md)
- [Continuidad y pendientes](CONTINUAR.md)
- [Resumen de datos procesados](data/processed/summary.json)
- [Vista general del primer render](docs/preview_general.png)

Las capturas son del prototipo, no del aspecto final del simulador. Ver [bus de prueba](docs/preview_practica.png), [cabina](docs/preview_cabina.png) y [puertas](docs/preview_puertas.png).

Estudio nuevo: [comparación de escala](docs/preview_escala.png) y [detalle ilustrativo de Mandalay](docs/preview_escala_mandalay.png).

## Reconstruir los datos

Desde esta carpeta, con Python 3.9:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
.venv/bin/python tools/fetch_pilot.py
.venv/bin/python tools/build_pilot.py
.venv/bin/python -m unittest discover -s tests -v
```

La descarga usa la instantánea existente; `tools/fetch_pilot.py --refresh` crea otra fechada y cambia `data/raw/latest.json`. El resultado 3D está en `game/data/pilot.json`. Actualizar los datos no actualiza automáticamente el modelo de obras.

Para reconstruir el estudio de compresión, ejecutar `.venv/bin/python tools/build_scale_study.py`. Usa la instantánea fijada en `data/design/americas_scale_study.json` y genera archivos separados; no modifica el explorador original. Las distancias del estudio son sobre el eje oficial recortado, no sobre carriles ni rutas de servicio.

## Atribución

Geometría: Unidad Administrativa Especial de Catastro Distrital / IDECA y entidades del Mapa de Referencia; estaciones y trazados: TRANSMILENIO S.A. Las seis fichas consultadas declaran CC BY 4.0. Se conservan las fichas originales en `data/raw/20260909T035301Z/`. Cambios realizados: recorte espacial, reproyección, triangulación y extrusión con alturas estimadas. Ver [fuentes](docs/FUENTES.md).
