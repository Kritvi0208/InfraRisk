"""Quick test runner for NLP module"""
import sys
sys.path.insert(0, r'c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI')

# Run tests
if __name__ == "__main__":
    from src.nlp.test_nlp import run_tests
    success = run_tests()
    sys.exit(0 if success else 1)
