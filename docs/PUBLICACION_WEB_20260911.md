# Viabilidad de publicar en GitHub Pages — análisis, 11 sep. 2026

Daniel preguntó si es posible subir el simulador a un host como GitHub Pages y que
**todas las funcionalidades sigan presentes**. Este documento evalúa eso. **No se publicó
nada**; AGENTS.md exige solicitud expresa y aquí solo se pidió la evaluación.

## Respuesta corta

Sí. `app/dist` es estático puro y no necesita servidor. Con una salvedad de tipo MIME que
se comprueba en el primer despliegue y una decisión de licencia que no es técnica.

## Qué se publicaría

25 archivos, **10 MB sin comprimir y 1,7 MB comprimidos**: 13 módulos `.mjs`, 7 JSON de
datos, Three.js vendorizado con su licencia, un HTML y una hoja de estilo. El límite de
GitHub Pages es 1 GB por sitio y 100 GB de tráfico al mes, así que el tamaño no es un
problema ni de lejos.

## Revisión funcionalidad por funcionalidad

| Qué necesita | Estado | Nota |
|---|---|---|
| Servidor de aplicación | No necesita | Todo el cálculo ocurre en el navegador |
| Rutas de los recursos | Compatible | Todas relativas (`./services.json`); funciona bajo `/transmi-game/` |
| Web Worker de módulo | Compatible | `new Worker('./worker.mjs', {type:'module'})` funciona sobre HTTPS |
| Recursos externos | Ninguno | No se carga ni una fuente, script o imagen de otro dominio |
| Cabeceras especiales | Ninguna | No usa `SharedArrayBuffer`, aislamiento de origen ni service worker |
| Guardado del escenario | Compatible | `localStorage`, por origen y por navegador |
| Invalidación de caché | Ya resuelta | Sufijo `?v=` en los 25 usos; Pages cachea, el sufijo fuerza la recarga |
| Nombres que Jekyll ignora | Ninguno | No hay archivos ni carpetas que empiecen por `_` |
| Consultas en vivo a APIs | No hace | Los datos son instantáneas locales; jugar no consulta TransMilenio ni OSM |

**Lo único a verificar:** que Pages sirva `.mjs` con un tipo JavaScript. Si lo sirviera
como `text/plain`, el navegador rechazaría los módulos y la aplicación no arrancaría. Se
comprueba en el primer despliegue abriendo la consola; si fallara, la solución es renombrar
a `.js` o añadir un paso de construcción. Conviene añadir un `.nojekyll` vacío de todos
modos, que cuesta nada y evita sorpresas del procesado de Jekyll.

## Cómo habría que desplegarlo

Pages publica la raíz del repositorio o la carpeta `docs/`. **Ninguna de las dos sirve
aquí**: la raíz expone `data/` entero, unos 90 MB de instantáneas crudas, y `docs/` es la
documentación del proyecto, no la aplicación.

Lo correcto es un flujo de GitHub Actions que publique **solo `app/dist`** como artefacto
de Pages. Eso mantiene fuera del sitio los datos crudos, las herramientas y el histórico,
y deja el repositorio como está.

## Lo que cambia al publicar, aunque el código sea el mismo

- **El lanzador LAN deja de ser el camino**. `ABRIR_EN_RED_LOCAL.command` seguiría
  existiendo para uso local, pero la URL pública lo reemplaza para cualquiera.
- **Cada visitante ejecuta su propia simulación**, como ya pasa entre pestañas. No hay
  estado compartido ni servidor que lo sostenga.
- **La construcción inicial toma unos 8 s de CPU** y unos 500 MB de memoria en el
  escenario completo. En un equipo modesto o un móvil de poca memoria puede ser lento o
  fallar. La QA del proyecto es de escritorio: antes de presentarlo como público conviene
  probar en móviles reales, que es un pendiente ya declarado en el plan.
- **Las cifras y vigencias quedan a la vista de cualquiera.** La aplicación ya distingue
  publicado de estimado y rotula los horarios vencidos, que es justo lo que hace falta
  para que no se malinterprete.

## Licencia y atribución

Daniel decidió que, al estar públicos los enlaces y no declarar licencia, se asumirá que
pueden usarse, y que el proyecto quede sin licencia o con la que corresponda. Queda
registrado como decisión suya.

Dos cosas que conviene hacer igual, porque son obligaciones concretas y baratas:

1. **OpenStreetMap es ODbL 1.0** y exige atribución. Ya aparece «© OpenStreetMap» en el
   mapa; al publicar conviene que el enlace a la licencia sea visible, no solo el texto.
2. **Three.js va con su licencia MIT** en `app/dist/vendor/THREE-LICENSE.txt`, que se
   publica junto con la librería. Eso ya cumple.

Sobre el resto: [FUENTES.md](FUENTES.md) registra que la licencia de los endpoints de
rutas y cartografía de TransMilenio no está establecida en las respuestas consultadas. No
soy quien pueda resolver eso, y «es público» no equivale a «es reutilizable» en términos
legales. Lo dejo anotado una vez y no insisto: la decisión es de Daniel y está tomada.

Un detalle práctico distinto de la licencia: publicar una réplica del sistema conviene que
deje claro que **no es un sitio oficial de TransMilenio y no son posiciones en vivo**. Eso
ya está dicho dentro de la aplicación; en un sitio público debería estar también en la
primera pantalla.

## Recomendación

Es viable y el trabajo técnico es pequeño: un flujo de Actions que publique `app/dist`, un
`.nojekyll`, y comprobar la consola en el primer despliegue. Lo que no es pequeño es la
decisión de publicar, y esa ya la tomó Daniel. Cuando dé la orden, se hace.
