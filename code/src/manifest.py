"""Write results/MANIFEST.json: what produced the results and their checksums.

Run as `python -m src.manifest` after `python -m src.experiments`. The report's
reproducibility appendix quotes this file.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ("numpy", "scipy", "networkx", "pandas", "matplotlib", "pyyaml")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=CODE_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def _git_dirty() -> bool | None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", ".", ":!results/MANIFEST.json"],
            cwd=CODE_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return bool(result.stdout.strip())


def build_manifest(root: Path = CODE_ROOT) -> dict:
    results = sorted(
        path for path in (root / "results").rglob("*") if path.is_file() and path.name != "MANIFEST.json"
    )
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_head": _git_head(),
        "git_dirty": _git_dirty(),  # True means results may not match the commit
        "python": platform.python_version(),
        "packages": {name: metadata.version(name) for name in PACKAGES},
        "configs": {
            path.name: _sha256(path) for path in sorted((root / "configs").glob("*.yaml"))
        },
        "results": {str(path.relative_to(root)): _sha256(path) for path in results},
    }


def main() -> None:
    manifest = build_manifest()
    target = CODE_ROOT / "results" / "MANIFEST.json"
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
    print(f"wrote {target} ({len(manifest['results'])} result files)")


if __name__ == "__main__":
    main()
