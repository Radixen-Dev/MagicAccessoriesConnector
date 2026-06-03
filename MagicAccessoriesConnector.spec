# -*- mode: python ; coding: utf-8 -*-
# Distributes as a Homebrew Cask — blueutil is a declared Homebrew dependency,
# not bundled inside the .app.

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MagicAccessoriesConnector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
app = BUNDLE(
    exe,
    name='MagicAccessoriesConnector.app',
    icon=None,
    bundle_identifier='dev.radixen.magic-accessories-connector',
    info_plist={
        'CFBundleName': 'MagicAccessoriesConnector',
        'CFBundleDisplayName': 'Magic Accessories Connector',
        'CFBundleShortVersionString': '1.2.0',
        'CFBundleVersion': '1.2.0',
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'NSBluetoothAlwaysUsageDescription': 'Magic Accessories Connector needs Bluetooth access to forget and reconnect your Magic devices.',
    },
)
