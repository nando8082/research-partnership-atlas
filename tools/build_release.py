"""Build a source archive from an explicit list; never include local caches."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "app.py", "analytics.py", "ontology.py", "cordis_real_seed.csv",
    "FUENTES_CORDIS.csv", "requirements.txt",
    "README.md", "METHOD.md", "VERSION.txt",
    "CHANGELOG.md", "DATA_PROVENANCE.md", "PUBLICATION.md", "VALIDATION.md",
    ".gitignore", ".gitattributes", "RELEASE_NOTES.md", "tests/test_app.py", ".github/workflows/checks.yml",
    "tools/build_release.py",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    files = list(FILES)
    for name in ("LICENSE", "CITATION.cff"):
        p = ROOT / name
        if not p.is_file():
            parser.error(f"Missing {name}; complete authorship and license first.")
        if "PENDIENTE" in p.read_text(encoding="utf-8"):
            parser.error(f"Unresolved metadata in {name}.")
        files.append(name)
    missing = [f for f in files if not (ROOT / f).is_file()]
    if missing:
        parser.error("Missing files: " + ", ".join(missing))
    stem = "research-partnership-atlas-v1.0.0"
    target = ROOT / "dist" / (stem + ".zip")
    target.parent.mkdir(exist_ok=True)
    manifest = []
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in files:
            data = (ROOT / name).read_bytes()
            archive.writestr(stem + "/" + name, data)
            manifest.append(hashlib.sha256(data).hexdigest() + "  " + name)
        archive.writestr(stem + "/SHA256SUMS.txt", "\n".join(manifest) + "\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".zip.sha256").write_text(digest + "  " + target.name + "\n", encoding="utf-8")
    print(target)
    print("SHA256:", digest)


if __name__ == "__main__":
    main()
