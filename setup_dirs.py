"""Create directory structure for InfraRisk AI ML Models."""

import os
from pathlib import Path

base_path = Path(r"c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI")

directories = [
    "src/models",
    "src/data",
    "tests",
    "examples",
    "notebooks",
    "docs",
]

for dir_name in directories:
    dir_path = base_path / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Created/Verified: {dir_path}")

print("\n✅ Directory structure ready!")
