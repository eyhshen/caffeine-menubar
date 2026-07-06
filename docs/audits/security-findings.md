# Security findings — tooling/desktop-env/caffeine-menubar

- **Repo:** `/Users/elainesyh/Documents/GitHub/tooling/desktop-env/caffeine-menubar`
- **Audit date:** 2026-07-06
- **Scope:** ⚠️ *Interpretation flag:* the runbook scoped a repo called "membar", which does not exist; this menubar app is the closest match — redirect if you meant something else. Swept the working tree for credential patterns; swept all 5 commits of git history via `/usr/bin/git log -p --all` (795-line dump; `/usr/bin/git` used because the rtk shell hook truncates plain `git log -p` output) with the brief's secret regex plus a check for `.env`/credential/key-file additions. Read all of `app.py`, `install.sh`, `uninstall.sh`, `make_icons.py`, `requirements.txt`. This is a local, offline, single-user desktop utility: no network code, no auth surface, no stored data, no server — most audit categories are structurally empty for it.

---

## No findings of substance

- **Secrets:** none in the working tree; none in any of the 5 commits (b93cec0 → eea0d20); no env/credential file ever added. The only grep hits repo-wide are icon filenames and this audit's own patterns.
- **Attack surface:** `app.py` makes zero network calls; its subprocess use is fixed argv lists (`app.py:27,41,50` — `caffeinate`, `pgrep`, `pkill`), no shell interpolation, no user-supplied input anywhere in the program.
- **Install scripts:** `install.sh` writes only under the repo and `$HOME/Library` (`:14,26-27`), uses `set -euo pipefail` (`:10`), and fetches nothing except pip packages.

## Low — unpinned PyPI installs at install time

**Evidence:** `requirements.txt:1-2` (`rumps>=0.4`, `pillow>=10`); `install.sh:20` installs whatever PyPI serves that day, and `:19` additionally `--upgrade`s pip.

**Why it matters (barely):** the classic supply-chain exposure — a future malicious/compromised release of either package would be picked up by the next `./install.sh` run. For a personal offline tool this is the lowest realistic severity; noted because the fix is one line.

**Remediation (described, not applied):** pin exact versions (`rumps==0.4.0`, `pillow==12.2.0` — the versions currently in `.venv`) or add a `pip freeze`-generated lock. Nothing else to do.
