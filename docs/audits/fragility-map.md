# Fragility map — tooling/desktop-env/caffeine-menubar

- **Repo:** `/Users/elainesyh/Documents/GitHub/tooling/desktop-env/caffeine-menubar`
- **Audit date:** 2026-07-06
- **Scope:** ⚠️ *Interpretation flag:* the runbook scoped a repo called "membar", which does not exist under `~/Documents/GitHub`; this repo (the only menubar app) is the closest match — redirect if you meant something else. Read all tracked code: `app.py` (117 lines), `install.sh`, `uninstall.sh`, `make_icons.py`, `README.md`, `requirements.txt`, plus the installed LaunchAgent plist at `~/Library/LaunchAgents/com.elaine.caffeine-menubar.plist` and `.venv/pyvenv.cfg` as deployment evidence. Skipped `.venv/` package internals and pre-rendered icons. Findings are proportionate to a ~150-line app.

Ranked highest risk first.

---

## F1 — LaunchAgent + venv hardcode absolute paths; moving the repo or upgrading Homebrew Python silently kills the app at login (MED — has already bitten once)

**Evidence:**
- `install.sh:15` (`PY="$DIR/.venv/bin/python"`) and `:33-38` bake the absolute repo path into the plist; confirmed in the live plist (`~/Library/LaunchAgents/com.elaine.caffeine-menubar.plist`, ProgramArguments → `/Users/elainesyh/Documents/GitHub/tooling/desktop-env/caffeine-menubar/...`).
- **It already happened:** `.venv/pyvenv.cfg` records `command = ... -m venv /Users/elainesyh/Documents/GitHub/tooling/caffeine-menubar/.venv` — the repo used to live at `tooling/caffeine-menubar` and was moved to `tooling/desktop-env/`; the current plist points at the new path, so `install.sh` had to be re-run to recover.
- Second trigger: `.venv/bin/python3.14` symlinks to `/opt/homebrew/opt/python@3.14/bin/python3.14` — a Homebrew Python major/minor bump breaks the venv interpreter.
- Failure is silent by design: `install.sh:40` sets `KeepAlive=false` (no restart) and the only symptom lands in `~/Library/Logs/caffeine-menubar.log`.

**Blast radius:** The ☕ just never appears after login; nothing on screen says why. Rerunning `./install.sh` fixes it — the fragility is that nothing tells you to.

**Fix direction:** One line in README ("moved the folder or upgraded Python? re-run ./install.sh"), or have the plist invoke a tiny wrapper that re-execs install.sh's venv check.

## F2 — Cleanup relies solely on `atexit`; a crash or SIGTERM leaves an invisible immortal `caffeinate` (MED)

**Evidence:** `app.py:75` registers `atexit.register(self._cleanup)`; `_cleanup` (`:77-81`) terminates only `self.proc`. There is no signal handler anywhere in `app.py`. CPython does not run `atexit` on unhandled SIGTERM/SIGKILL or a hard crash.

**Why fragile:** If the app dies abnormally while toggled ON, the spawned `caffeinate -d -i -m -s` (`app.py:27` — no `-t` timeout) survives as an orphan. The state indicator (the cup) is gone with the app, so the Mac silently never sleeps — display included — until someone thinks to `pkill caffeinate`.

**Blast radius:** Battery drain / screen burn on a laptop left unplugged; no UI hint at all. Directly interacts with F3 in `uninstall.sh`.

## F3 — `uninstall.sh`'s success message makes a claim the code doesn't keep (LOW, but it will bite exactly once)

**Evidence:** `uninstall.sh:8-9` — `pkill -f "caffeine-menubar/app.py"` then `echo "✓ Removed. (Any active caffeinate from the app is also stopped.)"`. `pkill` sends SIGTERM; per F2 the app has no SIGTERM handler, so `_cleanup` (atexit) likely never runs and the app's `caffeinate` child is **not** stopped. (Runtime behavior unverified — rumps/PyObjC could conceivably install a handler — but nothing in this repo's code does.) Note `launchctl bootout` (`:6`) may terminate the app first via launchd; the pkill path is the fallback where the claim is most likely false.

**Blast radius:** Uninstall while caffeinated → Mac stays permanently awake with the app *and its indicator* gone. Fix direction: add `pkill -x caffeinate` scoped check, or a SIGTERM handler in `app.py` that calls `_cleanup`.

## F4 — Undocumented invariant: "keep-awake" is defined as "a process named exactly `caffeinate` exists" (LOW)

**Evidence:** `app.py:41` (`pgrep -x caffeinate`) drives the icon; `app.py:50` (`pkill -x caffeinate`) implements global OFF. The docstring (`app.py:33-38`) documents the video-playback exclusion deliberately, so this is a design choice — listed here only for its blast radius: clicking the cup OFF kills *every* user-owned `caffeinate`, including one wrapping someone else's long-running job (e.g. an overnight `caffeinate make …`), whose keep-awake assertion drops mid-run. Conversely, apps holding IOKit power assertions without a `caffeinate` process (Amphetamine, video calls) never make the cup steam.

**Blast radius:** Confined to expectations — but "one click killed my overnight job's keep-awake" is a real cross-tool trap worth one README sentence.

---

No other findings — the module graph is one file, the icons are committed (so the `make_icons.py` → `icons/` build step isn't a runtime dependency: `app.py:22-24` reads pre-rendered PNGs that exist in git), and the 2 Hz poll / 0.45 s animation split (`app.py:28-29`) is self-contained.
