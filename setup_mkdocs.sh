#!/bin/bash

# Exit on error
set -e

echo "🔧 Setting up MkDocs in pydaadop..."

# 1️⃣ Install MkDocs & Plugins
pip install mkdocs mkdocs-material mkdocstrings[python]

# 2️⃣ Initialize MkDocs in `pydaadop`
mkdocs new docs

# 3️⃣ Modify mkdocs.yml
cat > mkdocs.yml <<EOL
site_name: PyDaaDop Documentation
theme:
  name: material
  features:
    - navigation.tabs

nav:
  - Get Started: docs/get-started.md
  - Concepts: docs/concepts.md
  - API Documentation: docs/api.md

plugins:
  - search
  - mkdocstrings:
      default_handler: python

EOL

# 4️⃣ Create Documentation Pages
mkdir -p docs
echo "# Get Started" > docs/get-started.md
echo "# Concepts" > docs/concepts.md
echo -e "# API Documentation\n\n::: pydaadop" > docs/api.md

# 5️⃣ Set Up GitHub Actions for Automatic Deployment
mkdir -p .github/workflows
cat > .github/workflows/deploy.yml <<EOL
name: Deploy MkDocs to GitHub Pages

on:
  push:
    branches:
      - main  # Change if needed

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install mkdocs mkdocs-material mkdocstrings[python]

      - name: Build and deploy
        run: |
          mkdocs gh-deploy --force
EOL

# 6️⃣ Commit and Push Changes
git add .
git commit -m "Setup MkDocs documentation with GitHub Pages"
git push origin main  # Adjust branch if needed

echo "✅ MkDocs setup complete! Docs will deploy via GitHub Pages."
