# Estación Mandalay (05101 / TM0082)

Ficha de investigación para una primera reconstrucción métrica. Consulta y descarga de fuentes: **2026-09-09 (UTC−05, Bogotá)**. Las medidas que siguen se separan de la información operativa y visual publicada; no se infieren cotas de una captura de pantalla.

## Datos publicados en el conjunto geográfico local

El registro de estaciones descargado desde la capa oficial de TransMilenio (`FeatureServer/2`) identifica:

| Campo | Valor | Estado |
|---|---:|---|
| `num_est` / nombre | `05101` / Mandalay | Publicado por la capa; confianza alta |
| punto WGS84 | `(-74.14129817180734, 4.630863657469235)` | Publicado; confianza alta |
| `id_trazado` | `TZ009` | Publicado; confianza alta |
| `long_est` | **115.705 m** | Atributo publicado, no medición independiente; confianza alta |
| `ancho_est` | **3 m** | Atributo publicado; no se interpreta como ancho total de plataforma; confianza media-alta |
| `num_vag` | **2** | Atributo publicado; confianza alta |
| `esta_oper` | `1` | Atributo publicado por la capa; confianza alta para el estado del dato, no como garantía de operación futura |
| `cap_art` / `cap_biart` | `144` / `96` | Atributos de capacidad del dataset; no son cotas geométricas |

Fuente y procedencia: [estaciones-troncales-de-transmilenio1](https://datosabiertos.bogota.gov.co/dataset/estaciones-troncales-de-transmilenio1), capa [FeatureServer/2](https://gis.transmilenio.gov.co/arcgis/rest/services/ConsultaSubgerenciaPlanificacionSITP/Consulta_Planificacion_SITP/FeatureServer/2). La descarga local conserva `retrieved_at_utc = 2026-09-09T03:53:01.602284+00:00`, licencia declarada CC BY 4.0 y SHA-256 en `data/raw/20260909T035301Z/manifest.json`.

## Eje y contexto del corredor

El registro de `TZ009` en la capa oficial de trazados nombra el corredor **Américas**, con origen `Avenida Caracas`, destino `Portal Americas`, y tipo `EXCLUSIVO` (`tipo_tra=1`, `esta_oper=1`). El corredor incluye Banderas (05100, al oeste), Mandalay (05101), Av. Américas–Av. Boyacá (05102) y Marsella (05103, al este). Marsella no es la vecina inmediata de Mandalay; entre ambas está Av. Américas–Av. Boyacá.

En la geometría publicada, los vértices inmediatamente alrededor de Mandalay son:

- hacia Banderas: `(-74.1419571222619, 4.630924199140237)`;
- hacia Marsella: `(-74.13975469054466, 4.630689569775616)`.

La dirección local resultante es aproximadamente **O–E**, con una ligera componente hacia el norte al avanzar hacia Banderas y hacia el sur al avanzar hacia Marsella (rumbo local hacia Marsella ≈ **96.5°**, calculado solo a partir de esos vértices WGS84). Esto orienta el eje del corredor/carriles en el prototipo; **no demuestra la orientación del edificio de la estación ni la posición exacta de cada plataforma**.

Fuente: [trazados-troncales-de-transmilenio](https://datosabiertos.bogota.gov.co/dataset/trazados-troncales-de-transmilenio), capa [FeatureServer/5](https://gis.transmilenio.gov.co/arcgis/rest/services/ConsultaSubgerenciaPlanificacionSITP/Consulta_Planificacion_SITP/FeatureServer/5), registro `id_trazado=TZ009`.

## Visor oficial de planos

La página [Plano de estaciones y portales de TransMilenio](https://tramites.transmilenio.gov.co/plano-estaciones-portales-transmilenio) carga el endpoint público [`/station-maps/api/map`](https://tramites.transmilenio.gov.co/station-maps/api/map). En la respuesta consultada, Mandalay aparece así:

```json
{
  "id": 98,
  "code": "TM0082",
  "name": "Mandalay",
  "description": null,
  "type": "station",
  "x_pct": 0.68281,
  "y_pct": 0.34637,
  "line": {"id": 6, "name": "Américas", "color": "#BB0615"},
  "image_url": "https://tramites.transmilenio.gov.co/storage/station-maps/markers/optimized/7040645e-9547-46ef-89d5-229741168670.jpg"
}
```

Consulta puntual exitosa del 2026-09-09 mediante `curl`, con cabecera `Accept: application/json`. El principal revisó la copia temporal de 48.842 bytes y confirmó el registro anterior. SHA-256 de la respuesta completa: `de4204921e82e34fc4690e4fb168d69efc2a55fb91e2397ec711241c10c6ecac`. Aquí se conserva únicamente el registro relevante; la respuesta completa quedó fuera del repositorio. La licencia de esta API está pendiente de establecer y no se hereda de la capa geográfica.

La respuesta también publica una imagen base de 1920×1080 y un marcador de Mandalay, pero al descargar tanto la imagen base como la imagen del marcador el servidor respondió **404 Página no encontrada** (consulta 2026-09-09). No se obtuvo un plano utilizable a través de esos enlaces; esto no descarta que existan otras fuentes oficiales. La reconsulta por urllib del endpoint devolvió 403 durante la revisión. El registro observado del visor permite identificar el marcador, no determinar dimensiones, puertas o accesos.

## Vagones y referencias de operación histórica

La nota oficial [Conozca los nuevos cambios para algunas estaciones del Sistema](https://www.transmilenio.gov.co/comunicaciones/noticias-de-transmilenio/boletines-informativos/conozca-los-nuevos-cambios-para-algunas-estaciones-del-sistema) está fechada **3 de mayo de 2019**. Su tabla “Cambios del 8 del Mayo en estaciones” para Mandalay publica estas paradas:

| Vagón | Oriente → Occidente | Occidente → Oriente |
|---|---|---|
| 1 | servicios **5** y **F51** | servicios **5** y **M51** |
| 2 | servicio **F19** | servicios **C19** |

La misma página enlaza una imagen histórica de “Puntos de parada de la estación Mandalay” con `parada=7670`, pero ese enlace legado también responde 404 al consultarlo ahora. Esta tabla documenta una configuración de operación de 2019, **no la vigente en 2026 ni un plano de puertas**. No deben modelarse puertas individuales ni señalización actual a partir de esos códigos de servicio.

## Primera reconstrucción recomendada

Para una versión inicial reproducible, usar el punto WGS84 y el eje local de `TZ009`; conservar **115.705 m**, **3 m** y **2 vagones** como atributos publicados del dataset, marcando el ancho como pendiente de interpretación geométrica. Puede representarse una estación lineal de dos módulos/vagones a lo largo del eje O–E, con la advertencia de que la división exacta de la longitud, las plataformas, los accesos y las puertas no están verificadas.

### Pendientes de verificación

- plano o levantamiento que confirme si los 115.705 m corresponden a una plataforma, a la envolvente completa o a otra convención;
- ancho físico de plataforma y separación entre plataformas/carriles;
- número y posición de accesos, escaleras, rampas y torniquetes;
- puertas por vagón y correspondencia con servicios;
- orientación exacta del edificio respecto al eje del trazado;
- estado operativo vigente y cambios posteriores a la tabla de 2019.

No se incorporan al juego las imágenes externas descargadas para consulta; permanecen solo en `work/mandalay/`.
