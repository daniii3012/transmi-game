# Primera sección conducible de Mandalay

9 de septiembre de 2026 · disposición `mandalay-local-v1` · prototipo local.

Abrir **ABRIR_MANDALAY.command**. También se llega desde la pausa de la pista anterior, con «Conducir en Mandalay». No requiere instalar herramientas adicionales en el equipo de Daniel.

## Qué se puede hacer

Dos prácticas, hacia Av. Boyacá o hacia Banderas, seleccionables con **Esc**. Cada una empieza a 75 m del punto de parada: aproximarse, detenerse, abrir con **P**, esperar 4 segundos, cerrar y avanzar 25 m. Los rótulos indican el sentido, no un recorrido hasta esas estaciones. No se ofrece un servicio comercial ni se circula por Boyacá todavía.

Se conserva la conducción del articulado, reversa, deslizamiento al rozar el andén, cámaras orientables, zoom y tolerancia de parada. La línea arena corresponde a la posición del frente del bus. **W/S** acelerar/frenar, **A/D** girar, **Espacio** freno de mano, **R** avance/reversa, **C** cámara, **clic derecho + ratón** orientar, **rueda** acercar, **V** centrar, **Q/E** mirar a los lados en cabina, **Retroceso** reiniciar, **F2** explorador.

La atención verifica las cuatro puertas, incluidos los anclajes del cuerpo trasero. Acepta una separación de 0,025–0,90 m y error longitudinal de hasta 1,20 m por puerta. Son parámetros de accesibilidad del juego. Salirse de alineación reinicia la espera; retroceder no completa la salida. Las ocho hojas del bus se animan; aún no hay puertas móviles de plataforma ni pasajeros.

## Geometría y procedencia

- Cuatro huellas de secciones Vagon del esquema oficial de Mandalay, con zona central unida sin superficies superpuestas. Dos plataformas paralelas con dos módulos cada una. Referencia: [investigación y límites](MANDALAY_REFERENCIAS_ADICIONALES.md).
- Calzadas, andenes, separadores y huellas de edificios de la instantánea oficial del 9 de septiembre. Datos fuente conservados sin cambios.
- Recorte local de **480 m fuente → 390 m jugables**. Los 300 m centrales permanecen intactos; los 180 m restantes se reducen a 90 m. Es un ensayo local nuevo, no la disposición completa del corredor del estudio anterior ni una escala global de la ciudad.
- **84 partes de edificios** conservan dimensiones de huella y patios; alturas estimadas por pisos × 3 m. Se trasladan los edificios de los extremos, sin aplastarlos. Se omiten 179 registros por límites del recorte, contacto con calzadas o solapamientos tras acercarlos. Ese conteo no mide ahorro total de modelado.
- El esquema de estación y el catastro no coinciden exactamente en el borde. Se añaden **58,68 m² de empalmes de superficie estimados**, todos dentro de una franja máxima de 1 m desde la calzada publicada. Se recortan las caras de andén/separador que los ocultarían. No se modifica la cartografía original ni se afirma que el borde esté levantado en campo.
- Las cubiertas, cerramientos, vegetación, ventanas y mobiliario son elaboración provisional propia. El puente peatonal toma como referencia visual la ortofoto SIMUR nominal 2021; su altura, apoyos y accesos son aproximaciones. No es evidencia de la situación física de septiembre de 2026.

La reserva de 150 m por lado protege la estación y el acceso representado. Antes de conectarla al resto del corredor deben revisarse los extremos, las rampas y el enlace con la disposición común. El eje fuente se conserva en AEQD, con origen WGS84 de Mandalay y orientación registrada en el resumen. El eje longitudinal local transforma `z` así: dentro de ±150 m, identidad; fuera, signo(z) × (150 + (abs(z) − 150) × 0,5). No se aplica al tamaño del bus ni a los edificios.

## Qué sigue provisional

Altura de plataforma 1,10 m, cubierta desde 4,35 m y deck del puente alrededor de 6,3 m: **supuestos del modelo**, no cotas verificadas. Las puertas de práctica se diseñaron para el articulado provisional; no prueban nomenclatura A/B, compatibilidad real o distribución de paradas de 2026. La sección Externa 287 se excluye por función física ambigua.

La conducción continúa siendo plana. Hay colisiones de plataforma, cubiertas y estructura principal del puente; edificios, vegetación y vías laterales son contexto y no tienen una simulación física completa. Los extremos reinician la práctica si se sale de la muestra. No hay acceso peatonal controlable, pendientes para el bus, tráfico, rutas oficiales, sonido, guardado de partida ni carga por sectores. El aspecto cozy está en una primera aplicación; no es el acabado final.

El servicio nuevo de esquemas tiene copyright TransMilenio S.A. y licencia de reutilización aún no establecida; se mantiene separado de las seis capas CC BY 4.0. No se incorporan fotografías externas como texturas. Revisar esa procedencia antes de una futura distribución.

## Archivos y comprobaciones

- `data/design/mandalay.json`: parámetros, estimaciones y versión.
- `tools/build_mandalay.py`: generación reproducible desde fuentes locales; triangulación compartida, compresión, selección de contexto y registro de ajustes.
- `game/data/mandalay.json` y `data/processed/mandalay_summary.json`: escena y procedencia.
- `mandalay_world.gd`: arquitectura provisional y decoración; `mandalay.gd`: dos sentidos sobre el controlador compartido de práctica; `station_service.gd`: parada orientable y anclajes.
- `game/tests/test_mandalay.gd`: 17 comprobaciones, incluidos los dos ciclos completos con colisiones de escena y apertura visual.
- `tests/test_mandalay.py`: escala de aristas contrastada con distancias geodésicas, conservación de huellas/patios y hashes, envolvente completa del bus sobre la superficie en ambos recorridos.

La integración de la pista anterior sigue pasando tras reutilizar su controlador. La suite Python tiene 11 pruebas aprobadas. Estas pruebas verifican el prototipo: no sustituyen cotas, vigencia de operación o un benchmark prolongado.

Reconstruir desde la raíz con `../../work/venv/bin/python tools/build_mandalay.py`. Comprobar con Godot `--headless --path game --script res://tests/test_mandalay.gd -- --keep-running`. Capturar con Godot gráfico `--path game res://scenes/mandalay.tscn -- --capture-mandalay`.

Capturas nativas: [general](preview_mandalay.png), [cabina](preview_mandalay_cabina.png), [parada](preview_mandalay_parada.png). El próximo hito es revisar niveles y detalles de Mandalay, usar la ficha compartida del vehículo para futuras variantes y preparar la conexión a la siguiente estación; Boyacá se mantiene sin habilitar hasta revisar sus niveles.

La ficha compartida del articulado ya está integrada: anclajes con IDs y hash de versión, GLB reconstruido y detección de desincronización. Ver [ficha del vehículo](FICHA_DE_VEHICULO.md). La siguiente exploración solicitada es la [simulación 2D](EXPLORACION_TRANSMI_2D.md).
