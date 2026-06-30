"""Caffeine — a tiny macOS menu-bar app that keeps your Mac awake.

A coffee-cup icon sits in the menu bar. When caffeinated, the cup **steams**
(animated); when off, it's a plain cup. Click it to toggle on/off.

Under the hood it runs the system `caffeinate` tool (no sleep / no display off)
while ON, and kills it when OFF or on quit.

Run:  python3 app.py     (see README for a double-clickable .app build)
"""
from __future__ import annotations

import atexit
import subprocess
from pathlib import Path


def _system_caffeinated() -> bool:
    """Return True if any caffeinate process is running on this Mac."""
    result = subprocess.run(["pgrep", "-x", "caffeinate"], capture_output=True)
    return result.returncode == 0

import rumps

ICONS = Path(__file__).resolve().parent / "icons"
ICON_OFF = str(ICONS / "cup_off.png")
ICON_ON = [str(ICONS / f"cup_on_{i}.png") for i in range(4)]

# caffeinate flags: -d display, -i idle/system, -m disk, -s system (on AC). Keeps the Mac fully awake.
CAFFEINATE_CMD = ["caffeinate", "-d", "-i", "-m", "-s"]
ANIM_INTERVAL = 0.45  # seconds per steam frame


class CaffeineApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("Caffeine", icon=ICON_OFF, template=True, quit_button="退出")
        self.proc: subprocess.Popen | None = None
        self.frame = 0
        self.status_item = rumps.MenuItem("状态：未咖啡因 ☕", callback=None)
        self.toggle_item = rumps.MenuItem("开启 Caffeination", callback=self.toggle)
        self.menu = [self.status_item, self.toggle_item, None]  # None = separator before Quit
        self.timer = rumps.Timer(self.animate, ANIM_INTERVAL)
        self.timer.start()
        atexit.register(self._kill)

    @property
    def on(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def _kill(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.proc = None

    def _start(self) -> None:
        self.proc = subprocess.Popen(CAFFEINATE_CMD)
        self.status_item.title = "状态：咖啡因中 ♨︎"
        self.toggle_item.title = "关闭 Caffeination"

    def _stop(self) -> None:
        self._kill()
        self.status_item.title = "状态：未咖啡因 ☕"
        self.toggle_item.title = "开启 Caffeination"
        self.icon = ICON_OFF

    def toggle(self, _sender) -> None:
        self._stop() if self.on else self._start()

    def animate(self, _timer) -> None:
        # Drive icon from real system state, not just our own subprocess.
        if _system_caffeinated():
            self.frame = (self.frame + 1) % len(ICON_ON)
            self.icon = ICON_ON[self.frame]
        else:
            self.icon = ICON_OFF


if __name__ == "__main__":
    CaffeineApp().run()
