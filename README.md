# ☕ caffeine-menubar

A tiny macOS menu-bar app that keeps your Mac awake — with a coffee cup that **actually steams** while it's working.

![cup steaming](icons/cup_on_2.png) ← what you see in your menu bar when caffeinated

---

## What it does

| State | Icon | Mac behavior |
|-------|------|--------------|
| OFF | ☕ (still cup) | normal sleep/screensaver |
| ON  | ☕💨 (steaming, animated) | no display sleep, no idle sleep, no disk sleep, no system sleep |

Click the icon → toggle. That's it.

Under the hood it runs macOS's built-in `caffeinate -d -i -m -s`. No background daemons, no system extensions, no permissions required.

---

## Setup

```bash
git clone https://github.com/eyhshen/caffeine-menubar
cd caffeine-menubar

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# icons are already included, but you can regenerate them:
# .venv/bin/python make_icons.py

.venv/bin/python app.py
```

A coffee cup appears in your menu bar. Click it.

---

## Start at login (optional)

**Option A — Login Item (easiest):**
System Settings → General → Login Items → + → add `app.py`
(This won't work reliably; see Option B for a real solution.)

**Option B — build a `.app` with py2app:**
```bash
.venv/bin/pip install py2app
# setup.py coming soon
```

**Option C — LaunchAgent** (runs headlessly, most reliable):
```bash
# example plist coming soon
```

---

## Files

```
app.py          menu-bar app (rumps + subprocess caffeinate)
make_icons.py   draws the cup + 4 steam frames using Pillow
icons/          pre-rendered template PNGs (auto-tints for light/dark menu bar)
requirements.txt
```

---

## Requirements

- macOS (uses `caffeinate`, which ships with OS X 10.8+)
- Python 3.9+
- `rumps` and `Pillow` (see `requirements.txt`)

---

Built in an afternoon. Does one thing well.
