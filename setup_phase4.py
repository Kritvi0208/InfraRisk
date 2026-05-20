import os
import sys

base_path = os.path.dirname(os.path.abspath(__file__))
dirs_to_create = [
    "src/nlp",
    "tests",
    "docs",
    "examples",
    "data/benchmarks",
]

for dir_path in dirs_to_create:
    full_path = os.path.join(base_path, dir_path)
    os.makedirs(full_path, exist_ok=True)
    print(f"Created: {full_path}")

print("All directories initialized successfully!")
