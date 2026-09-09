# Bogotá Transmi

Proyecto personal de simulación de buses de TransMilenio, con Bogotá a escala métrica real y conducción accesible. Primera sesión: 8 de septiembre de 2026, hora de Bogotá.

**El progreso está guardado localmente.** Para continuar, leer primero [CONTINUAR.md](CONTINUAR.md). El documento principal es [PLAN_DEL_PROYECTO.md](docs/PLAN_DEL_PROYECTO.md).

## Qué existe hoy

- Proyecto nativo de Godot 4.7.2 y explorador de cámara libre de un recorte de Américas: Mandalay, Av. Américas–Av. Boyacá y Marsella.
- Descarga reproducible de seis capas oficiales, con licencias, metadatos, identificadores y comprobaciones SHA-256.
- Conversión de polígonos reales de calzadas, andenes, separadores y construcciones a una escena 3D de unas 301.000 caras triangulares.
- Coordenadas locales en metros y pruebas de escala y conservación de patios interiores.
- Plan de mapa, buses, estaciones, rutas, obras y continuidad entre sesiones.

**Todavía no hay un bus conducible.** Esta es una prueba de la base geográfica. Los edificios usan alturas estimadas; las estaciones son marcadores; el terreno es plano. Los puentes, las obras actuales y sus desvíos requieren modelado específico. Su apariencia es provisional.

## Abrir

En Finder, abrir **ABRIR_EXPLORADOR.command** con doble clic. Usa la copia de Godot que está en `../../work/tools/Godot.app`, relativa a esta carpeta. No requiere descargar nada para explorar la muestra ya preparada. También puede abrirse `game/project.godot` con Godot 4.7.2.

Controles: **1** vista general; **2/3/4** estaciones; **WASD o flechas** mover; **Q/E** bajar/subir respecto a la cámara; **Shift** acelerar; **clic derecho mantenido** mirar; **B** mostrar/ocultar edificios; **Esc** liberar cursor. Es una cámara de inspección, sin colisiones.

## Documentos

- [Plan del proyecto](docs/PLAN_DEL_PROYECTO.md)
- [Fuentes y límites de los datos](docs/FUENTES.md)
- [Buses y referencias visuales](docs/BUSES_Y_REFERENCIAS.md)
- [Arquitectura propuesta](docs/ARQUITECTURA.md)
- [Continuidad y pendientes](CONTINUAR.md)
- [Resumen de datos procesados](data/processed/summary.json)
- [Vista general del primer render](docs/preview_general.png)
- [Vista de Av. Boyacá del primer render](docs/preview_boyaca.png)

Las capturas son del prototipo, no del aspecto final del simulador. Consultar CONTINUAR.md para el estado de la última revisión visual.

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

## Atribución

Geometría: Unidad Administrativa Especial de Catastro Distrital / IDECA y entidades del Mapa de Referencia; estaciones y trazados: TRANSMILENIO S.A. Las seis fichas consultadas declaran CC BY 4.0. Se conservan las fichas originales en `data/raw/20260909T035301Z/`. Cambios realizados: recorte espacial, reproyección, triangulación y extrusión con alturas estimadas. Ver [fuentes](docs/FUENTES.md).
