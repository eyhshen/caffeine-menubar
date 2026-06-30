"""Caffeine — a tiny macOS menu-bar app that shows (and controls) keep-awake.

The coffee cup **steams whenever your Mac is actually being kept awake** — not just
when *this* app turned it on. It checks for a live `caffeinate` process (this app's
toggle, the built-in tool, or anything else using caffeinate), so the steam mirrors
the true keep-awake state; when nothing is caffeinating, the cup sits still.

Click the cup to toggle THIS app's own keep-awake on/off (it runs the system
`caffeinate`). Either way the steam mirrors the true, live state.

Run:  python3 app.py     (see README for the double-clickable .app)
"""
from __future__ import annotations

import atexit
import subprocess
from pathlib import Path

import rumps

ICONS = Path(__file__).resolve().parent / "icons"
ICON_OFF = str(ICONS / "cup_off.png")
ICON_ON = [str(ICONS / f"cup_on_{i}.png") for i in range(4)]

# Our own keep-awake: prevent display(-d), idle(-i), disk(-m), system(-s) sleep.
CAFFEINATE_CMD = ["caffeinate", "-d", "-i", "-m", "-s"]
ANIM_INTERVAL = 0.45   # steam frame cadence
POLL_INTERVAL = 2.0    # how often to re-check the real system state


def system_caffeinated() -> bool:
    """True if any `caffeinate` process is currently keeping the Mac awake.

    Detects THIS app's toggle, the built-in `caffeinate`, or any other caffeinate —
    so the steam mirrors the real keep-awake state, not just our own switch. We match
    `caffeinate` specifically (not pmset's PreventUserIdleDisplaySleep) so that normal
    video playback / audio doesn't make the cup steam.
    """
    try:
        r = subprocess.run(["pgrep", "-x", "caffeinate"], capture_output=True, text=True, timeout=3)
        return r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        return False


class CaffeineApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("Caffeine", icon=ICON_OFF, template=True, quit_button="退出")
        self.proc: subprocess.Popen | None = None  # our own caffeinate (the toggle)
        self.caffeinated = False                    # real system state (any source)
        self.frame = 0
        self.status_item = rumps.MenuItem("", callback=None)
        self.toggle_item = rumps.MenuItem("开启 Caffeination（本应用）", callback=self.toggle)
        self.menu = [self.status_item, self.toggle_item, None]
        self.poll_timer = rumps.Timer(self.poll, POLL_INTERVAL)
        self.poll_timer.start()
        self.anim_timer = rumps.Timer(self.animate, ANIM_INTERVAL)
        self.anim_timer.start()
        self.poll(None)  # set initial state immediately
        atexit.register(self._kill)

    @property
    def mine_on(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def _kill(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.proc = None

    def toggle(self, _sender) -> None:
        if self.mine_on:
            self._kill()
            self.toggle_item.title = "开启 Caffeination（本应用）"
        else:
            self.proc = subprocess.Popen(CAFFEINATE_CMD)
            self.toggle_item.title = "关闭 Caffeination（本应用）"
        self.poll(None)  # reflect immediately

    def poll(self, _timer) -> None:
        self.caffeinated = system_caffeinated()
        if self.caffeinated:
            who = "本应用 + 系统" if self.mine_on else "其它来源"
            self.status_item.title = f"☕ 电脑保持清醒中（{who}）"
        else:
            self.status_item.title = "💤 电脑可正常休眠"

    def animate(self, _timer) -> None:
        if self.caffeinated:
            self.frame = (self.frame + 1) % len(ICON_ON)
            self.icon = ICON_ON[self.frame]
        else:
            self.icon = ICON_OFF


if __name__ == "__main__":
    CaffeineApp().run()
