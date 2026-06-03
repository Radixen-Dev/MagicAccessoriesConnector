# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None
project_root = Path(__file__).parent.resolve()

blueutil_src = project_root / "third_party" / "blueutil"
binaries = []
if blueutil_src.exists():
    binaries.append((str(blueutil_src), "."))


a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    bundle_identifier='com.example.magicaccessoriesconnector',
)
