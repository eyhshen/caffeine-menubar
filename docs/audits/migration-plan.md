# Migration plan — tooling/desktop-env/caffeine-menubar

- **Repo:** `/Users/elainesyh/Documents/GitHub/tooling/desktop-env/caffeine-menubar`
- **Audit date:** 2026-07-06
- **Scope:** ⚠️ *Interpretation flag:* the runbook scoped a repo called "membar", which does not exist; this menubar app is the closest match — redirect if you meant something else. Checked `requirements.txt` against installed versions (`.venv/lib/python3.14/site-packages/*.dist-info`) and against PyPI live (`pypi.org/pypi/<pkg>/json`, fetched 2026-07-06). Read `app.py` and `make_icons.py` for deprecated API usage. Proportionate verdict for a ~150-line app: there is almost nothing to migrate.

## Current state (verified)

| Package | Installed (.venv dist-info) | PyPI latest (live, 2026-07-06) | Gap |
|---|---|---|---|
| rumps | 0.4.0 | **0.4.0** (uploaded 2022-10-15) | none — already latest |
| Pillow | 12.2.0 | **12.3.0** (requires Python ≥3.10) | one patch-level minor |
| Python | 3.14.5 venv (`.venv/pyvenv.cfg`) | — | current |
| (transitive) pyobjc-core / -framework-Cocoa | 12.2.1 | not checked | — |

No deprecated stdlib APIs in use: `app.py` uses `subprocess.run/Popen` with argv lists, `pathlib`, `atexit`, modern `X | None` annotations (`app.py:64`), `from __future__ import annotations` (`:14`). `make_icons.py` uses current Pillow drawing APIs (`rounded_rectangle`, `arc` — nothing removed in Pillow 10–12).

## Steps

### 1. Pin the working versions **[mechanical]** — risk: low
`requirements.txt:1-2` uses floors (`rumps>=0.4`, `pillow>=10`). Pin to the verified-working set (`rumps==0.4.0`, `pillow==12.2.0`, or bump Pillow to 12.3.0 while at it — it's only used by `make_icons.py` at install time, so blast radius is icon generation). Doubles as the fix for the security note on unpinned installs.

### 2. Declare the AppKit dependency you already use **[mechanical]** — risk: low
`app.py:60` and `:113` import `AppKit` directly, but `requirements.txt` never mentions pyobjc — it arrives only as rumps's transitive dependency (present in `.venv` as pyobjc-core/pyobjc-framework-Cocoa 12.2.1). Both imports are wrapped in `try/except Exception: pass`, so if a future rumps release ever changed its deps the app wouldn't crash — the Dock icon suppression would just silently stop working. One line in `requirements.txt` (`pyobjc-framework-Cocoa`) closes the gap.

### 3. Watch item, no action: rumps is dormant **[judgment]** — risk: low today
rumps 0.4.0 is the latest release and is from **October 2022** (PyPI, verified live) — 3.5+ years with no release, and its metadata declares no `requires_python` and no dependencies. It demonstrably runs on Python 3.14 here (the venv installed and the LaunchAgent is registered; live runtime behavior not exercised during this read-only audit — commit eea0d20's message describes it running). The realistic future break is a macOS or CPython change that rumps never patches. No migration to do now; if it ever breaks, the app's rumps surface is tiny (`App`, `MenuItem`, `Timer` — `app.py:55-73`), so porting to raw PyObjC `NSStatusBar` is an afternoon-sized job. Explicitly **not** recommending that pre-emptively.

No sequencing constraints — steps 1 and 2 are independent one-liners.
