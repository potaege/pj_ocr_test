@echo off
set VENV_DIR=.venv

echo ===============================
echo  Creating virtual environment
echo ===============================

if not exist %VENV_DIR% (
    python -m venv %VENV_DIR%
)

echo ===============================
echo  Installing requirements
echo ===============================

call %VENV_DIR%\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ===============================
echo  DONE!
echo ===============================
echo Activate venv with:
echo    %VENV_DIR%\Scripts\activate

echo This window will close automatically in 5 seconds...
timeout /t 5 > nul
exit