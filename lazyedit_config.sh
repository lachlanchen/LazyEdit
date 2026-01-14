#!/bin/bash

# LazyEdit configuration file - automatically generated

# Project paths
LAZYEDIT_DIR="/home/lachlan/DiskMech/Projects/lazyedit"
LAZYEDIT_USER="lachlan"

# Python/Conda settings
CONDA_PATH="/home/lachlan/miniconda3/etc/profile.d/conda.sh"
CONDA_ENV="lazyedit"

# App settings
APP_ARGS="-m lazyedit"
SESSION_NAME="lazyedit"

# Function to activate conda
activate_conda() {
    if [ -n "$CONDA_PATH" ]; then
        source "$CONDA_PATH"
        conda activate "$CONDA_ENV" 2>/dev/null || echo "Warning: Could not activate conda environment '$CONDA_ENV'"
    else
        echo "Warning: Conda path not set. Cannot activate environment."
    fi
}
