# Av. Américas–Av. Boyacá: niveles y referencias

Ficha acotada de investigación para el cruce de la avenida de Las Américas (AC 6) con avenida Boyacá (AK 72) y la estación **Av. Américas–Av. Boyacá** (05102). Consulta: **9 de septiembre de 2026 (Bogotá, UTC−05)**. El alcance es este cruce; no incluye las obras de avenida 68 ni el nodo de carrera 50.

## Resultado que puede usarse en el prototipo

Hay evidencia oficial de una estación ubicada en **AV Americas–KR 71**, con longitud publicada de **115,715 m**, ancho publicado de **3,0 m**, área publicada de **347,145 m²**, dos vagones y un punto WGS84 **(-74.1342245707, 4.6301177984)**. La misma ficha publica **1 acceso**, de los cuales **1 es acceso por puente**; los campos de acceso desde espacio público y acceso por deprimido valen 0. Estos son atributos del inventario, no un levantamiento constructivo ni cotas de plataforma.

Una referencia distrital de fecha no confirmada denomina el paso de avenida Boyacá como **“bajo el Puente N-S”**. Es suficiente para una hipótesis geométrica de que la calzada norte–sur de Boyacá pasa sobre el entorno de Américas y que la estación tiene conexión peatonal por puente. No permite fijar la altura libre, la cota de la calzada superior, la cota BRT, la pendiente de rampas ni el espesor de la estructura.

No se encontró en las fuentes oficiales consultadas una sección transversal, perfil longitudinal, plano constructivo o tabla de cotas que confirme niveles en metros. La física debe mantener esas alturas como parámetros provisionales hasta obtener planos del IDU o un levantamiento verificable.

## Fuentes primarias

### 1. Inventario oficial de estaciones troncales de TransMilenio

