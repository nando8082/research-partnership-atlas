# Validation — Research Partnership Atlas v1.0.0

Local checks on 2026-10-07, Windows / Anaconda Python 3.13.9.
Direct dependency versions are recorded in requirements.txt.
pycountry 24.6.1 was installed only under .release-check/deps for these checks;
the global Anaconda environment was not modified.

## Completed

- Syntax validation for app.py, analytics.py and ontology.py.
- analytics.py and ontology.py are byte-identical to the internal V16 copies.
- AST comparison: analytical app functions are unchanged. Public labels, the download User-Agent,
  version identifiers and download filenames were updated.
- Five unittest checks passed: project-level bilateral weights and persistence;
  country funding, coordination and isolated countries; documented annual counts;
  public version; Streamlit seed startup and ES/EN language switching.
- All thirteen figures were constructed and serialized in both ES and EN with
  test fixtures. The English ZIP was generated successfully and checked for
  thirteen PDF files (PDF headers verified) plus manifest_figures_en.csv.
  This checks export execution, not visual quality or installed font fidelity.

Test fixtures are artificial inputs used only by tests, never application data.
The full CORDIS download and all populated-interface interactions have not been
verified in this session. Python 3.11 / Linux is configured in GitHub Actions but
has not been executed here. No complete fresh-environment installation was run.

## Publication status

Authors: Daniel Pinargo and Daniel Lopez. Rights holder: Daniel Pinargo.
Software license: MIT. CITATION.cff contains these confirmed metadata.
Public name: Research Partnership Atlas. No GitHub push, release or Zenodo upload was made.

Build the source archive with:

```text
python tools/build_release.py
```

The builder uses an explicit source list and includes SHA256SUMS.txt. It excludes
caches, environments, verification copies, Git internals and generated results.
The final command refuses to build without LICENSE and CITATION.cff. It does not
replace CFF schema validation or the publication checks in PUBLICATION.md.

## Final metadata checks

After selecting Research Partnership Atlas and MIT, the five tests passed again.
CITATION.cff validated against the official CFF 1.2.0 JSON schema.
The source ZIP includes LICENSE and CITATION.cff; archive integrity and all
SHA-256 manifest entries were verified. Application calculations remain unchanged.

## Distribution cleanup

The two dependency files were consolidated into requirements.txt with pinned
direct versions. Anaconda instructions are included in README.md. Packaging and
GitHub Actions use that same dependency file. Generated files and local
verification tools are excluded from the source distribution.

After dependency consolidation, all five tests passed again. Syntax, local
Markdown links, removed-file references and Git exclusions were checked.
Byte and AST comparisons confirmed that analytical modules and calculations
remain unchanged from the internal development baseline.
