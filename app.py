"""Caffeine — a tiny macOS menu-bar app that shows AND globally controls keep-awake.

The coffee cup **steams whenever your Mac is actually being kept awake** — by ANY
`caffeinate` process (this app, the built-in tool, another app, even a background
agent). It mirrors the true, live state; when nothing is caffeinating, the cup is still.

Click the cup to toggle:
  • If the Mac is currently caffeinated (by anything) → **globally turns it OFF**
    (kills every `caffeinate` process).
  • If it's not → turns it ON (starts a `caffeinate`).

Run:  python3 app.py
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


def kill_all_caffeinate() -> None:
    """Global OFF: terminate every caffeinate process (ours, the agent's, anything)."""
    try:
        subprocess.run(["pkill", "-x", "caffeinate"], capture_output=True, timeout=3)
    except Exception:
        pass


class CaffeineApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("Caffeine", icon=ICON_OFF, template=True, quit_button="退出")
        # Run as a pure menu-bar accessory — no Dock icon, no app-switcher entry.
        try:
            from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
            NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        except Exception:
            pass
        self.proc: subprocess.Popen | None = None  # our own caffeinate (for atexit cleanup)
        self.caffeinated = False                    # real system state (any source)
        self.frame = 0
        self.status_item = rumps.MenuItem("", callback=None)
        self.toggle_item = rumps.MenuItem("开启 Caffeination", callback=self.toggle)
        self.menu = [self.status_item, self.toggle_item, None]
        self.poll_timer = rumps.Timer(self.poll, POLL_INTERVAL)
        self.poll_timer.start()
        self.anim_timer = rumps.Timer(self.animate, ANIM_INTERVAL)
        self.anim_timer.start()
        self.poll(None)  # set initial state immediately
        atexit.register(self._cleanup)

    def _cleanup(self) -> None:
        # On quit, only stop OUR own caffeinate (don't globally kill others).
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.proc = None

    def toggle(self, _sender) -> None:
        if system_caffeinated():
            kill_all_caffeinate()   # global OFF
            self.proc = None
        else:
            self.proc = subprocess.Popen(CAFFEINATE_CMD)  # ON
        self.poll(None)  # reflect immediately

    def poll(self, _timer) -> None:
        self.caffeinated = system_caffeinated()
        if self.caffeinated:
            self.status_item.title = "☕ 电脑保持清醒中"
            self.toggle_item.title = "全局关闭 Caffeination"
        else:
            self.status_item.title = "💤 电脑可正常休眠"
            self.toggle_item.title = "开启 Caffeination"

    def animate(self, _timer) -> None:
        if self.caffeinated:
            self.frame = (self.frame + 1) % len(ICON_ON)
            self.icon = ICON_ON[self.frame]
        else:
            self.icon = ICON_OFF


if __name__ == "__main__":
    # Belt-and-suspenders: suppress Dock icon before the run loop starts.
    # The LaunchAgent plist also sets ProcessType=UIElement, but this ensures
    # the policy is right even when the script is run directly.
    try:
        from AppKit import NSApp, NSApplicationActivationPolicyAccessory  # type: ignore[import]
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except Exception:
        pass
    CaffeineApp().run()
