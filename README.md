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
- **Auto-start at login** — register as a login item with a single `brew services` command

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
brew install magic-accessories-connector
```

That's it. Homebrew downloads and installs everything, including the `blueutil` dependency.

---

### Start the app

**Run once (current session only):**

```sh
magic-accessories-connector
```

**Start automatically at every login (recommended):**

```sh
brew services start magic-accessories-connector
```

After either command, a **MAC** icon appears in your menu bar.

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

To remove **everything** — the app, its login item, and all saved preferences:

```sh
brew services stop magic-accessories-connector
brew uninstall magic-accessories-connector
rm -rf ~/Library/Application\ Support/MagicAccessoriesConnector
```

The three commands do the following, in order:

1. **Stop the service** — removes the LaunchAgent so the app no longer starts at login
2. **Uninstall the formula** — removes the app binary and its Python virtualenv from Homebrew's Cellar
3. **Remove saved preferences** — deletes the app data folder

> `brew uninstall` does **not** remove the service log. To remove it too:
> ```sh
> rm -f $(brew --prefix)/var/log/magic-accessories-connector.log
> ```
> After that, nothing else is left on your machine.

If you also want to remove `blueutil` (the Bluetooth CLI that MAC depends on):

```sh
brew uninstall blueutil
```

Only do this if nothing else on your system uses it.

---

## Troubleshooting

### The MAC icon doesn't appear in the menu bar

macOS limits the number of visible menu bar icons. Try scrolling or checking in **System Settings → Control Center** to see if it's hidden. If using Bartender or a similar tool, check its hidden items tray.

### "blueutil not found" appears in the menu

Homebrew may not be on your `PATH` in the login session. Try:

```sh
brew doctor
```

If blueutil is missing entirely:

```sh
brew install blueutil
```

Then click **Refresh** in the MAC menu.

### Auto-reconnect always times out

The retry window is ~12 seconds. If your device takes longer to enter pairing mode, pair it manually through the Bluetooth Settings window that opens automatically. The device will be paired after that and will appear again in the MAC menu.

### The app crashes or the menu is blank

Check the service log:

```sh
tail -50 $(brew --prefix)/var/log/magic-accessories-connector.log
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
install.sh        — dev quick-start script
uninstall.sh      — full removal script (handles both Homebrew and source installs)
build.sh          — PyInstaller standalone .app builder (for future binary releases)
MagicAccessoriesConnector.spec — PyInstaller bundle configuration
```

### Full uninstall script (dev mode)

The `uninstall.sh` script handles both Homebrew-installed and source-run setups, prompting at each step:

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
