# Research Partnership Atlas v1.0.0

Aplicación Python/Streamlit para explorar colaboración internacional y financiación de investigación en CORDIS Horizon Europe y Horizon 2020. Primera versión pública preparada a partir de la versión interna V16: doce figuras analíticas, ontología conceptual, indicadores nacionales y exportaciones CSV/PDF.

**Estado:** distribución local v1.0.0 preparada para subir a GitHub y Zenodo. Autores: Daniel Pinargo y Daniel Lopez. Titular: Daniel Pinargo. Licencia: MIT. Nombre público: Research Partnership Atlas. No se ha asignado un DOI. Consulte [PUBLICATION.md](PUBLICATION.md).

## Instalación

Se recomienda Python 3.11 en un entorno separado. Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

En Linux/macOS use `.venv/bin/python`. `requirements.txt` fija las versiones directas usadas en las comprobaciones; no es un bloqueo de todas las dependencias transitivas. Consulte [VALIDATION.md](VALIDATION.md).

### Anaconda

Desde Anaconda Prompt, entre a la carpeta del proyecto y ejecute:

```text
conda create -n research_partnership_atlas python=3.11 -y
conda activate research_partnership_atlas
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Para cerrar use Ctrl+C. Para reabrir, active el entorno, entre a la carpeta y vuelva a ejecutar Streamlit.

Kaleido 1 necesita Chrome/Chromium para PDF. Puede instalar Chrome mediante plotly_get_chrome en el entorno elegido: [documentación](https://plotly.com/python/static-image-export/). Instale Times New Roman para conservar la tipografía solicitada; el renderizador puede sustituirla si falta. No se distribuye esa fuente.

## Uso

1. Abra la dirección de Streamlit, normalmente http://localhost:8501.
2. Seleccione ES/EN, HORIZON/H2020 y pulse la descarga completa.
3. Ajuste años, regiones y países.
4. Explore las cinco pestañas y descargue resultados.

La muestra de cinco proyectos no incluye participaciones y no habilita análisis. La descarga completa requiere Internet. Se reutiliza una descarga durante seis horas. Cambiar programas requiere pulsar otra vez el botón. ES/EN tiene traducción parcial.

El filtro de países conserva proyectos con cualquiera de los países seleccionados y todas sus organizaciones, incluidos socios extranjeros. Elegir Ecuador no restringe todas las métricas a Ecuador.

## Figuras y archivos

| Figura | Resultado |
| --- | --- |
| 1 | Trayectoria anual normalizada de proyectos por país y financiación |
| 2 | Proyectos, financiación, socios y diversificación |
| 3 | Diversificación frente a persistencia |
| 4 | Matriz de colaboración ordenada por comunidades |
| 5 | Lorenz y Gini |
| 6 | Distribución acumulada del tamaño de consorcios |
| 7 | Coordinación y financiación por proyecto |
| 8 | Spearman con ajuste FDR |
| 9 | PCA |
| 10 | KMeans representado en PCA |
| 11 | Trayectorias de ocho países con más participaciones |
| 12 | Umbrales de persistencia bilateral |
| 13 | Ontología conceptual fija |

Descargas: research_partnership_atlas_analysed_cordis_v1.csv, country_metrics_v1.csv, pair_persistence_v1.csv, pca_loadings_v1.csv (si existe PCA) e research_partnership_atlas_v1_english_figures_pdf.zip. El ZIP contiene trece PDF en inglés y manifest_figures_en.csv. Las columnas se conservan; analysis_version identifica 1.0.0.

## Método y reproducibilidad

Lea [METHOD.md](METHOD.md). Los resultados son descriptivos, no causales. El análisis incluye entidades de varios tipos y agrupa por país. El total anual suma conteos nacionales de proyectos, mientras el indicador superior cuenta proyectos únicos. La financiación se asigna al año de inicio; la persistencia cuenta años de inicio distintos, aunque no sean consecutivos. El CSV analizado repite métricas nacionales en cada participación.

Los datos completos no se distribuyen aquí. Para repetir un estudio conserve originales, fechas, hash, programas, filtros, versión y entorno. CORDIS puede cambiar. Consulte [DATA_PROVENANCE.md](DATA_PROVENANCE.md).

## Estructura y verificación

app.py contiene interfaz, descarga y exportaciones; analytics.py calcula indicadores; ontology.py define el esquema conceptual. La muestra y el inventario son cordis_real_seed.csv y FUENTES_CORDIS.csv.

```powershell
python -m unittest discover -s tests -v
```

Consulte VALIDATION.md para el alcance real de las comprobaciones.

## Autoría, licencia y cita

Autores del software: **Daniel Pinargo y Daniel Lopez**. Titular de derechos: **Daniel Pinargo**. El código y la documentación propia se distribuyen bajo [MIT](LICENSE). Los datos externos conservan sus condiciones y atribuciones; consulte DATA_PROVENANCE.md.

La referencia del software está en [CITATION.cff](CITATION.cff). Solicitamos citar la versión utilizada en investigaciones. MIT exige conservar el aviso de derechos y licencia; no impone una cita bibliográfica. El DOI se incorporará después de su asignación.

El software implementa el marco analítico del manuscrito *Strengthening International University Collaboration through Resilient Research Funding Network Analytics for Strategic Diversification and Sustained Research Partnerships*. La autoría del artículo y las contribuciones al marco conceptual se documentan en el manuscrito; son distintas de los metadatos de este software.

GitHub publica código y Zenodo archiva software con DOI. Para ejecutar la interfaz públicamente se necesita alojamiento adicional.
