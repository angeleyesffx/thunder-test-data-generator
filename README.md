# Thunder Test Data Generator

### ⚡ Automated Test Data Engineering & Synthetic Data Provisioning

`thunder-test-data-generator` is a config-driven Python CLI that generates synthetic test data by calling REST APIs. Built for QA teams working with services behind a middleware relay, it eliminates manual data provisioning while keeping secrets out of source control.

Key characteristics:
- **Config-driven:** YAML-based configuration for environments, countries, services, and API endpoints
- **Locale-aware fake data:** Faker integration with `pt_BR`, `en_US`, `es_MX`, and 20+ other locales
- **Jinja2 templating:** Request bodies built from parameterised templates
- **Parallel execution:** ThreadPoolExecutor for concurrent requests
- **Two execution modes:** Debug (inspect payloads) and Execution (fire requests)

---

## Requirements

- Python 3.8+
- pip

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
make install
# or: pip install -r requirements.txt
```

### 3. Configure secrets

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your auth tokens and API keys. This file is `.gitignore`d — never commit it.

### 4. Configure your environment

Copy the example config and adapt it to your target APIs:

```bash
cp config.example.yml config.yml
```

See `config.example.yml` for a fully documented reference with all supported options.

---

## Running

### Debug Mode (default — no requests sent)

Use this to verify that Thunder is building payloads correctly before sending anything.

```bash
make debug
# or:
python main.py -CONFIG_YAML config -ENV sit
```

### Execution Mode (`-e` flag — requests are sent)

```bash
make run
# or:
python main.py -CONFIG_YAML config -ENV sit -e
```

### CLI Reference

| Flag | Description |
|------|-------------|
| `-CONFIG_YAML <name>` | YAML config file to load (without `.yml`). Defaults to `config`. |
| `-ENV <env>` | Environment key inside the config (e.g. `sit`, `dev`, `uat`). Defaults to `sit`. |
| `-COUNTRIES <list>` | Comma-separated country codes to run (e.g. `br,ar`). Defaults to all configured. |
| `-services <list>` | Comma-separated services to run. Defaults to all configured. |
| `-METHODS <list>` | Comma-separated HTTP methods to run (e.g. `post,put`). |
| `-VERSIONS <list>` | Comma-separated API versions to run (e.g. `v1,v2`). |
| `-FLOW <name>` | Named execution flow from `flow/config_flow.yml`. |
| `-e` / `--execute` | Enable Execution Mode. Without this flag, the tool runs in Debug Mode. |
| `--no-ssl-verify` | Disable SSL certificate verification (for internal/self-signed environments only). |
| `-v` / `--verbose` | Enable debug-level logging output. |

### Examples

Run debug mode for Brazil and Argentina, accounts service, POST and PUT, v1:
```bash
python main.py -ENV dev -COUNTRIES br,ar -services accounts -METHODS post,put -VERSIONS v1
```

Run execution mode with a specific config and flow:
```bash
python main.py -CONFIG_YAML my_config -FLOW onboarding_flow -e
```

Run everything with the default config in execution mode:
```bash
python main.py -e
```

---

## Testing

```bash
make test
# or: pytest tests/ -v
```

The test suite covers the core data generation and file utilities (53 tests). A minimal `config_test.yml` is included so tests run without any production credentials.

---

## Project Structure

```
thunder-test-data-generator/
├── main.py                  # Entry point
├── api_sender.py            # Orchestrates execution flow and data generation
├── environment.py           # Config loading, arg parsing, all getter functions
├── commons/
│   ├── randomGenerator.py   # Faker-backed synthetic data generation
│   ├── requestBuilder.py    # HTTP request construction and execution
│   ├── payloadBuilder.py    # Jinja2 template rendering
│   ├── csvBuilder.py        # CSV data source strategies
│   ├── jsonBuilder.py       # JSON file utilities
│   ├── logger.py            # Logging setup
│   └── utils.py             # Filesystem utilities
├── templates/               # Jinja2 request body templates
├── datasource/              # CSV data files
├── flow/                    # Execution flow configs
├── config.yml               # Your environment config (gitignored if it has secrets)
├── config.example.yml       # Documented config reference
├── .env                     # Secrets (gitignored)
├── .env.example             # Secrets template
├── Makefile                 # Common commands
└── tests/                   # pytest test suite
```
