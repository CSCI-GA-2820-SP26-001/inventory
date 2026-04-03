# Inventory Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python_3.12-blue.svg)](https://python.org/)

A REST API service for managing inventory items. Built with Flask and SQLAlchemy.

## Overview

This service provides CRUD operations for inventory records. Each inventory item has a name, product ID, quantity on hand, restock level, and condition (`new`, `open_box`, or `used`). The `/service` folder contains the `Inventory` model and REST routes; `/tests` contains test suites for the model and service.

## Prerequisites

- Python 3.12
- Pipenv (recommended) or pip

## Setup

### Using this repo as a template

Press the **Use this template** button on GitHub to create your own repository from this template.

### Local setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd inventory
   ```

2. Copy environment configuration:
   ```bash
   cp dot-env-example .env
   ```
   Edit `.env` if needed (e.g. database URL).

3. Install dependencies:
   ```bash
   pipenv install --dev
   ```
   Or with Make:
   ```bash
   make install
   ```

4. Optional — copy hidden files if you moved files manually:
   ```bash
   cp .gitignore   ../<your_repo_folder>/
   cp .flaskenv    ../<your_repo_folder>/
   cp .gitattributes ../<your_repo_folder>/
   ```

## Running the Service

```bash
honcho start
# or
make run
```

The API will be available at the URL configured in `.flaskenv` (default typically `http://localhost:8000`).

## Development

| Command     | Description                    |
|------------|--------------------------------|
| `make install` | Install Python dependencies   |
| `make lint`    | Run flake8 and pylint         |
| `make test`    | Run pytest with coverage      |
| `make run`     | Start the service (honcho)    |
| `make secret`  | Generate a secret hex key     |

## Project Layout

```text
.gitignore          - Ignores Vagrant and other metadata
.flaskenv           - Environment variables for Flask
.gitattributes      - Line ending handling (e.g. CRLF)
.devcontainer/      - VSCode Remote Containers support
dot-env-example     - Copy to .env for local config
Pipfile             - Python dependencies (Pipenv)
Makefile            - Development and build commands

service/                    - Main service package
├── __init__.py             - Package initializer
├── config.py               - Configuration
├── models.py               - Inventory model and ItemCondition enum
├── routes.py               - REST API routes
└── common/
    ├── cli_commands.py     - Flask CLI (e.g. recreate tables)
    ├── error_handlers.py   - HTTP error handling
    ├── log_handlers.py     - Logging setup
    └── status.py           - HTTP status constants

tests/
├── __init__.py
├── factories.py            - Test factories
├── test_cli_commands.py    - CLI tests
├── test_models.py          - Model tests
└── test_routes.py          - Route tests
```

## API Summary

The service exposes a REST API to create, read, update, and delete **Inventory** records, plus **restock** (`PUT /inventory/<id>/restock` with JSON `{"amount": <positive integer>}`) to increase `quantity_on_hand`. Each record includes:

- **name** — Item name
- **product_id** — Product identifier
- **quantity_on_hand** — Current stock
- **restock_level** — Threshold for restocking
- **condition** — One of: `new`, `open_box`, `used`
- **created_at** / **last_updated** — Timestamps (managed by the service)

Use the root URL (`/`) for a simple service description. Full CRUD endpoints are defined in `service/routes.py`.

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE).

This repository is part of the New York University (NYU) course **CSCI-GA.2820-001 DevOps and Agile Methodologies**, created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
