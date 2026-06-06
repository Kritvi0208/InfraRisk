"""Import-path compatibility for the organized InfraRiskAI layout.

Python imports this module automatically when commands are run from the
project root. It keeps legacy root-style imports working after the source files
were moved into src/core, src/nlp, src/models, src/p3, and src/p5.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
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
