# Advanced Print Engine — Environment Setup & Tracking

This file tracks every dependency, command, and configuration applied to the bench environment to run the Advanced Print Engine successfully.

## 1. App Creation & Installation
- **App Name**: `advanced_print_engine`
- **Created via**: `bench new-app advanced_print_engine`
- **Installed on Site**: `test` via `bench --site test install-app advanced_print_engine`

## 2. Python Dependencies
The app utilizes Playwright for headless browser PDF rendering.
- **Package Tracked**: `playwright` added to `requirements.txt` and `pyproject.toml`.
- **Installation Command**:
  ```bash
  uv pip install playwright --python ./env/bin/python
  ```

## 3. Playwright Browser Binaries
Playwright requires local browser binaries (Chromium) to execute headless rendering.
- **Binary Installation Command**:
  ```bash
  ./env/bin/playwright install chromium
  ```
- **Binaries Cached Location**: `/home/avasar/.cache/ms-playwright/`

## 4. Troubleshooting & Notes
- Ensure system dependencies for Chromium (like `libgbm1`, `libnss3`, `libatk-bridge2.0-0`, etc.) are present on the host container/system if rendering fails with shared library errors.