Fuente: [FeatureServer/2, consulta reproducible para `num_est=05102`](https://gis.transmilenio.gov.co/arcgis/rest/services/ConsultaSubgerenciaPlanificacionSITP/Consulta_Planificacion_SITP/FeatureServer/2/query?where=num_est%3D%2705102%27&outFields=%2A&returnGeometry=true&outSR=4326&f=pjson) y [metadatos de la capa](https://gis.transmilenio.gov.co/arcgis/rest/services/ConsultaSubgerenciaPlanificacionSITP/Consulta_Planificacion_SITP/FeatureServer/2?f=pjson). El conjunto también está publicado en [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/estaciones-troncales-de-transmilenio).

Fecha de consulta: 2026-09-09. El registro `objectid=635` identifica `05102`, “AV. Américas - AV. Boyacá”, `TZ009`, coordenadas **(-74.13422457, 4.63011780)**, `ub_est=AV Americas - KR 71`, `long_est=115.715`, `ancho_est=3.0`, `area_est=347.145`, `num_vag=2`, `num_acc=1`, `acc_esp=0`, `acc_depr=0` y `acc_puent=1`. El campo `esta_oper=1` describe el estado del registro consultado; no certifica por sí solo la operación física de la estación ese día.

Respalda: identidad, punto, corredor, dimensiones de inventario, número de accesos y existencia de un acceso clasificado como puente. **No respalda:** altura de estación, elevación de calzadas, gálibo, pendientes, ancho real de plataforma, posición del puente o cotas de rampas/escaleras. Los valores `long_est`, `ancho_est` y `area_est` deben conservarse como datos publicados, no convertirlos en una caja constructiva sin contraste.

### 2. Visor oficial de planos/listado de estaciones

Fuente: [API pública del visor de estaciones](https://tramites.transmilenio.gov.co/station-maps/api/map) y [página del visor](https://tramites.transmilenio.gov.co/plano-estaciones-portales-transmilenio).

En la respuesta consultada aparece el marcador `TM0081`, “Av Américas -Av. Boyacá”, tipo `station`, línea Américas, con `x_pct=0.6655` y `y_pct=0.37649`. La API es útil para conservar el identificador del visor y comprobar que el nombre corresponde a la estación del cruce. La imagen enlazada por el marcador no entregó un plano constructivo utilizable durante la consulta; el registro no publica dimensiones, alturas, puertas ni accesos detallados.

Estado: referencia de identificación visual y de procedencia, no fuente de cotas. La respuesta observada no demuestra por sí sola vigencia operativa futura.

### 3. IDU: contrato de factibilidad y diseños para la intersección exacta

Fuente oficial: [Reporte de Puntos IDU, febrero de 2025](https://www.idu.gov.co/Archivos_Portal/2025/servicio-a-la-ciudadania/canales-de-atencion/02-febrero/REPORTE-Puntos-IDU-24-02-2025.pdf). El reporte registra el contrato **IDU-529-2022** como consultoría para evaluar y diseñar la ampliación de dos cruces de Américas: Boyacá (AK 72) y avenida del Congreso Eucarístico (AK 68), en ejecución, para Kennedy y Puente Aranda, bajo la Dirección Técnica de Proyectos. La ficha de mayo de 2024 contiene la misma identificación [IDU, mayo de 2024](https://www.idu.gov.co/Archivos_Portal/2024/servicio-a-la-ciudadania/canales-de-atencion/05-mayo/Puntos-IDU-20-05-2024.pdf).

Respalda que durante 2024–2025 el cruce seguía asociado a una consultoría de factibilidad/estudios y diseños, no a una obra cuya geometría final pueda darse por construida. No se hallaron en esos reportes perfiles, planos de cotas, gálibos o secciones publicadas. Para el escenario de septiembre de 2026, el estado exacto del contrato y cualquier diseño adoptado requieren una consulta vigente del expediente IDU/SECOP; no anticipar niveles proyectados.

### 4. Alcaldía de Bogotá: proyecto BIM del IDU

Fuente: [El Instituto de Desarrollo Urbano tendrá 25 proyectos con BIM en 2023](https://bogota.gov.co/mi-ciudad/movilidad/el-instituto-de-desarrollo-urbano-tendra-25-proyectos-con-bim-en-2023), publicada el **27 de octubre de 2022**.

La nota incluye, entre los proyectos en diseño, los estudios para establecer la factibilidad de ampliar las intersecciones de Américas (AC 6) con Boyacá (AK 72) y con carrera 68. Es una confirmación institucional independiente de que se trataba de una fase de estudios/diseño. No aporta cotas ni debe mezclarse con las obras de carrera 68 como si fueran el cruce de Boyacá.

### 5. Secretaría Distrital de Movilidad: referencia geométrica del paso

Fuente: [Registro Bici Bogotá, jornadas en vía](https://registrobicibogota.movilidadbogota.gov.co/), consultado el 2026-09-09. La página lista el punto **“Av Boyaca con Av Américas - Bajo el Puente N-S”** para una jornada del miércoles 2 de septiembre. La página no muestra de forma inequívoca el año junto a esa fecha; por ello se usa como evidencia terminológica/geométrica observada, no como certificado de operación en septiembre de 2026.

Respalda la existencia o reconocimiento administrativo de un **puente N–S** en el cruce. No publica cota, luz, ancho, rampas ni relación altimétrica exacta con los carriles BRT. La frase no basta para decidir si el puente corresponde a calzada mixta, BRT, o una estructura con varios niveles sin revisar planos.

## Medidas y decisiones de modelado

**Confirmadas como atributos publicados:** punto de estación; longitud 115,715 m; ancho de inventario 3,0 m; área 347,145 m²; dos vagones; un acceso; un acceso clasificado como puente; ubicación “AV Americas–KR 71”; nomenclatura “Puente N-S”.

**Estimadas o solo hipótesis geométrica:** que Boyacá pasa sobre Américas en sentido norte–sur; posición exacta del puente respecto de la estación; altura del tablero; gálibo; nivel de carriles mixtos y BRT; altura de andén; pendientes y longitudes de rampas; escaleras; separación vertical entre plataformas y calzadas.

**Pendientes:** obtener del expediente IDU-529-2022 o de un repositorio oficial un plano/perfil con cotas y fases vigentes; verificar si el acceso puente inventariado es peatonal, su localización y si tiene rampas; comprobar estado operativo real de la estación a septiembre de 2026; confirmar si el diseño de ampliación cambió la sección existente. Hasta entonces, mantener el cruce fuera de la circulación física final o usar un nivel provisional explícitamente marcado como estimado.

No se copian imágenes ni se incorporan texturas externas al juego.

Revisión del principal: punto, longitud y ancho contrastados con la instantánea geográfica local; campos de área y accesos reconsultados directamente en la API oficial; nota BIM de 2022 consultada directamente. No se reobtuvieron cotas del PDF IDU ni se validó la fecha de la jornada de Registro Bici; conservar esas referencias como pistas de investigación. Ninguna de estas fuentes habilita por sí sola el cruce para conducir.
