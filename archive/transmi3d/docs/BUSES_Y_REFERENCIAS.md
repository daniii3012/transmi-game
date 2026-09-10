# Buses: selección y guía de referencias

Daniel quiere buses reconocibles, incluyendo articulados, biarticulados y duales. El modelo definitivo debe representar una variante concreta, con referencias de ambos lados y del frente, la trasera y la cabina.

## Familias que debe admitir el proyecto

| Familia | Geometría y operación | Pintura: criterio de trabajo |
|---|---|---|
| Articulado troncal | Dos cuerpos, un fuelle; longitud de prueba cercana a 18 m, pendiente de ficha de la variante | Daniel destaca una franja amarilla. Verificar disposición y generación con fotografías. |
| Biarticulado troncal | Tres cuerpos, dos fuelles; requiere más espacio al girar y parar | Daniel destaca dos franjas amarillas. No asumir que todas las generaciones tienen el mismo patrón. |
| Dual rígido | Un cuerpo; acceso por ambos lados y operación en infraestructura troncal y tráfico mixto | Daniel destaca extremos grises; contrastar variantes híbridas y generaciones. |
| Dual articulado eléctrico | Dos cuerpos, un fuelle, puertas por ambos lados; candidato para segundo bus | Elegir Busscar o Marcopolo, no combinar sus carrocerías. Comprobar pintura final frente a renders de presentación. |

“Dual” se refiere aquí a su operación en infraestructura troncal y tráfico mixto. No significa dos fuelles ni obliga a tener dos tipos de motor. La [descripción oficial de los nuevos eléctricos](https://www.transmilenio.gov.co/comunicaciones/noticias-de-transmilenio/comunicados-oficiales/bogota-pone-rodar-futuro-llegan-50-buses-articulados-electricos-unicos-mundo) confirma acceso por ambos lados, dos secciones y ensamblaje de 25 vehículos por Busscar y 25 por Marcopolo. La entrada a operación se describe como gradual; no asignarles servicios concretos sin comprobarlos.

La [página histórica de tipos de buses](https://www.transmilenio.gov.co/viaje-en-transmi/como-utilizar-transmi/buses-de-transmilenio), actualizada en 2019, ayuda a distinguir articulado y biarticulado, pero no describe por sí sola la flota eléctrica de 2026.

## Referencias visuales localizadas con búsqueda de imágenes

| Referencia | Qué revisar | Estado |
|---|---|---|
| [Busscar: Urbanuss Pluss S5 en pruebas](https://www.busscar.com.co/es/asi-le-fue-en-pruebas-a-bus-de-transmilenio-a-gas-natural-urbanuss-pluss-s5-EV111) | Frente, faros, parabrisas, unión, carrocería y relación con chasis Scania | Fuente del fabricante; foto localizada en búsqueda de imágenes. |
| [Catálogo de Busscar](https://www.busscar.com.co/es/) | Diferencias entre modelos articulados y biarticulados | Fuente del fabricante; falta ficha dimensional de la variante escogida. |
| [Scania Colombia: sistemas de buses](https://www.scania.com/co/es/home/products/buses-and-coaches/bus-systems.html) | Chasis y tipologías | Fuente del fabricante; no sustituye planos de carrocería. |
| [TransMi se transforma con buses eléctricos](https://www.transmilenio.gov.co/publicaciones/154634/transmi-se-transforma-con-mas-y-mejores-buses-electricos) | Diseño promocional del articulado eléctrico A051 | Render localizado; distinguirlo de fotos de unidades entregadas. |
| [Galería del comunicado de los 50 eléctricos](https://www.transmilenio.gov.co/comunicaciones/noticias-de-transmilenio/comunicados-oficiales/bogota-pone-rodar-futuro-llegan-50-buses-articulados-electricos-unicos-mundo) | Exterior, interiores, puertas, cámaras y espejos digitales | Artículo leído; los enlaces directos de algunas fotos fallaron. Falta revisión visual completa de ambos modelos. |
| [Biarticulado en Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Bogota_TransMilenio_bus_biarticulado.jpg) | Referencia histórica de tres cuerpos y pintura | Foto localizada; confirmar fecha y licencia del archivo si se incorpora a una carpeta visual. |

Se hicieron búsquedas para eléctricos duales, Busscar/Scania S5 y franjas de articulados/biarticulados. Los resultados mezclan generaciones y a veces etiquetan mal la tipología: confirmar contando cuerpos y fuelles. La observación de Daniel sobre las franjas queda registrada como requisito a contrastar, no como una regla oficial universal ya demostrada.

## Ficha mínima antes de modelar un bus definitivo

Registrar modelo, año/generación, operador de referencia, chasis, carrocería, propulsión y longitud/ancho/altura; ubicación de ejes y articulaciones; puertas y escaleras por lado; posición y forma de parabrisas, ventanas, espejos y luces. Para cada dimensión, anotar fuente y confianza. No deducir medidas exactas de una fotografía en perspectiva.

Crear primero volúmenes de prueba, ejes y pivotes; comprobar giros y reversa; después modelar el exterior, puertas animadas y cabina visible. Exportar GLB con piezas separadas y aplicar escala en Blender. Pintura y ruteros deben ser recursos configurables, no geometría duplicada por ruta.

Para la primera entrega jugable bastan un volante funcional, tablero de velocidad, aceleración/frenado coherentes y puertas con enclavamiento. Las diferencias entre eléctrico y combustión se representarán inicialmente mediante respuesta del acelerador y audio, con parámetros propios.
