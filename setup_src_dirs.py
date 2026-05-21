import os
import sys

# Create src/models directory
src_models = os.path.join(os.getcwd(), "src", "models")
os.makedirs(src_models, exist_ok=True)
print(f"Created directory: {src_models}")
