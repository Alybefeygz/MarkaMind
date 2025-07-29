#!/bin/bash
echo "Activating MarkaMind virtual environment..."
source venv/Scripts/activate
echo
echo "Virtual environment activated!"
echo "Python version:"
python --version
echo
echo "Pip version:"
pip --version
echo
echo "Python location:"
which python 2>/dev/null || where python
echo
echo "You can now install dependencies with: pip install -r requirements.txt"
bash