# Blackbox Test Standards

Rules and conventions for the Fynca FE blackbox test suite. Follow these when writing new tests, page objects, or utilities.

## Reference Examples

The patterns in this document are grounded in real code under `test/black_box/`. When in doubt, look at these canonical examples:

| Concern | Reference file |
|---------|----------------|
| Test file structure (Arrange / Act / Assert, fixtures, markers) | `test/black_box/test_flows.py`, `test/black_box/test_canvas.py` |
| Page object (locators, action methods) | `test/black_box/fynca/canvas_page.py` |
| Login page object | `test/black_box/fynca/login_page.py` |
| Facade | `test/black_box/fynca/fynca.py` |
| Shared dataclasses | `test/black_box/models.py` |
| Shared utilities | `test/black_box/utils.py` |
| Fixtures / session auth | `test/black_box/conftest.py` |

## Core Principles

All code in this test suite — page objects, utilities, and tests — should follow these principles:

- **Leave it better than you found it** — fix issues you encounter, don't pile more on top
- **Stop duplicating code** — look for existing page objects, utilities, and helpers before writing new ones
- **YAGNI** — don't create unnecessary abstractions or generalizations; strip unnecessary parts from your PR
- **Trust no one** — sanitize, check, and verify all input from everywhere
- **Code should be as simple as possible** — avoid deeply nested code (3 levels is bad, more is worse), avoid too many variables, avoid fancy hand waves
- **Prefer composition over inheritance** — page objects use composition (facade + page + dialog), not class hierarchies
- **One function = one action = one verb** — split anything else into smaller helpers
- **Variable name should be proportional to the scope it's used in** — short for one-line scopes, descriptive for module-level
- **You run the AI** — review all AI-generated test code with this document in hand before sending to your reviewer
- **Every class or module must have a well-defined mission** — encode it in the name or docstring

## Project Layout

```
test/black_box/
├── conftest.py                  # Fixtures and hooks only
├── models.py                    # Shared dataclasses (TestConfig, …)
├── utils.py                     # Shared utilities (validate_response, …)
├── test_<feature>.py            # Test files grouped by feature
│
└── fynca/                       # Fynca app POM
    ├── fynca.py                 # Facade — navigates to pages
    ├── login_page.py
    ├── home_page.py
    ├── canvas_page.py
    ├── <name>_dialog.py         # One class per dialog (when needed)
    ├── <name>_wizard.py         # One class per multi-step wizard (when needed)
    └── <subdomain>/             # Optional grouping (e.g. canvas panels)
        ├── <page>_page.py
        ├── <name>_dialog.py
        └── <name>_wizard.py
```

Supporting root scripts:

- `save_auth.py` — headed Chrome login; writes `auth/storage_state.json`
- `pytest.ini` — `testpaths = test/black_box`

## Naming Conventions

### Files

| Type | Pattern | Example |
|------|---------|---------|
| Test file | `test_<feature>.py` | `test_canvas.py`, `test_flows.py`, `test_login.py` |
| Page object | `<page_name>_page.py` | `canvas_page.py`, `login_page.py` |
| Dialog | `<action>_<entity>_dialog.py` | `share_canvas_dialog.py` |
| Wizard | `<action>_<entity>_wizard.py` | `create_canvas_wizard.py` |
| Utility | descriptive noun | `utils.py`, `api_patterns.py` |

### Classes

| Type | Pattern | Example |
|------|---------|---------|
| Page object | `<PageName>Page` | `CanvasPage`, `LoginPage`, `HomePage` |
| Dialog | `<Name>Dialog` | `ShareCanvasDialog` |
| Wizard step | `<StepName>Step` | `StarterStep`, `TemplateDetailsStep` |
| Facade | Product name | `Fynca` |
| Data class | descriptive noun | `TestConfig`, `WatchlistRow` |

### Test Functions

```
test_<action>_<subject>[_<condition>]
```

Examples:
- `test_canvas_loads_when_authenticated`
- `test_academy_shows_first_thesis_curriculum`
- `test_watchlist_asset_filters`

### Fixtures

| Scope | Naming | Example |
|-------|--------|---------|
| Session | `<noun>` or `<noun>_<qualifier>` | `test_config`, `storage_state` |
| Function | `<adjective>_<noun>` or product noun | `fynca`, `canvas`, `unauthenticated_fynca` |

### Pytest Markers

Every test must have:
1. A **feature marker** (`@pytest.mark.canvas`, `@pytest.mark.login`, …)
2. An **xray marker** linking to the test case (`@pytest.mark.xray("FYNCA-…")`)

Optional second marker for priority: `smoke`, `sanity`.

Registered markers (see `pytest.ini`): `smoke`, `sanity`, `login`, `canvas`, `monkey`, `exploratory`, `xray`.

```python
@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-002")
def test_academy_shows_first_thesis_curriculum(canvas: CanvasPage) -> None:
```

## Page Object Model

### Structure

Every page object follows this template:

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class SomePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url
        self.reload()

    def reload(self) -> None:
        self._page.goto(f"{self._base_url}/path")
```

Rules:
- Store `page` as `self._page` (private).
- The constructor navigates to the page via `self.reload()` when the page must be ready immediately. Prefer an optional `navigate: bool = True` flag when callers may reuse an already-open page.
- Prefix private/internal helpers with `_` (e.g. `_sidebar`, `_parse_rows`).

### Dialog Objects

Dialogs store their root locator as `self._dialog`:

```python
class ShareCanvasDialog:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._dialog = self._page.get_by_role("dialog")
```

The dialog locator (`self._dialog`) scopes all element lookups to the dialog, preventing conflicts with background page elements. **Always use `self._dialog` as a member variable, not a method.**

### Return Types for Navigation

Methods that open a new page or dialog **return the corresponding page object**:

```python
# Facade returns page objects
def goto_canvas(self) -> CanvasPage:
    return CanvasPage(self._page, self._base_url, self._canvas_url)

