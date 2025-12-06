#!/bin/bash
# Helper script to install packages in virtualenv without --user flag

if [ -z "$1" ]; then
    echo "Usage: ./install_package.sh <package-name>"
    echo "Example: ./install_package.sh pygame"
    exit 1
fi

# Check if venv exists
if [ -d ".venv" ]; then
    echo "Installing $1 in virtual environment..."
    .venv/bin/pip install "$@"
else
    echo "Virtual environment not found. Using system pip..."
    python3 -m pip install "$@"
fi

