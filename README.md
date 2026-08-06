# Fynca Playwright Automation

Blackbox UI tests for the authenticated [Fynca app](https://app.fynca.io) canvas workspace.

## Setup

```powershell
cd C:\Users\benik\fynca-automation
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
```

## Save login session (once)

```powershell
.\.venv\Scripts\python.exe save_auth.py
```

Complete sign-in in Chrome. Session is saved to `auth/storage_state.json`.

## Configure canvas

```
FYNCA_BASE_URL=https://app.fynca.io
FYNCA_CANVAS_URL=https://app.fynca.io/canvas/<your-canvas-id>
```

## Run tests

```powershell
pytest -m canvas
pytest -m "monkey or exploratory"
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Post-login flows covered

1. Authenticated canvas loads
2. Starter picker (Margo / Nico / Otto + Ask Margo / Show Nico / Just build)
3. Start from scratch dismisses picker
4. Academy Getting Started thesis curriculum (steps 1–6)
5. Academy topic tracks + advanced lesson modules
6. Agents (Bob & Charlie) Build/Ask chat
7. Ideas welcome + catalyst/theme/stock suggestions
8. Watchlist / Portfolio empty states and filters
9. Zoom / pan / selection toolbar + Share dialog
10. Monkey sidebar + exploratory locator sweep

## CI / Allure

Workflow: `.github/workflows/playwright.yml`

Required GitHub secret:

- `FYNCA_STORAGE_STATE_B64` — base64 of `auth/storage_state.json`

Optional variable:

- `FYNCA_CANVAS_URL`

Encode secret (PowerShell):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("auth\storage_state.json"))
```

## Layout

Standards: [`docs/automation-standart.md`](docs/automation-standart.md)  
Skill (pages/tests): [`.cursor/skills/create-fynca-automation/`](.cursor/skills/create-fynca-automation/)

```
├── save_auth.py
├── docs/automation-standart.md
├── test/black_box/
│   ├── conftest.py
│   ├── models.py
│   ├── utils.py
│   ├── test_*.py
│   └── fynca/                 # POM facade + pages
│       ├── fynca.py
│       ├── login_page.py
│       ├── home_page.py
│       └── canvas_page.py
└── .github/workflows/playwright.yml
```
