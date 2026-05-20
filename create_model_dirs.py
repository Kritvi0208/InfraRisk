import os
import sys

# Create directory structure
base = r"c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"
src_dir = os.path.join(base, "src", "models")
os.makedirs(src_dir, exist_ok=True)
print(f"Created: {src_dir}")