def goto_login(self) -> LoginPage:
    return LoginPage(self._page, self._base_url)

# Page returns dialog/wizard objects when extracted
def share(self) -> ShareCanvasDialog:
    self._page.get_by_role("button", name="Share canvas").click()
    return ShareCanvasDialog(self._page)
```

### Method Naming

**Do not use a `click_` prefix.** Use plain verbs that describe the user action:

```python
# Correct
def open_academy(self) -> None: ...
def share(self) -> None: ...
def start_from_scratch(self) -> None: ...
def filter_watchlist(self, asset_class: str) -> None: ...

# Wrong — redundant prefix
def click_academy(self) -> None: ...
def click_share_canvas(self) -> None: ...
```

Full naming conventions:

| Pattern | Usage | Examples |
|---------|-------|---------|
| Plain verb | Actions that trigger something | `save()`, `close()`, `share()`, `reload()` |
| `open_` | Open a panel / section | `open_academy()`, `open_watchlist()` |
| `get_` | Read-only data retrieval | `get_url()`, `get_credits_label()` |
| `is_` / `has_` | Boolean presence checks | `is_share_visible()`, `has_text()` |
| `set_` | Set a form value | `set_status()` |
| `fill_` | Fill text fields | `fill_identifier()`, `fill_chat_message()` |
| `select_` | Choose from options | `select_chat_mode()`, `select_academy_lesson()` |
| `filter_` | Apply filters | `filter_watchlist()`, `filter_portfolio()` |
| `next()` | Wizard step transition | `next()` → returns the next step |
| `save()` | Submit dialogs/forms | Single method, regardless of button text |
| `close()` | Cancel/dismiss dialogs | `close()` |

### Method Organization

Organize methods in page objects in this order:
1. `__init__` / `reload`
2. Public action methods (`open_*`, `start_*`, `filter_*`, `share`, …)
3. Public data-retrieval methods (`get_*`, `is_*`, `has_*`)
4. Private helpers (`_sidebar`, `_parse_*`, `_field`)

## Wizard Pattern

Multi-step flows are modeled as **one class per step**. Each step exposes `next()` which returns the next step's wrapper:

```python
class TemplateDetailsStep:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._dialog = self._page.get_by_role("dialog")

    def set_template_name(self, name: str) -> None:
        self._dialog.get_by_label("Name").fill(name)

    def next(self) -> TemplateContentStep:
        self._dialog.get_by_role("button", name="Next").click()
        return TemplateContentStep(self._page)

    def close(self) -> None:
        self._dialog.get_by_role("button", name="Cancel").click()


class TemplateContentStep:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._dialog = self._page.get_by_role("dialog")

    def save(self) -> None:
        with self._page.expect_response(API_PATTERN) as response_info:
            self._dialog.get_by_role("button", name="Save").click()
        validate_response(response_info.value)
```

Rules:
- **Step classes live in the same wizard file.**
- `next()` returns the next step, not `None`.
- The final step has `save()`, not `next()`.
- **One `save()` method handles all button text variants** — use a combined locator if the same dialog shows "Create" or "Save changes" depending on mode:
  ```python
  def save(self) -> None:
      save_button = self._dialog.locator(
          "button:has-text('Create'), button:has-text('Save changes')"
      )
      with self._page.expect_response(API_PATTERN) as response_info:
          save_button.click()
      validate_response(response_info.value)
  ```

Usage in a test file:

```python
step1 = templates_page.create_template()
step1.set_template_name("My Thesis")
step2 = step1.next()
step2.save()
```

## Page Objects vs Test Files — Responsibility Split

### Page objects: actions and data, no flows

Page objects expose **individual user actions** and **data retrieval methods**. They must **never** combine multiple steps into a single "convenience" method:

```python
# Wrong — this is a test flow hiding in a page object
def complete_academy_lesson(self, title: str) -> None:
    self.open_academy()
    self.select_academy_lesson(title)
    self.dismiss_overlays()

