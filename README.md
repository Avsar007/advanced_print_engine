### Advanced Print Engine

Advanced PDF print rendering engine using Playwright

### Installation

#### 1. Get and Install the App
You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO
bench install-app advanced_print_engine
```

#### 2. Python Dependencies
The app utilizes Playwright for PDF rendering. It is listed as a dependency in `pyproject.toml` and `requirements.txt`, which will be installed automatically by `bench get-app`. 

If you need to install it manually inside the bench virtual environment:
```bash
./env/bin/pip install playwright
```

#### 3. Playwright Browser Binaries
Playwright requires headless Chromium binaries. Run the following command from your bench directory to download and cache them:
```bash
./env/bin/playwright install chromium
```

#### 4. System/OS Dependencies
To run headless Chromium, your system must have the required shared libraries (such as `libgbm`, `libnss3`, etc.). You can install them automatically using Playwright:
```bash
# Install system dependencies for Chromium
./env/bin/playwright install-deps chromium

# Note: On some Linux systems, you might need root privileges:
sudo ./env/bin/playwright install-deps chromium
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/advanced_print_engine
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
