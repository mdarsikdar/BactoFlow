#!/bin/bash

# ==============================================================================
# Environment Installation Script
# ==============================================================================
# This script installs all necessary Conda environments and databases.
# Usage: bash install_environments.sh
# ==============================================================================

set -e

# Get Conda base directory
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

echo "=== Installing Pipeline Environments ==="

# 1. Install all YAML environments
for env_file in envs/*.yml; do
    env_name=$(basename "$env_file" .yml)
    if conda env list | grep -q "$env_name"; then
        echo "Environment $env_name already exists. Skipping."
    else
        echo "Creating environment $env_name from $env_file..."
        conda env create -f "$env_file"
    fi
done

# 2. Database Initialization
echo "--- Initializing Databases ---"

# ABRicate
echo "Setting up ABRicate databases..."
conda run -n abricate abricate-get_db --all --force

# MLST
echo "Setting up MLST databases..."
conda run -n mlst mlst-download_all

# PADLOC
echo "Setting up PADLOC databases..."
conda run -n padloc padloc --download

echo "=== All Environments and Databases are Ready ==="
