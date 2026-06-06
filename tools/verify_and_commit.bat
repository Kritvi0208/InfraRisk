@echo off
REM Verify NLP Module Installation

cd /d "c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"

echo.
echo ========================================
echo NLP Module Verification
echo ========================================
echo.

python verify_nlp.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Verification PASSED - Ready to commit
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Verification FAILED
    echo ========================================
)

pause
