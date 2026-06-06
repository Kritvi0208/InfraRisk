"""InfraRisk AI package."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (
    ROOT / "src" / "core",
    ROOT / "src" / "nlp",
    ROOT / "src" / "models",
    ROOT / "src" / "p3",
    ROOT / "src" / "p5",
)

for source_dir in reversed(SOURCE_DIRS):
    source_path = str(source_dir)
    if source_dir.exists() and source_path not in sys.path:
        sys.path.insert(0, source_path)
