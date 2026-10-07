# Publicar Research Partnership Atlas v1.0.0

La distribución local contiene código, licencia MIT, citación, pruebas y un ZIP de fuentes. No se ha publicado todavía un repositorio remoto ni un registro Zenodo.

## Datos listos para el depósito

- Título: Research Partnership Atlas: International Collaboration and Research Funding Analytics
- Tipo de recurso: Software
- Versión: 1.0.0
- Autores, en orden: Daniel Pinargo; Daniel Lopez
- Titular de derechos: Daniel Pinargo
- Licencia del software: MIT
- Acceso: público
- Palabras clave: CORDIS; international collaboration; research funding; network analysis; Streamlit

La descripción de RELEASE_NOTES.md puede usarse en GitHub o Zenodo. Afiliaciones y ORCID son opcionales y deben corresponder a datos reales. La licencia del código no sustituye las condiciones de los datos CORDIS.

## Subir a GitHub

Nombre recomendado del repositorio: research-partnership-atlas.

1. Cree un repositorio público vacío en GitHub. Para subir desde esta carpeta, no añada README ni LICENSE desde GitHub porque ya están incluidos.
2. Si usa Git, configure su identidad real para el commit si todavía no está configurada. Ejecute desde la carpeta del proyecto:

```text
git add .
git status
git commit -m "Prepare Research Partnership Atlas v1.0.0"
git remote add origin URL_REAL_DEL_REPOSITORIO
git push -u origin main
```

Sustituya URL_REAL_DEL_REPOSITORIO por su URL HTTPS o SSH real. No publique ese marcador. Si ya existe origin, revise su valor antes de modificarlo.

También puede usar la carga de archivos de GitHub. Suba el contenido de la carpeta de fuentes del ZIP, incluidos los archivos ocultos .github, .gitignore y .gitattributes; no suba el ZIP como sustituto del código fuente. No incluya .git, .release-check, __pycache__, entornos ni dist.

3. Añada la URL real como repository-code en CITATION.cff y como enlace del repositorio en README.md.
4. Revise el resultado de GitHub Actions. El workflow comprueba la instalación y cinco pruebas en Python 3.11 / Linux; esa ejecución remota todavía no se ha realizado.

## Registrar mediante la integración GitHub–Zenodo

1. Acceda a Zenodo, vincule GitHub y habilite este repositorio en la integración.
2. Antes de crear la release, registre la fecha real de publicación en CITATION.cff (date-released, formato YYYY-MM-DD) y CHANGELOG.md, confirme los cambios y envíelos a GitHub.
3. Cree una release pública con etiqueta v1.0.0, título Research Partnership Atlas v1.0.0 y descripción de RELEASE_NOTES.md. Seleccione el commit definitivo. Si adjunta el ZIP de fuentes, vuelva a generarlo después de actualizar metadatos.
4. Espere el procesamiento y compruebe autores, versión, licencia MIT, acceso público, archivos y DOI en el registro Zenodo.
5. Incorpore el DOI de la versión en README/CITATION.cff y en la referencia del paper. Este commit posterior no modifica por sí solo los archivos ya archivados por Zenodo; documente ese hecho y use nuevas releases para futuras versiones.

Habilite la integración antes de crear la release. Un push o commit no reemplaza una release. No cree DOI ficticios ni incluya como DOI del artículo el valor de ejemplo de una plantilla editorial.

## Alternativa: depósito manual

Cree un nuevo depósito Zenodo como Software, seleccione acceso público, complete los campos anteriores y cargue dist/research-partnership-atlas-v1.0.0.zip. El archivo .zip.sha256 permite comprobar su integridad. Verifique los metadatos y publique. Enlace el repositorio real como recurso relacionado cuando exista.

Elija una ruta principal de depósito para evitar registrar dos veces la misma versión con identificadores independientes. El conjunto de datos concreto que reproduzca el paper puede depositarse por separado con licencia y atribución propias.

## Alcance científico

VALIDATION.md registra las comprobaciones realizadas. La descarga completa de CORDIS y la reproducción exacta de las cifras del manuscrito no se han verificado en esta sesión. Eso no se debe presentar como validado al publicar. Conserve datos originales, fechas, hashes, filtros y entorno para reproducir el estudio.

GitHub y Zenodo publican y archivan el software; no ejecutan la interfaz como servicio web.

Documentación oficial consultada el 7 de octubre de 2026:

- https://help.zenodo.org/docs/github/describe-software/citation-file/
- https://help.zenodo.org/docs/github/enable-repository/
- https://help.zenodo.org/docs/github/archive-software/github-upload/
- https://help.zenodo.org/docs/deposit/describe-records/licenses/
