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
2. Starter picker (Margo / Nico / Otto)
3. Start from scratch dismisses picker
4. Watchlist panel
5. Portfolio panel
6. Canvases panel
7. Templates panel
8. Academy
9. Zoom / fit controls
10. Share dialog
11. Chat Build/Ask (when panel open)
12. Monkey sidebar clicks
13. Exploratory locator sweep

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

```
├── save_auth.py
├── conftest.py
├── test_canvas.py
├── test_monkey.py
├── test_exploratory.py
├── fynca/
│   ├── canvas_page.py
│   ├── fynca.py
│   ├── login_page.py
│   └── home_page.py
└── .github/workflows/playwright.yml
```
