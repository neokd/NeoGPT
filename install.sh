#!/bin/bash

# Check if Python is installed
if command -v python3 &>/dev/null; then
    # Get the version information
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

    # Check if the version is greater than or equal to 3.10
    if [[ "$(printf '%s\n' "3.10" "$python_version" | sort -V | head -n1)" == "3.10" ]]; then
        echo "Python version is greater than or equal to 3.10. Proceeding with the script..."
        if command -v conda &>/dev/null; then
            echo "Anaconda installed. Proceeding to environment setup..."
            # Create a new Conda environment and specify the python version, for example, 'neogpt-env'
            conda create --name neogpt-env python=$python_version
            conda activate neogpt-env
        fi
        pip install -r requirements.txt
        python neogpt/builder.py
        python main.py
    else
        echo "Python version is less than 3.10. Please upgrade Python to version 3.10 or later."
    fi
else
    echo "Python is not installed. Please install Python version 3.10 or later."
fi
