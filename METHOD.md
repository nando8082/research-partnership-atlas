# Research Partnership Atlas v1.0.0 — método y límites

La V1 conserva los cálculos de la versión interna V16.

## Datos y selección

Tablas project y organization de CORDIS Horizon Europe/Horizon 2020. No hay filtro exclusivo de universidades. La unidad nacional es el país normalizado de cada participación. Los años corresponden al inicio del proyecto. «Solo años completos» excluye el año actual y futuros; no implica proyectos terminados ni cobertura exhaustiva. El filtro de países conserva proyectos con cualquiera de ellos y todos sus socios.

## Métricas

Cada proyecto genera una relación por pareja de países distintos. Su peso es un proyecto compartido, sin multiplicar por organizaciones. Solo países con vínculos entran al grafo.

- Proyectos: identificadores distintos por país.
- Participaciones: filas de organizaciones, sin deduplicación adicional.
- Organizaciones: identificadores distintos.
- Financiación: contribuciones de organizaciones; no contribución máxima del proyecto.
- Fondos/proyecto: financiación nacional / proyectos distintos; no mide retorno ni productividad.
- Coordinación: porcentaje de filas cuyo rol contiene COORD, no porcentaje de proyectos coordinados.
- Degree: centralidad normalizada de NetworkX.
- Betweenness: normalizada y sin ponderación.
- PageRank/eigenvector: ponderados por proyectos compartidos; eigenvector puede faltar si falla.
- HHI: suma de cuadrados de proporciones de colaboración con socios.
- Diversificación: 1 − HHI, indefinida sin socios.
- Persistencia bilateral: años distintos de inicio compartidos; no exige continuidad. Media y máximo nacionales sobre relaciones.
- Comunidades: Louvain con semilla 42; alternativa greedy modularity.
- Densidad: NetworkX sobre países con vínculos.
- Gini: fórmula estándar sobre fondos nacionales no negativos y no ausentes; indefinido si no hay fondos positivos.

## Tiempo, agregaciones y faltantes

El total anual suma proyectos nacionales. Un proyecto multinacional cuenta una vez por país. El indicador superior Projects sí cuenta proyectos únicos. Las dos series de la figura 1 se normalizan por su propio máximo, multiplicado por 100.

Los fondos se asignan al año de inicio, sin distribuirlos entre años de ejecución. No representan desembolsos efectivos. Las métricas nacionales usan min_count=1: todos los importes ausentes producen NaN. Las sumas anuales/consorcios pueden devolver cero si todos faltan; el total superior sustituye ausentes por cero al sumar. No hay imputación de registros, pero estas agregaciones no siempre distinguen ausencia de cero.

Códigos inválidos no entran a métricas nacionales. Se conservan raw_country y country_valid. Sus filas pueden seguir contando en participaciones, tamaños de consorcio y totales financieros.

El CSV analizado tiene una fila por participación y repite métricas nacionales: no deben sumarse nuevamente. La auditoría registra ensamblaje de datos; con caché no garantiza una descarga nueva.

## Estadística

Spearman (figura 8): siete indicadores, eliminación de ausentes por pares y mínimo ocho países. Benjamini–Hochberg ajusta comparaciones; estrellas q < 0.05 y q < 0.01. Constantes pueden dar resultados indefinidos. La correlación de la figura 7 no pertenece a ese ajuste.

PCA: diez indicadores estandarizados, casos completos, mínimo seis países y dos componentes. KMeans: ocho indicadores, casos completos, mínimo ocho países, semilla 42, 30 inicializaciones y k de 2 a min(6,n−2), elegido por silhouette máximo. Los grupos se dibujan sobre PCA; no tienen interpretación sustantiva automática. Atípicos y redundancias pueden influir.

La figura 4 muestra hasta 36 países. La ECDF de consorcios usa raíz cuadrada y percentiles en conteos originales. La figura 11 selecciona ocho países por participaciones. La figura 12 muestra fracciones de vínculos y volumen con al menos t años activos; no es Kaplan–Meier ni corrige censura.

La ontología es fija, conceptual y no validada por esos cálculos. No se establecen relaciones causales ni se generan datos de reemplazo al fallar CORDIS. PDF no tiene una configuración de 800 DPI.
