# Advanced Print Engine — Environment Setup & Tracking

This file tracks every dependency, command, and configuration applied to the bench environment to run the Advanced Print Engine successfully.

## 1. App Creation & Installation
- **App Name**: `advanced_print_engine`
- **Created via**: `bench new-app advanced_print_engine`
- **Installed on Site**: `test` via `bench --site test install-app advanced_print_engine`

## 2. Python Dependencies
The app utilizes Playwright for headless browser measurements and WeasyPrint for backend HTML-to-PDF compilation.
- **Packages Tracked**: `playwright`, `weasyprint` added to `requirements.txt` and `pyproject.toml`.
- **Installation Command**:
  ```bash
  ./env/bin/pip install -r apps/advanced_print_engine/requirements.txt
  ```

## 3. Playwright Browser Binaries
Playwright requires local browser binaries (Chromium) to execute headless rendering.
- **Binary Installation Command**:
  ```bash
  ./env/bin/playwright install chromium
  ```
- **Binaries Cached Location**: `/home/avasar/.cache/ms-playwright/`

## 4. System Utilities & Shared Libraries
To support PDF rendering and high-resolution diagnostic image generation, the following system libraries must be installed on the host OS:

- **PDF/Image Converters**:
  ```bash
  sudo apt update
  sudo apt install -y poppler-utils ghostscript
  ```

- **WeasyPrint Layout & Font rendering library dependencies**:
  ```bash
  sudo apt install -y shared-mime-info libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
  ```

## 5. Troubleshooting & Notes
- Ensure system dependencies for Chromium (like `libgbm1`, `libnss3`, `libatk-bridge2.0-0`, etc.) are present on the host container/system if rendering fails with shared library errors.
