#!/usr/bin/env python
"""Create Phase 4 NLP directory structure."""

import os
import sys


def create_directories():
    """Create src/nlp directory structure."""
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Create directories
    dirs = [
        os.path.join(base_path, "src"),
        os.path.join(base_path, "src", "nlp"),
        os.path.join(base_path, "tests"),
        os.path.join(base_path, "tests", "nlp"),
    ]

    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created: {dir_path}")

    # Create __init__.py files
    init_files = [
        os.path.join(base_path, "src", "__init__.py"),
        os.path.join(base_path, "src", "nlp", "__init__.py"),
        os.path.join(base_path, "tests", "__init__.py"),
        os.path.join(base_path, "tests", "nlp", "__init__.py"),
    ]

    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write('"""InfraRisk AI NLP Module."""\n')
            print(f"✓ Created: {init_file}")

    print("\n✓ Directory structure created successfully!")


if __name__ == "__main__":
    create_directories()
