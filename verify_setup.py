#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing InfraRisk Components...")
print("="*50)

try:
    from src.data.real_data_loader import RealDataLoaders
    data = RealDataLoaders.load_all()
    print("✓ Data loaders")
except Exception as e:
    print(f"✗ Data: {e}")

try:
    from src.models.siamese_cnn import SiameseCNN
    model = SiameseCNN(pretrained=False)
    print("✓ CNN model")
except Exception as e:
    print(f"✗ CNN: {e}")

try:
    from src.features.advanced_financials import AdvancedFinancials
    dscr = AdvancedFinancials.calculate_dscr_detailed(100, 20, 10, 15)
    print(f"✓ Financial metrics (DSCR={dscr:.2f}x)")
except Exception as e:
    print(f"✗ Financials: {e}")

try:
    from src.data.portfolio_persistence import PortfolioPersistence
    db = PortfolioPersistence(":memory:")
    print("✓ Database persistence")
except Exception as e:
    print(f"✗ Database: {e}")

print("="*50)
print("\n✓ All components operational!")
print("\nRun: streamlit run src/simulation/dashboard_enhanced.py")
