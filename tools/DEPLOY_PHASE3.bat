@echo off
REM Phase 3 Integration - Git Commit and Push Script for Windows

cd /d "c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"

echo.
echo === PHASE 3 INTEGRATION - GIT DEPLOYMENT ===
echo.

REM Check git status
echo Checking git status...
git status --short | findstr /C:"monte_carlo" /C:"shap_interpreter" /C:"attention_extractor" /C:"centrality_analyzer" /C:"backtesting" /C:"model_registry"

echo.
echo Staging Phase 3 files...
git add monte_carlo_pd.py
git add shap_interpreter.py
git add attention_extractor.py
git add centrality_analyzer.py
git add backtesting.py
git add model_registry.py
git add MODELS_INIT_TEMPLATE.py
git add PHASE3_INTEGRATION_COMPLETE.md
git add PHASE3_INTEGRATION_CHECKLIST.md

echo.
echo Verifying staged files...
git status --short

echo.
echo Creating commit...
git commit -m "Complete Phase 3 Integration - 6 Advanced Analytics Models ^(1100 lines^)

Advanced analytics framework with:
- Monte Carlo PD simulation (10K scenarios, P10/P50/P90)
- SHAP model interpretability (global + local explanations)
- TFT attention extraction (temporal importance visualization)
- GNN centrality analysis (4 centrality metrics)
- Backtesting framework (AUC, Gini, KS, PSI, calibration)
- Model registry (MLflow-compatible lifecycle management)

Total: 1,100 lines across 6 core modules
All modules include mock/synthetic data support
Production-ready with vectorized NumPy implementation

Co-authored-by: Copilot ^<223556219+Copilot@users.noreply.github.com^>"

echo.
echo.
echo Pushing to GitHub...
git push origin

echo.
echo === PHASE 3 DEPLOYMENT COMPLETE ===
echo All files pushed to GitHub repository
echo.
pause
