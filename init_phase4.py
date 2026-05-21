#!/usr/bin/env python3
"""Setup script to create Phase 4 NLP directories and files"""

import json
import os
import sys
from pathlib import Path

# Get current directory
cwd = os.getcwd()
print(f"Working directory: {cwd}")

# Create directories
dirs = [
    "src",
    "src/nlp",
    "tests",
    "docs",
    "examples",
    "data",
    "data/benchmarks",
]

for dir_path in dirs:
    full_path = os.path.join(cwd, dir_path)
    Path(full_path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {full_path}")

print("\n✓ All directories created successfully!")
print(f"\nDirectory structure:")
for root, dirs_list, files in os.walk("src"):
    level = root.replace("src", "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
