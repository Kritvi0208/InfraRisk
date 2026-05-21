#!/usr/bin/env python3
"""Setup script to create directory structure and initialize models."""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """Create all necessary directories."""
    base_path = Path(__file__).parent

    directories = [
        "src",
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
        print(f"✓ {dir_path}")

    return base_path


def create_init_files(base_path: Path):
    """Create __init__.py files."""
    packages = [
        "src",
        "src/models",
        "src/data",
        "tests",
    ]

    for package in packages:
        init_file = base_path / package / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""InfraRisk AI Package."""\n')
            print(f"✓ {init_file}")


if __name__ == "__main__":
    try:
        print("🔧 Creating directory structure...")
        base_path = create_directory_structure()

        print("\n📦 Creating __init__.py files...")
        create_init_files(base_path)

        print("\n✅ Setup complete!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
