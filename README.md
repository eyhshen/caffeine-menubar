# ☕ caffeine-menubar

A tiny macOS menu-bar app that keeps your Mac awake — with a coffee cup that **actually steams** while it's working.

![cup steaming](icons/cup_on_2.png) ← what you see in your menu bar when caffeinated

---

## What it does

The cup **steams whenever your Mac is being kept awake** — by *anything* using
`caffeinate` (this app, the built-in tool, another app, a background agent). It mirrors
the real, live state, not just its own switch.

| State | Icon | Mac behavior |
|-------|------|--------------|
| 💤 idle  | ☕ (still cup)            | normal sleep / screensaver |
| ☕ awake | ☕💨 (steaming, animated) | display / idle / disk / system sleep all blocked |

Click the cup to toggle:
- **caffeinated → globally OFF** — stops *every* `caffeinate`, whoever started it
- **not caffeinated → ON** — starts one

Under the hood: macOS's built-in `caffeinate -d -i -m -s`. No daemons, no system
extensions, no permissions.

---

## Install (starts now + at login)

```bash
git clone https://github.com/eyhshen/caffeine-menubar
cd caffeine-menubar
./install.sh
```

Sets up a venv, renders the icons, and registers a **LaunchAgent** so the ☕ runs in
your menu bar and relaunches at login. Remove anytime with `./uninstall.sh`.

> **Why a LaunchAgent, not a double-click `.app`?** A bare-script `.app` often doesn't
> register as a GUI app on modern macOS, so its menu-bar icon never appears ("nothing
> happens"). The LaunchAgent launches it properly into your login session.

### Run once, no install
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

---

## Files

```
app.py          menu-bar app (rumps + subprocess caffeinate)
make_icons.py   draws the cup + 4 steam frames using Pillow
icons/          pre-rendered template PNGs (auto-tints for light/dark menu bar)
install.sh      venv + icons + LaunchAgent (start now & at login)
uninstall.sh    stop + remove the LaunchAgent
requirements.txt
```

---

## Requirements

- macOS (uses `caffeinate`, which ships with OS X 10.8+)
- Python 3.9+
- `rumps` and `Pillow` (see `requirements.txt`)

---

Built in an afternoon. Does one thing well.
