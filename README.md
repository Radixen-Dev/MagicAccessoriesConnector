# Magic Accessories Connector

> Forget your Magic Mouse or Magic Keyboard on one Mac, then re-pair it to another — straight from your menu bar, in one click.

---

## The Problem

Apple Magic accessories pair to exactly one Mac at a time. Switching between two Macs means diving into System Settings, forgetting the device, waiting for it to appear on the other machine, and re-pairing — every single time.

**Magic Accessories Connector** lives quietly in your menu bar and does all of that for you. One click forgets the device and immediately attempts to auto-pair and reconnect it so you barely have to touch anything.

---

## What It Does

- **One-click forget + reconnect** — unpairs the device and begins trying to re-pair automatically for ~12 seconds while you flip the device's pairing switch
- **Auto-reconnect with retry** — polls for the device repeatedly so the timing is forgiving
- **Bluetooth Settings shortcut** — opens the system panel automatically so you can pair manually if auto-reconnect times out
- **Smart device filtering** — shows only Magic devices by default; toggle to see all paired Bluetooth devices
- **Persistent preferences** — your filter choice is remembered between sessions
- **Auto-start at login** — enable from the menu bar icon with one click, no terminal needed

---

## Requirements

- macOS 12 Monterey or later
- [Homebrew](https://brew.sh) — the macOS package manager

> No Xcode, no Python knowledge, and no other setup required.

---

## Installation

### Install Homebrew (if you don't have it)

Open **Terminal** (press `⌘ Space`, type *Terminal*, press Enter) and paste:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. When it finishes, come back here.

---

### Install Magic Accessories Connector

```sh
brew tap Radixen-Dev/tap
brew install --cask magic-accessories-connector
```

That's it. Homebrew downloads the app, installs it to `/Applications/`, and installs the `blueutil` dependency automatically.

---

### Launch the app

```sh
open /Applications/MagicAccessoriesConnector.app
```

A **MAC** icon appears in your menu bar.

> **First launch on a new Mac:** macOS Gatekeeper may show a security prompt because the app is not yet signed with an Apple certificate. Right-click the app in Finder, choose **Open**, then click **Open** in the dialog. You only need to do this once.

---

### Start automatically at every login (recommended)

Click the **MAC** icon in the menu bar, then click **Start at Login**. A checkmark confirms it's enabled. No terminal command needed.

---

## Using the App

### Forget + Reconnect a device

1. Click the **MAC** icon in the menu bar
2. Click **Forget + Reconnect: \<device name\>**
3. A notification confirms the device was forgotten and tells you to put it into pairing mode
4. Switch the device's pairing mode (the small button/switch on the device)
5. The app tries to pair and connect automatically for ~12 seconds
6. A second notification confirms success — or an alert tells you to pair manually via the Bluetooth Settings window that opened automatically

### Toggle device visibility

By default, only Apple Magic devices are shown. To see every paired Bluetooth device:

- Click **Show all paired devices**

To return to the filtered view:

- Click **Show only Magic devices**

### Start at Login

Click **Start at Login** in the menu to enable auto-start. The item shows a checkmark (\u2713) when active. Click it again to disable.

### Open Bluetooth Settings directly

Click **Open Bluetooth Settings** in the menu to jump straight to the system panel.

---

## Preferences

Your settings are stored at:

```
~/Library/Application Support/MagicAccessoriesConnector/prefs.json
```

This file is created automatically the first time you change a preference. It currently stores one key:

| Key | Type | Default | Description |
|---|---|---|---|
| `show_all_devices` | boolean | `false` | Show all paired Bluetooth devices, not just Magic accessories |

---

## Uninstall

To remove **everything** in a single command:

```sh
brew uninstall --cask --zap magic-accessories-connector
```

The `--zap` flag instructs Homebrew to also remove:
- The app from `/Applications/`
- Your saved preferences (`~/Library/Application Support/MagicAccessoriesConnector/`)
- The Start-at-Login entry (`~/Library/LaunchAgents/dev.radixen.magic-accessories-connector.plist`)

After this command, nothing from Magic Accessories Connector remains on your machine.

If you also want to remove `blueutil`:

```sh
brew uninstall blueutil
```

Only do this if nothing else on your system uses it.

### Upgrading from v1.0.0 (formula)

If you installed the old formula-based v1.0.0:

```sh
brew uninstall magic-accessories-connector
brew install --cask magic-accessories-connector
```

If you also want to remove `blueutil` (the Bluetooth CLI that MAC depends on):

```sh
brew uninstall blueutil
```

Only do this if nothing else on your system uses it.

---

## Troubleshooting

### The MAC icon doesn’t appear in the menu bar

Check the app is running:

```sh
pgrep -x MagicAccessoriesConnector
```

If it's not running, launch it:

```sh
open /Applications/MagicAccessoriesConnector.app
```

macOS limits the number of visible menu bar icons. Also check **System Settings → Control Centre** to see if it’s hidden, or your menu bar management tool (e.g. Bartender).

### The app is blocked on first launch

macOS Gatekeeper will prompt on the first open because the app is not yet notarized. Right-click the app in **Finder**, choose **Open**, then click **Open** again. You only need to do this once. Alternatively:

```sh
xattr -cr /Applications/MagicAccessoriesConnector.app
```

### Start at Login stopped working

If the **Start at Login** item loses its checkmark after a macOS update or system migration, disable and re-enable it from the menu.

### "blueutil not found" appears in the menu

```sh
brew install blueutil
```

If the Cask was freshly installed and blueutil is still missing, run:

```sh
brew reinstall --cask magic-accessories-connector
```

Then click **Refresh** in the MAC menu.

### Auto-reconnect always times out

The retry window is ~12 seconds. If your device takes longer to enter pairing mode, pair it manually through the Bluetooth Settings window that opens automatically. The device will be paired after that and will appear again in the MAC menu.

### The app crashes or the menu is blank

Check the macOS system log for the process:

```sh
log show --predicate 'process == "MagicAccessoriesConnector"' --last 5m
```

---

## For Developers

### Running from source

```sh
git clone https://github.com/Radixen-Dev/MagicAccessoriesConnector.git
cd MagicAccessoriesConnector
./install.sh
```

`install.sh` creates a `.venv`, installs dependencies, and launches the app directly.

### Project layout

```
app.py            — rumps menu bar app; all UI logic
bluetooth.py      — blueutil subprocess wrapper; retry/connect logic
requirements.txt  — Python dependencies (rumps only; pyobjc comes transitively)
build.sh          — PyInstaller .app builder + zip packager for Cask releases
MagicAccessoriesConnector.spec — PyInstaller bundle configuration
install.sh        — dev quick-start (source run only)
uninstall.sh      — full removal script (handles both Cask and source installs)
```

### Releasing a new version

1. Update the version string in `MagicAccessoriesConnector.spec` (`CFBundleShortVersionString` / `CFBundleVersion`) and `build.sh` (`VERSION=`)
2. Run `./build.sh` — it produces `dist/MagicAccessoriesConnector-<VERSION>.zip` and prints the SHA256
3. Create a git tag: `git tag v<VERSION> && git push origin main --tags`
4. Create a GitHub release and upload the zip as a release asset
5. Update `version`, `sha256`, and `url` in `Casks/magic-accessories-connector.rb` in the tap repo

### Full uninstall script (dev mode)

The `uninstall.sh` script handles both Cask-installed and source-run setups, prompting at each step:

```sh
./uninstall.sh           # interactive, prompts before each removal
./uninstall.sh --yes     # skip all prompts
./uninstall.sh --keep-blueutil  # leave blueutil installed
```

### How auto-reconnect works

```
unpair_device(address)
    │
    ▼
Open Bluetooth Settings   ← user puts device into pairing mode here
    │
    ▼
for attempt in 1..6 (every 2 seconds):
    pair_device(address)   ← succeeds once device is visible
        ├─ already paired? → skip pair, go straight to connect
        └─ not visible?    → wait, retry
    connect_device(address)
        └─ connected?      → notify success, done
    ▼
timeout → alert + manual pairing via open Bluetooth Settings window
```

### Environment variables

| Variable | Purpose |
|---|---|
| `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` | Prevents Cocoa crashes; set automatically by the Homebrew launcher and `install.sh` |
| `MAC_BLUEUTIL_PATH` | Override the path to the `blueutil` binary |

---

## License

MIT — see [LICENSE](LICENSE) if present, or assume free for personal and commercial use.
