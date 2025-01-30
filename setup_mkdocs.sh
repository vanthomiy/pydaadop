#!/bin/bash

# Create the docs folder
mkdir -p docs

# Create MkDocs configuration file
cat > mkdocs.yml <<EOL
site_name: PyDaaDop Documentation
theme:
  name: material
  features:
    - navigation.tabs

nav:
  - Home: index.md
  - Get Started: get-started.md
  - Concepts: concepts.md
  - API Documentation: api.md

plugins:
  - search
  - mkdocstrings:
      default_handler: python
EOL

# Create documentation files
cat > docs/index.md <<EOL
# Welcome to PyDaaDop

PyDaaDop is a powerful Python package for [describe functionality].

## Features
- Feature 1
- Feature 2
- Feature 3

## Installation
\`\`\`bash
pip install pydaadop
\`\`\`
EOL

cat > docs/get-started.md <<EOL
# Get Started

## Installation
Install the package using:

\`\`\`bash
pip install pydaadop
\`\`\`

## Basic Usage

\`\`\`python
from deriven_core import SomeModule

result = SomeModule.some_function()
print(result)
\`\`\`
EOL

cat > docs/concepts.md <<EOL
# Core Concepts

## Concept 1
Explain how this feature works.

## Concept 2
Explain another key concept.
EOL

cat > docs/api.md <<EOL
# API Documentation

::: deriven_core
EOL

# Create GitHub Actions workflow for deployment
mkdir -p .github/workflows
cat > .github/workflows/deploy.yml <<EOL
name: Deploy MkDocs

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install mkdocs-material mkdocstrings[python]

      - name: Deploy to GitHub Pages
        run: |
          mkdocs build
          mkdocs gh-deploy --force
EOL

echo "MkDocs setup complete. Run 'mkdocs serve' to preview locally."
