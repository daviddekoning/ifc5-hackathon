# IFC 5 Hackathon

This repo contains code written for the IFC 5 Hackathon in Budapest, February 5-6, 2025.

## Structure

This repo may contain multiple projects, so the base structure of the repo is as follows:

`/data`: a folder for storing reference data and files that is common across projects. e.g. json schemas, etc...

`/project-name`: a folder for project. All projects will share a single python and npm environment.

## Projects

### ifc-query
A Streamlit application that enables users to write and execute queries against IFCX-JSON files.

### usd-viewer
A web-based USD file viewer built with Flask and React.

## Setup

1. Install uv (Python dependency management):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Create and activate virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```bash
   uv pip install .
   ```
4. Install Node.js dependencies:
   ```bash
   cd usd-viewer/frontend && npm install
   ```