# Correct — each step is an individual method
def open_academy(self) -> None: ...
def select_academy_lesson(self, title: str) -> None: ...
def dismiss_overlays(self) -> None: ...
```

Exception: tiny setup helpers that only prepare a known precondition (e.g. `ensure_workspace_ready()` dismissing the starter picker) are acceptable when they do not hide business assertions.

### Test files: flows and assertions

The test file orchestrates the steps. Organize tests in the **Arrange / Act / Assert** pattern — use whitespace to separate the sections:

```python
def test_academy_shows_first_thesis_curriculum(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Academy")
    assert canvas.is_heading_visible("Learn Fynca by building your first thesis")
```

Do **not** label AAA sections with comments — the whitespace is enough:

```python
# Wrong — unnecessary comments
def test_academy_shows_first_thesis_curriculum(canvas: CanvasPage) -> None:
    # Arrange
    canvas.ensure_workspace_ready()
    # Act
    canvas.open_academy()
    # Assert
    assert canvas.is_heading_visible("Academy")

# Correct — whitespace makes the structure clear
def test_academy_shows_first_thesis_curriculum(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Academy")
```

### Tests must actually test something

Make sure tests prevent regressions. A test that calls a function without asserting the right outcome passes even when the code is broken:

```python
# Wrong — passes even if open_academy does nothing useful
def test_open_academy(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

# Correct — verifies Academy content is actually shown
def test_open_academy(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Academy"), "Academy heading was not visible"
```

## Locator Strategy

Use locators in this priority order:

| Priority | Method | When to use |
|----------|--------|-------------|
| 1 | `get_by_test_id("...")` | When `data-testid` exists in the DOM |
| 2 | `get_by_role("...", name="...")` | Buttons, tabs, menu items, textboxes |
| 3 | `get_by_text("...", exact=True)` | Unique visible text |
| 4 | `get_by_label("...")` | Form inputs with associated labels |
| 5 | CSS selector via `locator()` | Only when above options don't work |

### Form Field Pattern

When labels are not directly associated with inputs, use the sibling selector helper:

```python
def _field(self, label: str) -> Locator:
    return self._dialog.locator(f'label:has-text("{label}") + div input')
```

### Scoping Locators to Dialogs

When multiple dialogs or overlapping elements exist, scope locators:

```python
self._dialog.get_by_role("button", name="Copy link")  # scoped to dialog
```

## Waits, Timeouts, and Race Conditions

### Never use hardcoded timeouts

Rely on Playwright's built-in auto-wait and default timeout. Never pass explicit `timeout=` values:

```python
# Wrong
share.wait_for(state="visible", timeout=10000)

# Correct
share.wait_for(state="visible")
```

### Wait for visual indicators, not API calls

Prefer waiting for **something visible on screen** rather than intercepting API responses. This makes tests resilient to backend changes and aligns with how a real user experiences the page:

```python
# Preferred — wait for visible content
def reload(self) -> None:
    self._page.goto(self._canvas_url, wait_until="domcontentloaded")
    self._page.get_by_role("button", name="Share canvas").wait_for()
    self._page.get_by_role("button", name="Toolkit").wait_for()

# Acceptable but less preferred — wait for API response
def reload(self) -> None:
    with self._page.expect_response(self.CANVAS_API_PATTERN):
        self._page.goto(self._canvas_url)
```

Use `expect_response` only when:
- Asserting that an API call succeeded (e.g., after a create/save/delete action).
- The page has no reliable visual indicator of load completion.

### Handle loading race conditions with `or_`

When a page can render in two states (content or empty message), **wait for either** before checking which one appeared. Otherwise you'll hit a race condition where neither is rendered yet:

```python
# Correct — wait for either state, then check
empty_state = self._page.get_by_text("No positions yet", exact=True)
positions = self._page.get_by_role("table")
empty_state.or_(positions).wait_for(state="visible")

if empty_state.is_visible():
    return []
# ... parse rows

# Wrong — race condition; page may not have loaded yet
if self._page.get_by_text("No positions yet").is_visible():
    return []
# ... parse rows (may fail because table isn't rendered yet)
```

This pattern applies whenever you check for an empty state before parsing content: lists, tables, panels, etc.

### Don't lazy-load in `reload()` when not needed

If the page object doesn't need to be ready immediately on construction, consider whether `reload()` should be called in `__init__` or deferred until a method actually needs the content:

```python
# If page load is always needed on construction
def __init__(self, page: Page, base_url: str) -> None:
    self._page = page
    self._base_url = base_url
    self.reload()

# If navigation is optional (reuse already-open page)
def __init__(self, page: Page, base_url: str, *, navigate: bool = True) -> None:
    self._page = page
    self._base_url = base_url
    if navigate:
        self.reload()
```

## Fail Fast — Never Swallow Errors

**Do not write "safety guards" that silently handle unexpected states.** If something is wrong, the test should fail immediately and loudly.

### Don't guard with `is_visible()` before interacting

```python
# Wrong — swallows errors silently
if radio.is_visible() and radio.is_checked():
    return True
return False

# Correct — if the radio isn't there, the test fails with a clear error
return radio.is_checked()
```

If the element should be present, don't check visibility first. If it's truly absent, you *want* the test to fail so you know something broke.

Boolean `is_*` helpers that intentionally report presence (e.g. `is_starter_visible()`) are fine — they are the check, not a guard before a required interaction.

### Don't return `None` to hide failures

```python
# Wrong — caller has no idea why None was returned
def get_sidebar_names(self) -> list[str] | None:
    if not self._page.get_by_role("button", name="Toolkit").is_visible():
        return None

# Correct — return empty list if nothing found, fail if unexpected
def sidebar_names(self) -> list[str]:
    return [name for name in _SIDEBAR_NAMES if self._sidebar(name).is_visible()]
```

For methods returning collections: return `[]`, not `None`. Reserve `None` only for single-value lookups where "not found" is a valid state, and name the method with `_or_none` suffix.

## No Shadow State

**Do not store application state in page object attributes.** Always check what is actually on screen:

```python
# Wrong — shadow copy of page state
def select_chat_mode(self, mode: str) -> None:
    self._page.get_by_role("tab", name=mode).click()
    self._chat_mode = mode  # shadow state — gets out of sync

def is_build_mode_selected(self) -> bool:
    return self._chat_mode == "Build"

# Correct — check the actual page
def is_build_mode_selected(self) -> bool:
    return self._page.get_by_role("tab", name="Build", exact=True).is_visible()
```

## Constants and Module-Level Variables

### Prefix module-level locals with `_`

Module-level constants that are **not part of the public API** must be prefixed with `_`:

```python
# Correct
_ACADEMY_THESIS_STEPS = (
    "1. Start with a ticker",
    "2. Add a chart",
)
_SIDEBAR_NAMES = ("Toolkit", "Agents", "Ideas", "Academy")

# Wrong — looks like a public export
ACADEMY_THESIS_STEPS = (...)
SIDEBAR_NAMES = (...)
```

Exception: class-level constants on page objects (like `CANVAS_API_PATTERN`) are fine without underscore since they're scoped to the class.

### Inline constants used only once

If a constant is only used in a single method, inline it. Don't extract it to the module or class level:

```python
# Wrong — constant used only in one place, extracted to module level
_REACT_FLOW_TEST_ID = "rf__wrapper"

class CanvasPage:
    def is_react_flow_visible(self) -> bool:
        return self._page.get_by_test_id(_REACT_FLOW_TEST_ID).is_visible()

# Correct — inline where used
class CanvasPage:
    def is_react_flow_visible(self) -> bool:
        return self._page.get_by_test_id("rf__wrapper").is_visible()
```

### Place patterns near their usage

If a regex pattern is used by only one class or method, define it close to that code, not at the top of the file:

```python
# Correct — pattern next to the class that uses it
_SHARE_API = re.compile(r"/api/canvas/.+/share")

class ShareCanvasDialog:
    def copy_link(self) -> None:
        with self._page.expect_response(_SHARE_API) as resp:
            ...
```

When multiple classes across files share patterns, put them in a dedicated `api_patterns.py` module.

## Element Visibility and Count

### Use `is_visible()` for presence checks, not `count()`

```python
# Wrong
if element.count() > 0 and element.is_visible():
    ...

# Wrong
if element.count() > 0:
    ...

# Correct
if element.is_visible():
    ...
```

Use `count()` only when you genuinely need to know *how many* matching elements exist (e.g., iterating rows).

## Function Parameter Design

### Don't allow `None` for jointly-required params

If two parameters must both be provided or both be omitted, don't make them independently optional. Use overloads or require both:

```python
# Wrong — what happens if only one is None?
def find_suggestion(
    self, theme: str | None = None, ticker: str | None = None
) -> str | None:
    if theme and ticker:
        ...
    return ...

# Correct — caller must provide both or neither
def get_all_suggestions(self) -> Sequence[str]:
    ...

def find_suggestion(self, theme: str, ticker: str) -> str | None:
    ...
```

### Avoid redundant methods that return the same data

Don't create two methods that parse the same data differently. If you already have a method returning a list, callers can filter it themselves:

```python
# Wrong — redundant with sidebar_names()
def has_sidebar(self, name: str) -> bool:
    return name in self.sidebar_names()

# Correct — filter in the test when needed
names = canvas.sidebar_names()
assert "Academy" in names, f"Academy missing from {names}"
```

## Dict Access

### Prefer `dict[key]` over `dict.get()` + manual raise

Let Python's built-in `KeyError` surface naturally instead of re-implementing it:

```python
# Wrong — reimplements KeyError
label = _CHAT_MODE_LABELS.get(mode)
if label is None:
    raise ValueError(f"Unknown chat mode: {mode}")

# Correct — KeyError is clear and automatic
label = _CHAT_MODE_LABELS[mode]
```

## Return Style

### Don't assign-then-return

```python
# Wrong
url = self._page.url
return url

# Correct
return self._page.url
```

## API Response Assertions

For actions that trigger an API call (create, save, delete), use `expect_response` + `validate_response`:

```python
def save(self) -> None:
    with self._page.expect_response(TEMPLATES_API_PATTERN) as response_info:
        self._dialog.get_by_role("button", name="Save").click()
    validate_response(response_info.value)
```

This pattern:
- Waits for the specific API call to complete (no arbitrary sleeps).
- Asserts the response status is 2xx via `validate_response`.
- Is used for **mutating actions** only (create, save, delete).

## Assertions

### Where Assertions Live

| Type | Location | Example |
|------|----------|---------|
| API response status | Page object | `validate_response(resp.value)` |
| Data integrity | Page object parsing (`_parse_*`) | `assert cells, "Row must have cells"` |
| Business logic | **Test file** | `assert canvas.is_heading_visible("Academy")` |

Page objects expose **data and presence helpers**. Tests make the business assertion:

```python
# In test file — not in page object
assert canvas.is_heading_visible("Academy"), "Academy heading was not visible"
assert canvas.has_text("1. Start with a ticker"), "Missing academy step"
```

Always include a descriptive message in test-level assertions.

## Data Models

- Use `@dataclass(frozen=True)` for all data models.
- Use `Sequence[T]` for return types when the caller shouldn't mutate the list.
- Use `StrEnum` for string-based enumerations.
- Define dataclasses **close to where they're used** — in the page/dialog file that returns them, or in `models.py` if shared across multiple files.

```python
@dataclass(frozen=True)
class TestConfig:
    base_url: str
    email: str
    password: str
    canvas_url: str
```

## Fixtures

### Available Fixtures

| Fixture | Scope | Provides | Use when |
|---------|-------|----------|----------|
| `fynca` | function | Authenticated `Fynca` facade | Most authenticated tests |
| `canvas` | function | Authenticated `CanvasPage` | Canvas / panel / flow tests |
| `unauthenticated_fynca` | function | Unauthenticated `Fynca` | Login UI tests |
| `test_config` | session | `TestConfig` | Tests needing env config |
| `storage_state` | session | Path to `auth/storage_state.json` | Session reuse (wired into `context`) |

### Fixture Selection

- Tests that **don't need login** (or test the login UI itself) use `unauthenticated_fynca`.
- Tests that **need an authenticated session** use `fynca` / `canvas` (backed by `auth/storage_state.json` from `save_auth.py`).

## Logging

```python
logger = logging.getLogger(__name__)
```

### Rules

1. Every public page object method starts with `logger.info(...)`.
2. Use lazy `%s` formatting in logger calls, not f-strings:
   ```python
   # Correct
   logger.info("Opening sidebar: %s", name)

   # Incorrect
   logger.info(f"Opening sidebar: {name}")
   ```
3. Use `logger.debug` for private helper details.
4. Never log passwords or sensitive tokens (including contents of `storage_state.json`).

## Artifacts

On test failure (including fixture setup), the framework attaches to Allure:
- Full-page screenshot
- Page URL
- Video recording of the browser session (WebM)

Files are also kept under `reports/playwright`. Open the failed test in the Allure report to play the video. Prefer `@allure.title("...")` on tests for readable titles.

## Auth / Session

Authenticated tests reuse Clerk session state:

1. Run `save_auth.py` once locally (headed Chrome).
2. Complete sign-in manually.
3. Session is written to `auth/storage_state.json` (gitignored).
4. CI uses secret `FYNCA_STORAGE_STATE_B64`.

Do not automate Google OAuth in headless browsers — it is blocked by Google.

## Python Code Style

### File header

Every Python file in the test suite starts with the same boilerplate:

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = logging.getLogger(__name__)
```

Rules:

- **Always use `from __future__ import annotations`.** This defers all type hints, so you can write `Sequence[Foo]` without importing `Foo` at runtime.
- **Put runtime-only imports at the top, type-only imports under `TYPE_CHECKING`.** Anything imported solely for type hints (e.g. `Page`, `Locator`, `Sequence`, `Path`) belongs under `TYPE_CHECKING`.
- **One `logger = logging.getLogger(__name__)` per module.** Never `print`.

### Type hints

- **Type-hint every function signature** — parameters and return type.
- **Don't allow `None` for jointly-required parameters.** If two parameters must both be provided or both be omitted, split into two methods or require both. See [Function Parameter Design](#function-parameter-design).
- **Don't return `T | None` unless the function returns a single value and "not found" is a valid outcome.** When you must return `None`, suffix the method name with `_or_none`.
- **Use `Sequence[T]` for read-only return types.** Use `list[T]` only when callers are expected to mutate.
- **Use `Callable`, `Iterable`, etc. from `collections.abc`** — never from `typing`.

### Data models

Use `@dataclass(frozen=True)` for all data models. Shared example from `models.py`:

```python
@dataclass(frozen=True)
class TestConfig:
    base_url: str
    email: str
    password: str
    canvas_url: str
```

Use `StrEnum` for string-based enumerations:

```python
class ChatMode(StrEnum):
    BUILD = "Build"
    ASK = "Ask"
```

Place dataclasses **next to the page/dialog that returns them**, or in `models.py` if shared across multiple files.

### Naming and units

- **Use descriptive names** that clearly describe expected behavior.
- **Add units in the name or use types with units built in** — e.g. `timeout_ms`, `_WAIT_FOR_PANEL_SECONDS`.
- **Name proportional to scope** — `i` is fine inside a 3-line loop, `canvas_page` is required at module level.

### Function design

- **One function = one action = one verb.** If you find yourself joining verbs with `and`, split the method.
- **No one-line methods that only call another function.** Inline them. (Exception: methods required by an interface or protocol.)
- **Don't make classes with only `@staticmethod` / `@classmethod`** — use free functions in a module instead.
- **Avoid deeply nested code.** Three nesting levels is bad; more is worse. Split into private helpers.

## Playwright Best Practices

### Locator priority

Prefer role-based and semantic locators over CSS / XPath. Use locators in this priority order:

| Priority | Method | When to use |
|----------|--------|-------------|
| 1 | `get_by_test_id("...")` | When `data-testid` exists in the DOM |
| 2 | `get_by_role("...", name="...")` | Buttons, tabs, menu items, textboxes |
| 3 | `get_by_text("...", exact=True)` | Unique visible text |
| 4 | `get_by_label("...")` | Form inputs with associated labels |
| 5 | `get_by_title("...")` | Elements with title attributes |
| 6 | `page.locator()` with CSS | Last resort — only when semantic locators can't reach |

Examples from `canvas_page.py` / `login_page.py`:

```python
# Good — role + name
self._page.get_by_role("button", name="Share canvas").click()
self._page.get_by_role("heading", name="Academy", exact=True).wait_for()
self._page.get_by_role("textbox", name="Message input").fill(message)

# Good — test id when present
self._page.get_by_test_id("rf__wrapper").wait_for()

# Acceptable — last resort when Clerk fields lack roles/labels
self._page.locator("#identifier-field").fill(identifier)
```

```python
# Wrong — CSS string for something with a clear role
self._page.locator("button:has-text('Share canvas')")

# Wrong — XPath for something with a label
self._page.locator("//input[@id='email']")
```

### Visibility checks

- **Use `is_visible()` for presence checks**, not `count() > 0` or `count() == 0`.
- **Never combine `count()` and `is_visible()`** — pick one based on intent.
- **Use `count()` only when you genuinely need to know how many** matching elements exist.

```python
# Good — checking presence
if empty_state.is_visible():
    return []

# Good — actually counting
for i in range(rows.count()):
    text = rows.nth(i).text_content()

# Wrong
if element.count() > 0 and element.is_visible():
    ...
```

### Reuse locators

Store frequently-used locators as class attributes or local variables instead of recomputing them.

```python
class ShareCanvasDialog:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._dialog = self._page.get_by_role("dialog")
        self._copy_button = self._dialog.get_by_role("button", name="Copy link")
```

### Wait strategies

- **Never pass explicit `timeout=` values** — rely on Playwright's default.
- **Prefer waiting for a visible UI signal** over waiting for an API response.
- **Use `expect_response()` only for mutating actions** (create, save, delete) where you need to assert the request succeeded.
- **Use `or_()` to wait for either of two states** when the page can render in multiple ways (content vs empty placeholder). Otherwise you race.

```python
# Good — wait for either, then branch
empty_state.or_(table).wait_for(state="visible")
if empty_state.is_visible():
    return []

# Good — chat mode may be tab or button
tab = self._page.get_by_role("tab", name=mode, exact=True)
button = self._page.get_by_role("button", name=mode, exact=True)
tab.or_(button).click()

# Wrong — explicit timeout
table.wait_for(state="visible", timeout=10000)

# Wrong — race condition
if self._page.get_by_text("No items").is_visible():
    return []
# table may not be rendered yet
```

### Field interaction

- **Playwright's `fill()` clears the field first** — never call `clear()` before `fill()`.
- **Use `fill()` to replace** field content (works on `<input>`, `<textarea>`, and `contenteditable`).
- **Use `type()` / `press_sequentially()`** only when you need to trigger keystroke handlers or append text.

## Code Style

- Keep page object files under ~150 lines where possible. Split dialogs / wizards into their own files.
- `locator()` with CSS selectors is a last resort — prefer role-based / semantic locators.
- **Avoid deeply nested code** — 3 nesting levels is bad, more is worse. Split inner logic into private helper methods.
- **Don't make classes with only `@staticmethod` or `@classmethod`** — use free functions in a module instead.
- **No one-line methods that only call some other function** — inline them. (Exception: methods required by an interface or protocol.)

## Exception Handling

Follow the **log XOR re-raise** rule — do not log *and* re-raise the same exception, as this produces confusing double tracebacks:

```python
# Wrong — logs and re-raises, causing duplicate tracebacks
try:
    self._page.goto(url)
except PlaywrightError as e:
    logger.exception("Navigation failed")
    raise

# Correct — re-raise without logging (a higher-level handler will log it)
try:
    self._page.goto(url)
except PlaywrightError as e:
    raise NavigationError(f"Failed to navigate to {url}") from e

# Correct — log without re-raising (swallow and handle)
try:
    self._page.goto(url)
except PlaywrightError:
    logger.exception("Navigation failed, retrying")
    self._page.goto(url)
```

Do not include the exception object in the log message — `logger.exception` already appends the traceback:

```python
# Wrong
logger.exception("Navigation failed: %s", e)

# Correct
logger.exception("Navigation failed")
```

## Tabs and Collapsible Sections

### Keep layout details private

Page layout elements (tabs, collapsible/expandable areas) are **internal mechanics** that tests should never interact with directly. Any method that accesses content in a tab or collapsible section must privately switch to the correct tab first:

```python
# Wrong — test must know about tabs
def select_build_tab(self) -> None:
    self._page.get_by_role("tab", name="Build").click()

# Correct — public method owns the tab switch
def select_chat_mode(self, mode: str) -> None:
    tab = self._page.get_by_role("tab", name=mode, exact=True)
    button = self._page.get_by_role("button", name=mode, exact=True)
    tab.or_(button).click()
```

Rules:
- Tabs and collapsible sections are **private** when they are only layout — prefix with `_` if exposed as helpers.
- Every public method that reads from a specific tab **must switch to it first**.
- After switching tabs, **clean up** by switching back if other methods expect the default tab.

### Expandable rows — check state before toggling

When clicking a row toggles between expanded and collapsed, always check the current state before acting:

```python
# Wrong — assumes row is collapsed, breaks if called twice
def expand_row(self, row: Locator) -> None:
    row.click()

# Correct — check if already expanded
def _ensure_row_expanded(self, row: Locator) -> None:
    expand_icon = row.locator("[data-expanded='false']")
    if expand_icon.is_visible():
        row.click()
```

## Dataclass Field Naming

### Use nouns for property names, not question words

```python
# Wrong — question words as field names
@dataclass(frozen=True)
class IdeaSuggestion:
    what: str
    when: str

# Correct — noun-based, self-descriptive
@dataclass(frozen=True)
class IdeaSuggestion:
    theme_name: str
    ticker_symbol: str
```

### Enum values describe meaning, not appearance

```python
# Wrong — describes visual color, breaks if UI changes
class CreditBadgeType(StrEnum):
    LOW_RED = "red"
    OK_GREEN = "green"

# Correct — describes semantic meaning
class CreditBadgeType(StrEnum):
    LOW = "low"
    AVAILABLE = "available"
```

## Page Objects Must Only Parse What Is Displayed

Page objects should **read and return what the UI shows**, not apply business logic to compute derived values:

```python
# Wrong — page object computes status from credit count (business logic)
def _parse_credit_status(self, credits: int) -> CreditBadgeType:
    if credits <= 3:
        return CreditBadgeType.LOW
    return CreditBadgeType.AVAILABLE

# Correct — page object reads status from UI text/styling
def get_credits_label(self) -> str:
    return self._page.get_by_role("button", name="AI credits").inner_text()
```

## Regex and Parsing Patterns

### Use focused patterns, not overly broad ones

```python
# Wrong — matches too much unrelated text
_CREDITS_PATTERN = re.compile(r"credits:.*?(\d+)")

# Correct — focused extraction after scoping to the correct element
credits_text = self._page.get_by_role("button", name="AI credits").inner_text()
```

### Include the actual text in assertion messages

```python
# Wrong — no context on failure
assert match, "Could not parse credits"

# Correct — shows what text was being parsed
credits_text = credits_button.inner_text()
assert match, f"Could not parse credits from: '{credits_text}'"
```

## Configuration and Environment

Never hardcode environment-specific URLs or credentials in tests. Use `test_config` / `.env`:

```python
# Wrong — hardcoded canvas id in a test
page.goto("https://app.fynca.io/canvas/19a6606e631640d979a4a2de")

# Correct — use fixture / env
canvas = fynca.goto_canvas()  # uses test_config.canvas_url
```

Relevant env vars:
- `FYNCA_BASE_URL`
- `FYNCA_CANVAS_URL`
- `FYNCA_EMAIL` / `FYNCA_PASSWORD` (manual `save_auth.py` only)

## Redundant Assertions

### Don't assert things that can't fail

If the code above an assertion would already crash on the error condition, the assertion is redundant:

```python
# Wrong — if open_academy() waited for the heading, this adds little
canvas.open_academy()
assert canvas.is_heading_visible("Academy")  # may be redundant depending on wait

# Correct — assert business outcomes beyond the wait target
canvas.open_academy()
assert canvas.has_text("1. Start with a ticker"), "Missing academy step"
```

### Prefer exact expected values over `> 0`

```python
# Weak — passes even if unexpected extras appear
assert len(names) > 0

# Strong — exact / meaningful expectation
assert "Academy" in names, f"Academy missing from {names}"
```

## Consistency Across Similar Functions

When a class has multiple methods that do structurally similar things, make them structurally consistent:

```python
# Wrong — inconsistent early-return patterns in same class
def is_share_visible(self) -> bool:
    return self._page.get_by_role("button", name="Share canvas").is_visible()

def is_button_visible(self, name: str) -> bool:
    locator = self._page.get_by_role("button", name=name)
    return locator.count() > 0 and locator.first.is_visible()  # inconsistent

# Correct — same visibility style where possible
def is_share_visible(self) -> bool:
    return self._page.get_by_role("button", name="Share canvas").is_visible()

def is_button_visible(self, name: str) -> bool:
    return self._page.get_by_role("button", name=name).first.is_visible()
```

## Don't Click Before Fill

Playwright's `fill()` auto-focuses the element. Never call `.click()` before `.fill()`:

```python
# Wrong — click is redundant
input_field.click()
input_field.fill("value")

# Correct — fill handles focus
input_field.fill("value")
```

## Redundant `wait_for()` Before Actions

Playwright actions (click, fill, etc.) auto-wait for the element to be actionable. Don't add explicit waits before them unless you're waiting for a *different* state:

```python
# Wrong — redundant, .fill() already waits for visibility
self._page.get_by_role("textbox", name="Message input").wait_for(state="visible")
self._page.get_by_role("textbox", name="Message input").fill(message)

# Correct — let the action wait
self._page.get_by_role("textbox", name="Message input").fill(message)
```

## Running Code Formatting

Always run `ruff format` (and `ruff check`) before submitting a PR. Code that does not conform to formatting standards will be sent back.

## Do / Don't Cheatsheet

A consolidated quick reference. Each row is grounded in patterns from `test/black_box/`.

### Locators

| Do | Don't |
|----|------|
| `self._page.get_by_role("button", name="Share canvas")` | `self._page.locator("button:has-text('Share canvas')")` |
| `self._dialog.get_by_role("button", name="Copy link")` (scoped) | `self._page.get_by_role("button", name="Copy link")` (global, may collide) |
| `get_by_test_id("rf__wrapper")` when `data-testid` exists | guessing CSS classes when a test id exists |
| `get_by_text("Ask Margo", exact=True)` | `:text-is('Ask Margo')` raw selector |
| Reuse `self._dialog` as a member variable | Re-creating the dialog locator inside every method |

### Visibility / counting

| Do | Don't |
|----|------|
| `if element.is_visible():` | `if element.count() > 0:` |
| `for i in range(rows.count()):` (when iterating) | `if rows.count() > 0 and rows.is_visible():` |
| `empty_state.or_(table).wait_for(state="visible")` | Check `empty_state.is_visible()` before page rendered |

### Waits and API

| Do | Don't |
|----|------|
| `element.wait_for(state="visible")` (no timeout) | `element.wait_for(state="visible", timeout=10000)` |
| Wait for visible content to confirm page load | `time.sleep(5)` |
| `with page.expect_response(API_PATTERN): button.click()` for mutations | Wrap every read with `expect_response` |
| `validate_response(resp.value)` after a save / create / delete | Trust the click silently |

### Page object methods

| Do | Don't |
|----|------|
| `def open_academy(self) -> None:` | `def click_academy(self): ...` |
| `def sidebar_names(self) -> list[str]:` returns `[]` if empty | Returns `None` when empty |
| One method per user action (`open_academy`, `select_chat_mode`, `fill_chat_message`) | One mega-method `complete_agent_prompt(mode, text)` |
| Facade / page returns next dialog / wizard step object | Page returns `bool` / `None` after navigating |

### Tests

| Do | Don't |
|----|------|
| Arrange / Act / Assert separated by blank lines | Label sections with `# Arrange` / `# Act` / `# Assert` |
| Always end with an assertion that proves the side effect | Just call methods and trust them to throw |
| Assertion messages explain expectations: `assert canvas.is_heading_visible("Academy"), "…"` | Bare `assert canvas.is_heading_visible("Academy")` |
| Add `@pytest.mark.xray("FYNCA-…")` and a feature marker | No markers, no test-case linkage |

### Python style

| Do | Don't |
|----|------|
| `from __future__ import annotations` at the top of every file | Forward-reference imports at runtime |
| `if TYPE_CHECKING:` for `Page`, `Locator`, `Sequence`, etc. | Importing them at runtime when only used as type hints |
| `@dataclass(frozen=True)` for data models | Plain mutable classes for return values |
| `StrEnum` for string constants | Bare strings repeated across files |
| `logger.info("Opening sidebar: %s", name)` | `logger.info(f"Opening sidebar: {name}")` |
| Re-raise OR log — never both | `logger.exception(...)` followed by `raise` |
| `_PRIVATE_CONSTANT` for module-private values | `PUBLIC_LOOKING_CONSTANT` for internals |
| `dict[key]` (let `KeyError` surface) | `dict.get(key)` + manual `raise ValueError` |
| Return `self._page.url` directly | `url = self._page.url; return url` |

### Function design

| Do | Don't |
|----|------|
| `get_all_suggestions()` and `find_suggestion(theme, ticker)` | `get_suggestion(theme=None, ticker=None)` with mixed semantics |
| Inline a constant used in only one place | Hoist single-use constants to module level |
| `_or_none` suffix when `None` is a valid return | Silent `None` returns from collection methods |

### Playwright interactions

| Do | Don't |
|----|------|
| `input_field.fill("value")` | `input_field.click(); input_field.fill("value")` |
| Let actions auto-wait for the element | `element.wait_for(); element.click()` (redundant wait) |
| Check if row is expanded before toggling | Assume row state and click blindly |
| Scope locators to their container | Use broad page-level locators for dialog content |

### Naming and enums

| Do | Don't |
|----|------|
| `CreditBadgeType.LOW` (semantic meaning) | `CreditBadgeType.LOW_RED` (visual appearance) |
| `theme_name: str` (noun) | `what: str` (question word) |
| `share_button` (describes what it represents) | `locator` (describes the type) |

### Consistency and config

| Do | Don't |
|----|------|
| `test_config.canvas_url` / `FYNCA_CANVAS_URL` | Hardcode canvas URLs in tests |
| Same early-return style across similar functions in one class | Mixed positive/negative guard styles |
| Tabs/collapsibles handled inside page object methods | Expose raw `select_build_tab()` for tests to orchestrate |

## Complete Example

The following is a self-contained example showing a full test and page object working together. Patterns are taken from `test_flows.py` and `canvas_page.py`.

### Test file (`test_flows.py` excerpt)

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import allure
import pytest

if TYPE_CHECKING:
    from test.black_box.fynca.canvas_page import CanvasPage

logger = logging.getLogger(__name__)

_ACADEMY_THESIS_STEPS = (
    "1. Start with a ticker",
    "2. Add a chart",
    "3. Add fundamentals",
    "4. Add technicals",
    "5. Auto-arrange",
    "6. Ask AI with context",
)


@pytest.mark.canvas
@pytest.mark.smoke
@pytest.mark.xray("FYNCA-FLOW-002")
@allure.title("Academy opens Getting Started thesis curriculum")
def test_academy_shows_first_thesis_curriculum(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Academy"), "Academy heading was not visible"
    assert canvas.is_heading_visible("Learn Fynca by building your first thesis"), (
        "Getting Started curriculum heading was not visible"
    )
    for step in _ACADEMY_THESIS_STEPS:
        assert canvas.has_text(step), f"Missing academy step: {step}"
```

This test illustrates:

- `from __future__ import annotations` + `TYPE_CHECKING` imports.
- Feature + priority + xray markers, plus `@allure.title(...)`.
- AAA structure separated by blank lines, no comments.
- Each assertion has a descriptive message explaining the expectation.
- Page object exposes actions / presence helpers — the test does the business assertions.
- Test ends with assertions that prove the side effect actually happened (curriculum content).

### Page object (`canvas_page.py` excerpt)

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class CanvasPage:
    """Authenticated Fynca research canvas workspace."""

    def __init__(
        self,
        page: Page,
        base_url: str,
        canvas_url: str,
        *,
        navigate: bool = True,
    ) -> None:
        self._page = page
        self._base_url = base_url
        self._canvas_url = canvas_url
        if navigate:
            self.reload()

    def reload(self) -> None:
        logger.info("Opening canvas: %s", self._canvas_url)
        self._page.goto(self._canvas_url, wait_until="domcontentloaded")
        self._page.get_by_role("button", name="Share canvas").wait_for()
        self._page.get_by_role("button", name="Toolkit").wait_for()
        self._page.get_by_test_id("rf__wrapper").wait_for()

    def ensure_workspace_ready(self) -> None:
        if self.is_starter_visible():
            self.start_from_scratch()

    def start_from_scratch(self) -> None:
        logger.info("Starting canvas from scratch with Otto")
        self._page.get_by_role("button", name="Start from scratch with Otto").click()
        self._page.get_by_role("heading", name="Pick your starting point").wait_for(
            state="hidden"
        )

    def open_academy(self) -> None:
        logger.info("Opening Academy")
        self._sidebar("Academy").click()
        self._page.get_by_role("heading", name="Academy", exact=True).wait_for()

    def is_starter_visible(self) -> bool:
        return self._page.get_by_role(
            "heading", name="Pick your starting point"
        ).is_visible()

    def is_heading_visible(self, name: str) -> bool:
        return self._page.get_by_role("heading", name=name).is_visible()

    def has_text(self, text: str) -> bool:
        return self._page.get_by_text(text, exact=False).first.is_visible()

    def _sidebar(self, name: str) -> Locator:
        return self._page.get_by_role("button", name=name)
```

This page object illustrates:

- Constructor stores collaborators as private attributes; optional `navigate` avoids double-loads.
- `reload()` waits for visible UI signals (Share, Toolkit, React Flow), not hardcoded sleeps.
- Public action methods use plain verbs (`open_academy`, `start_from_scratch`), no `click_` prefix.
- Presence helpers (`is_*` / `has_*`) return what the UI shows; tests assert business outcomes.
- Private `_sidebar` helper keeps sidebar lookup DRY.
- Module-level logger named after the module.
