import json
import os
import plistlib
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List

import rumps
from Foundation import NSOperationQueue

from bluetooth import (
    BlueutilError,
    connect_device,
    is_already_paired_error,
    is_blueutil_available,
    is_device_connected,
    list_paired_devices,
    pair_device,
    unpair_device,
)


CONFIG_DIR = Path.home() / "Library" / "Application Support" / "MagicAccessoriesConnector"
PREFS_FILE = CONFIG_DIR / "prefs.json"

LAUNCH_AGENT_LABEL = "dev.radixen.magic-accessories-connector"
LAUNCH_AGENT_PLIST = (
    Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_LABEL}.plist"
)


def _is_start_at_login_enabled() -> bool:
    return LAUNCH_AGENT_PLIST.exists()


def _set_start_at_login(enabled: bool) -> None:
    if enabled:
        plist_data: dict = {
            "Label": LAUNCH_AGENT_LABEL,
            "ProgramArguments": [sys.executable],
            "EnvironmentVariables": {"OBJC_DISABLE_INITIALIZE_FORK_SAFETY": "YES"},
            "RunAtLoad": True,
            "KeepAlive": False,
        }
        LAUNCH_AGENT_PLIST.parent.mkdir(parents=True, exist_ok=True)
        with open(LAUNCH_AGENT_PLIST, "wb") as fh:
            plistlib.dump(plist_data, fh)
        subprocess.run(
            ["launchctl", "load", str(LAUNCH_AGENT_PLIST)],
            check=False,
            capture_output=True,
        )
    else:
        if LAUNCH_AGENT_PLIST.exists():
            subprocess.run(
                ["launchctl", "unload", str(LAUNCH_AGENT_PLIST)],
                check=False,
                capture_output=True,
            )
            LAUNCH_AGENT_PLIST.unlink(missing_ok=True)


class MagicAccessoriesConnectorApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("MAC", quit_button=None)
        self.show_all_devices = False
        self._reconnecting = False
        self._reconnect_lock = threading.Lock()
        self._load_prefs()
        self.refresh_menu()

    def _load_prefs(self) -> None:
        if not PREFS_FILE.exists():
            return

        try:
            payload = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
            self.show_all_devices = bool(payload.get("show_all_devices", False))
        except (json.JSONDecodeError, OSError):
            self.show_all_devices = False

    def _save_prefs(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"show_all_devices": self.show_all_devices}
        PREFS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _filtered_devices(self, devices: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if self.show_all_devices:
            return devices

        filtered = [device for device in devices if "magic" in device["name"].lower()]
        return filtered

    def _open_bluetooth_settings(self) -> None:
        subprocess.run(
            ["open", "x-apple.systempreferences:com.apple.BluetoothSettings"],
            check=False,
            capture_output=True,
        )

    def _dispatch_to_main(self, fn) -> None:
        """Schedule fn() on the main thread via NSOperationQueue."""
        NSOperationQueue.mainQueue().addOperationWithBlock_(fn)

    def _forget_and_reconnect_flow(self, address: str, name: str) -> None:
        ATTEMPTS = 6
        DELAY = 2  # seconds between attempts

        connected = False
        last_error = None
        unpair_error_msg = None

        try:
            try:
                unpair_device(address)
                self._open_bluetooth_settings()
                self._dispatch_to_main(lambda: rumps.notification(
                    title="Device forgotten",
                    subtitle=name,
                    message="Put it in pairing mode now. Trying auto-reconnect for about 12 seconds.",
                ))
            except BlueutilError as exc:
                unpair_error_msg = str(exc)

            if unpair_error_msg is None:
                has_paired = False

                for attempt in range(ATTEMPTS):
                    self._dispatch_to_main(lambda: setattr(self, 'title', '●'))

                    if not has_paired:
                        try:
                            pair_device(address)
                            has_paired = True
                        except BlueutilError as exc:
                            msg = str(exc)
                            if is_already_paired_error(msg):
                                has_paired = True
                            else:
                                last_error = msg
                                if attempt < ATTEMPTS - 1:
                                    self._countdown(DELAY)
                                continue

                    try:
                        connect_device(address)
                        if is_device_connected(address):
                            connected = True
                            break
                        last_error = "Pair/connect ran but device is not connected yet"
                    except BlueutilError as exc:
                        last_error = str(exc)

                    if attempt < ATTEMPTS - 1:
                        self._countdown(DELAY)

        finally:
            with self._reconnect_lock:
                self._reconnecting = False

            # Capture loop locals for the closure — the background thread exits
            # immediately after dispatching; the closure must carry its own copies.
            _unpair_err = unpair_error_msg
            _connected = connected
            _last_err = last_error

            if _connected:
                def _finish():
                    rumps.notification(
                        title="Auto-reconnect succeeded",
                        subtitle=name,
                        message="Device paired and connected.",
                    )
                    self.title = 'MAC'
                    self.refresh_menu()
            elif _unpair_err:
                def _finish():
                    self.title = '!'
                    # alert blocks until OK — cleanup runs after, not during
                    rumps.alert(title="Could not forget device", message=_unpair_err, ok="OK")
                    self.title = 'MAC'
                    self.refresh_menu()
            else:
                failure_msg = (
                    "Could not auto-reconnect in time. "
                    "Keep Bluetooth Settings open and pair manually."
                )
                if _last_err:
                    failure_msg = f"{failure_msg}\n\nLast error: {_last_err}"
                def _finish():
                    self.title = '!'
                    # alert blocks until OK — cleanup runs after, not during
                    rumps.alert(title="Auto-reconnect timed out", message=failure_msg, ok="OK")
                    self.title = 'MAC'
                    self.refresh_menu()

            self._dispatch_to_main(_finish)

    def _countdown(self, seconds: int) -> None:
        for remaining in range(seconds, 0, -1):
            self._dispatch_to_main(lambda r=remaining: setattr(self, 'title', str(r)))
            time.sleep(1)

    def _on_forget(self, _: rumps.MenuItem, address: str, name: str) -> None:
        with self._reconnect_lock:
            if self._reconnecting:
                return
            self._reconnecting = True
        threading.Thread(
            target=self._forget_and_reconnect_flow,
            args=(address, name),
            daemon=True,
        ).start()

    def refresh_menu(self) -> None:
        self.menu.clear()

        if not is_blueutil_available():
            self.menu.add(rumps.MenuItem("blueutil not found"))
            self.menu.add(rumps.MenuItem("Install blueutil", callback=self._install_help))
            self.menu.add(None)
            self.menu.add(rumps.MenuItem("Quit", callback=self._quit_app))
            return

        try:
            paired_devices = list_paired_devices()
            visible_devices = self._filtered_devices(paired_devices)
        except BlueutilError as exc:
            self.menu.add(rumps.MenuItem(f"Error: {exc}"))
            self.menu.add(None)
            self.menu.add(rumps.MenuItem("Refresh", callback=self._refresh_clicked))
            self.menu.add(rumps.MenuItem("Quit", callback=self._quit_app))
            return

        if not visible_devices:
            self.menu.add(rumps.MenuItem("No matching paired devices"))
        else:
            for device in visible_devices:
                name = device["name"]
                address = device["address"]
                label = f"Forget + Reconnect: {name} ({address})"
                self.menu.add(
                    rumps.MenuItem(
                        label,
                        callback=lambda item, a=address, n=name: self._on_forget(item, a, n),
                    )
                )

        self.menu.add(None)
        toggle_label = "Show only Magic devices" if self.show_all_devices else "Show all paired devices"
        self.menu.add(rumps.MenuItem(toggle_label, callback=self._toggle_filter))
        self.menu.add(rumps.MenuItem("Open Bluetooth Settings", callback=self._open_settings_clicked))
        self.menu.add(rumps.MenuItem("Refresh", callback=self._refresh_clicked))
        if getattr(sys, "frozen", False):
            login_label = "Don't Start at Login" if _is_start_at_login_enabled() else "Start at Login"
            self.menu.add(rumps.MenuItem(login_label, callback=self._toggle_start_at_login))
        self.menu.add(rumps.MenuItem("Quit", callback=self._quit_app))

    def _install_help(self, _: rumps.MenuItem) -> None:
        rumps.alert(
            title="blueutil missing",
            message="Install blueutil, then restart this app.\n\nHomebrew: brew install blueutil",
            ok="OK",
        )

    def _toggle_filter(self, _: rumps.MenuItem) -> None:
        self.show_all_devices = not self.show_all_devices
        self._save_prefs()
        self.refresh_menu()

    def _open_settings_clicked(self, _: rumps.MenuItem) -> None:
        self._open_bluetooth_settings()

    def _refresh_clicked(self, _: rumps.MenuItem) -> None:
        self.refresh_menu()

    def _toggle_start_at_login(self, _: rumps.MenuItem) -> None:
        _set_start_at_login(not _is_start_at_login_enabled())
        self.refresh_menu()

    def _quit_app(self, _: rumps.MenuItem) -> None:
        rumps.quit_application()


if __name__ == "__main__":
    os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
    MagicAccessoriesConnectorApp().run()
