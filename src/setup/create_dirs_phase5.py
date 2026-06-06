import os
import sys

# Create directories
base_path = r"c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"
sim_path = os.path.join(base_path, "src", "simulation")
dash_path = os.path.join(base_path, "src", "dashboard")

os.makedirs(sim_path, exist_ok=True)
os.makedirs(dash_path, exist_ok=True)

print(f"Created {sim_path}")
print(f"Created {dash_path}")
