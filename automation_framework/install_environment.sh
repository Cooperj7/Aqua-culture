#!/bin/bash

# Create the virtual environment
python3 -m venv venv-framework

# Activate the environment
. venv-framework/bin/activate

# Upgrade pip itself
pip install --upgrade pip
# Install the required packages
pip install -r requirements.txt