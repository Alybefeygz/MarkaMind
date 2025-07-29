@echo off
echo Activating MarkaMind virtual environment...
call venv\Scripts\activate.bat
echo.
echo Virtual environment activated!
echo Python version:
python --version
echo.
echo Pip version:
pip --version
echo.
echo Python location:
where python
echo.
echo You can now install dependencies with: pip install -r requirements.txt
cmd /k