@echo off
setlocal enabledelayedexpansion

cd /d "C:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"

REM Create directory structure
for %%D in (backend\app\api backend\app\models backend\app\services backend\app\utils frontend\src\components frontend\src\pages frontend\src\services docs data data\cache src\data src\models notebooks tests) do (
    if not exist "%%D" mkdir "%%D"
    echo Created: %%D
)

echo All directories created successfully!
pause
