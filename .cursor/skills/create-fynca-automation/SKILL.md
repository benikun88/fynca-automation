---
name: create-fynca-automation
description: >-
  Create Fynca Playwright page objects and blackbox tests using the project
  automation standards. Use when adding pages, dialogs, wizards, fixtures, or
  pytest flows under test/black_box, or when the user asks to write automation
  tests for app.fynca.io.
disable-model-invocation: false
---

# Create Fynca Automation Tests & Pages

Follow `docs/automation-standart.md` and the layout under `test/black_box/`.

## Layout (source of truth)

```
test/black_box/
├── conftest.py              # fixtures/hooks only
├── models.py                # shared dataclasses
├── utils.py                 # shared helpers
├── test_<feature>.py        # flows + assertions
└── fynca/                   # POM
    ├── fynca.py             # facade
    ├── <name>_page.py
    ├── <name>_dialog.py     # when needed
    └── <name>_wizard.py     # when needed
```

Imports use the full package path:

```python
from test.black_box.fynca import Fynca
from test.black_box.fynca.canvas_page import CanvasPage
from test.black_box.models import TestConfig
```

## When adding a page

1. Create `test/black_box/fynca/<page_name>_page.py`.
2. Class name: `<PageName>Page`.
3. File header:

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = logging.getLogger(__name__)
```

4. Store collaborators as `self._page`, `self._base_url` (private).
5. Constructor may call `self.reload()` when the page must be ready immediately.
6. Method naming:
   - actions: plain verbs (`open_academy`, `share`, `save`) — never `click_`
   - reads: `get_*` / `is_*` / `has_*`
   - forms: `fill_*`, `set_*`, `select_*`
7. One method = one user action. Do **not** hide multi-step flows in page objects.
8. Locators priority: `get_by_test_id` → `get_by_role` → `get_by_text(exact=True)` → `get_by_label` → CSS last.
9. No hardcoded `timeout=`. Prefer visible UI waits. No shadow state on the page object.
10. Every public method starts with `logger.info("...", %s)` (lazy formatting).
11. Export via facade method on `Fynca` that **returns** the page object:

```python
def goto_canvas(self) -> CanvasPage:
    return CanvasPage(self._page, self._base_url, self._canvas_url)
```

## When adding a dialog / wizard

- Dialog: `<action>_<entity>_dialog.py`, class `<Name>Dialog`, root as `self._dialog`.
- Wizard: one class per step in one file; `next()` returns next step; final step uses `save()`.

## When adding a test

1. File: `test/black_box/test_<feature>.py`.
2. Function: `test_<action>_<subject>[_<condition>]`.
3. Required markers: feature (`canvas` / `login` / …) + priority (`smoke`/`sanity`) + `@pytest.mark.xray("FYNCA-…")`.
4. Prefer `@allure.title("...")`.
5. AAA with blank lines only — no `# Arrange` comments.
6. Tests orchestrate page actions and own business assertions with messages.
7. Use fixtures: `fynca`, `canvas`, `unauthenticated_fynca`, `test_config`.
8. Authenticated tests rely on `auth/storage_state.json` (create via `save_auth.py`).

Example:

```python
@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-002")
@allure.title("Academy opens Getting Started thesis curriculum")
def test_academy_shows_first_thesis_curriculum(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Academy")
```

## Checklist before finishing

- [ ] File/class/test names match standards
- [ ] No multi-step convenience methods on pages
- [ ] Locators semantic; no blind CSS
- [ ] Assertions in test file (except API `validate_response` / parse integrity)
- [ ] Markers + xray present
- [ ] `ruff check` / `ruff format` clean
- [ ] Run: `pytest test/black_box/test_<feature>.py -v`

## More detail

Full rules: [docs/automation-standart.md](../../../docs/automation-standart.md)
