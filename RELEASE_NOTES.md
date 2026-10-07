# Research Partnership Atlas v1.0.0

First public distribution of Research Partnership Atlas, a Python/Streamlit application developed by Daniel Pinargo and Daniel Lopez to implement the analytical framework of the associated international research collaboration study.

The software processes official CORDIS Horizon Europe and Horizon 2020 project and organisation records to explore country-level research funding, collaboration networks, geographic diversification, coordination and partnership persistence. It provides twelve analytical figures, an additional conceptual ontology, country and bilateral metrics, PCA and KMeans analysis, CSV exports and an English PDF figure package.

The public version preserves the analytical implementation of the internal INTER V16 development version. It includes installation instructions, pinned direct dependencies, methodological definitions and limitations, data attribution, software citation metadata and automated checks.

Software and original documentation: MIT License.
Copyright (c) 2026 Daniel Pinargo.
Software authors: Daniel Pinargo and Daniel Lopez.
Third-party CORDIS data retain their own attribution and reuse conditions.

Validation includes five automated checks, seed-interface startup in ES/EN, construction of thirteen figures in both languages, PDF package export and CFF schema validation. Full CORDIS download and exact reproduction of the associated manuscript's reported values have not been verified in this preparation session. See VALIDATION.md and METHOD.md.

The bundled five-project sample does not enable the analytical results. Internet access is needed to download the full datasets. PDF export requires Chrome/Chromium with Kaleido 1; the requested Times New Roman font must be installed for matching typography.

This release archives the software. A reproducible study also requires the specific data snapshot, filters and environment used to generate its results.
