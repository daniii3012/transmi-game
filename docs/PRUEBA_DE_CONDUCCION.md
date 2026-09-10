# Primera prueba conducible

9 de septiembre de 2026. Abrir `ABRIR_SIMULADOR.command` desde Finder o `game/project.godot` con Godot 4.7.2. No requiere red. `F2` cambia entre pista y explorador geográfico; esta pista sigue siendo ficticia. La nueva sección basada en huellas de Mandalay se abre con ABRIR_MANDALAY.command o desde el menú de pausa; ver [Mandalay conducible](MANDALAY_JUGABLE.md).

| Control | Acción |
|---|---|
| W / flecha arriba | Acelerar |
| S / flecha abajo | Frenar |
| A, D / flechas laterales | Girar |
| Espacio | Freno de mano |
| R | Alternar avance/reversa, detenido |
| P | Abrir/cerrar las cuatro puertas izquierdas, detenido |
| C | Seguimiento, cabina, exterior |
| Clic derecho mantenido + ratón | Orientar cualquiera de las tres cámaras |
| Rueda del ratón | Acercar/alejar en exterior; ajustar campo de visión en cabina |
| V | Centrar la cámara |
| Q / E, en cabina | Mirar rápidamente a izquierda / derecha mientras se mantiene pulsado |
| Retroceso | Volver al inicio de la práctica |
| Esc | Pausa y menú |
| F2 | Explorar Américas / volver a conducir |

Avanzar por la recta hasta la plataforma. Frenar antes de la marca y ajustar la posición hasta que la interfaz indique alineación correcta. Abrir puertas, esperar cuatro segundos, cerrar y avanzar al menos 15 m para terminar la práctica. La comprobación incluye las cuatro puertas: alinear solo el frente no basta si el remolque queda cruzado.

La parada admite una separación entre puerta y borde de plataforma de **0,025 a 0,90 m**, hasta **1,20 m de desfase longitudinal por puerta** y un rumbo del frente dentro de 6°. Estos valores son tolerancias de juego para la práctica, no medidas reglamentarias de abordaje. Las puertas del remolque también deben quedar dentro del margen.

## Lo implementado

Modelo cinemático plano de un bus articulado con enganche detrás del eje de referencia, remolque que sigue su propia trayectoria, dirección limitada por velocidad, aceleración/freno progresivos, reversa y límite de articulación. Se comprueban los dos cuerpos y la envolvente del fuelle contra obstáculos mediante pasos pequeños y barrido de traslación. Las puertas impiden avanzar mientras estén abiertas o cerrándose.

Al rozar lateralmente el andén, el vehículo puede continuar deslizándose sin un frenado artificial completo. Cada desplazamiento se vuelve a comprobar contra obstáculos; los impactos frontales o maniobras sin salida libre siguen deteniendo el bus. La respuesta es una aproximación arcade plana, sin un modelo físico completo de fricción.

Modelo editable de Blender, ruedas, interior sencillo, ventanas, cuatro puertas con dos hojas deslizantes cada una y fuelle generado por el motor. La animación de apertura es de prueba, pendiente de elegir el mecanismo de una variante real. Tres cámaras orientables, velocidad/marcha/puertas, indicaciones de parada, pausa y reinicio. Primera aplicación del acabado cozy a pintura, entorno, vegetación y HUD; el escenario continúa siendo ficticio.

## Validación realizada

- 19 comprobaciones automáticas de conducción, geometría de giro, reversa, articulación, puertas, alineación y colisiones. Incluyen una barrera de 5 cm y colisión del remolque con el frente libre.
- 12 comprobaciones específicas del comentario de Daniel: roce durante diez segundos, separación posterior del andén, impactos frontales, tolerancia de parada y orientación/centrado de cámara. En el ensayo de roce, el bus avanzó unos 39,9 m a 4 m/s y terminó sin solape de sus tres envolventes con el muro.
- Prueba de integración en la escena: importa ambos cuerpos y ocho hojas, conduce automáticamente hasta la plataforma sin colisión, completa el tiempo de atención y comprueba que se abrieron las hojas del modelo.
- Ejecución gráfica en OpenGL sobre Metal / Apple M3 Pro; inspección de capturas exterior, cabina y puertas abiertas. Son capturas del juego, no imágenes generadas.

## Límites de esta entrega

Pista plana y entorno ficticio. Todavía no hay contacto físico con pendientes, suspensión, espejos funcionales, sonido, pasajeros visibles, tráfico, guardado de partida o selector de rutas oficiales. La conducción permite salir al césped; los impactos frontales detienen el vehículo y el límite exterior devuelve al inicio. Colisiones conservadoras de carrocería, sin simulación de daño ni contacto individual de retrovisores/hojas abiertas.

Las dimensiones y parámetros del vehículo son provisionales. El objetivo inmediato es probar maniobras; el aspecto final y el mapa real se desarrollan en etapas posteriores. La siguiente integración geográfica exige revisar los niveles y carriles de Américas y construir una estación con medidas contrastadas.

## Ejecutar pruebas

Con `GODOT` apuntando al ejecutable instalado, desde la raíz del proyecto:

```sh
"$GODOT" --headless --path game --script res://tests/test_driving.gd
"$GODOT" --headless --path game --script res://tests/test_player_feedback.gd
"$GODOT" --headless --path game --script res://tests/test_practice_scene.gd -- --keep-running
```

Las capturas se generan con `-- --capture-practice` en ejecución gráfica. El explorador usa `res://scenes/main.tscn -- --capture`.
