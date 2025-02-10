#!/usr/bin/env python3
"""
Standalone API Hook Script

This script does the following:
1. Scans src/pydaadop for Python files (ignoring __init__.py)
2. Creates a corresponding Markdown file in docs/api for each module, with content like:
      ::: pydaadop.x.y.z
3. Builds a nested navigation structure based on the docs/api folder.
4. Reads the existing mkdocs.yml, replaces (or appends) the API Documentation nav entry,
   and writes the updated configuration to mkdocs.generated.yml.

Usage:
    python docs/plugins/auto_api.py

Then build or serve MkDocs with:
    mkdocs serve -f mkdocs.generated.yml
    mkdocs build -f mkdocs.generated.yml
"""

import os
from pathlib import Path
import yaml

# Directories and files
SRC_DIR = Path("src/pydaadop")
DOCS_API_DIR = Path("docs/api")
MKDOCS_YML = Path("mkdocs.yml")
GENERATED_MKDOCS_YML = Path("mkdocs.generated.yml")


def generate_api_md_files():
    """
    Walk through SRC_DIR, and for each Python file (except __init__.py),
    create/update a Markdown file in DOCS_API_DIR that contains an mkdocstrings
    directive referencing the module.
    """
    print("Deleting existing API Markdown files...")
    for md_file in DOCS_API_DIR.rglob("*.md"):
        md_file.unlink()

    print("Generating API Markdown files...")
    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Compute module import path (e.g. "pydaadop.x.y.z")
        rel_path = py_file.relative_to(SRC_DIR)
        module_parts = list(rel_path.with_suffix("").parts)
        module_reference = ".".join(["pydaadop"] + module_parts)

        # Determine the destination Markdown file, preserving the directory structure
        md_file = DOCS_API_DIR / rel_path.with_suffix(".md")
        md_file.parent.mkdir(parents=True, exist_ok=True)

        # Write the mkdocstrings directive into the Markdown file
        content = f"::: {module_reference}\n"
        md_file.write_text(content, encoding="utf-8")
        print(f"  Created {md_file} referencing module {module_reference}")


def build_nav_structure(root: Path):
    """
    Recursively build a navigation structure (a list of dictionaries) from the folder
    structure rooted at 'root'. The paths will be relative to the docs/ folder.
    """
    nav_items = []
    for item in sorted(root.iterdir(), key=lambda x: x.name):
        if item.is_dir():
            subnav = build_nav_structure(item)
            if subnav:
                nav_items.append({item.name: subnav})
        elif item.is_file() and item.suffix == ".md":
            # Get path relative to docs/ and normalize for YAML
            rel_path = item.relative_to(Path("docs"))
            nav_items.append({item.stem: str(rel_path).replace(os.sep, "/")})
    return nav_items


def update_mkdocs_nav(api_nav):
    """
    Load mkdocs.yml, update (or append) the "API Documentation" nav entry with the
    generated navigation structure (api_nav), and write the updated config to a new file.
    """
    print("Updating MkDocs navigation configuration...")
    with MKDOCS_YML.open("r", encoding="utf-8") as f:
        # Use FullLoader to handle python-specific tags
        config = yaml.load(f, Loader=yaml.FullLoader)

    nav = config.get("nav", [])
    new_nav = []
    api_section_found = False

    for item in nav:
        if isinstance(item, dict) and "API Documentation" in item:
            new_nav.append({"API Documentation": api_nav})
            api_section_found = True
            print("  Replaced existing 'API Documentation' entry.")
        else:
            new_nav.append(item)

    if not api_section_found:
        new_nav.append({"API Documentation": api_nav})
        print("  Appended new 'API Documentation' entry.")

    config["nav"] = new_nav

    with GENERATED_MKDOCS_YML.open("w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"Updated MkDocs configuration written to {GENERATED_MKDOCS_YML}")



def main():
    print("Running standalone API hook script...")
    generate_api_md_files()
    api_nav = build_nav_structure(DOCS_API_DIR)
    update_mkdocs_nav(api_nav)
    print("Done.")

print("Running standalone API hook script...")
main()
