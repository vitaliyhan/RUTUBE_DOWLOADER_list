#!/bin/bash
venv_path="download_venv"
# Activate the virtual environment
source "$venv_path/Scripts/activate"

# Run the Python script
python cuncurency_list.py 2>&1