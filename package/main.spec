# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from brainframe.cli.frozen_utils import RELATIVE_TRANSLATIONS_PATH, RELATIVE_DEFAULTS_FILE_PATH

# Package data files in with the executable
data_files = [
    (str(RELATIVE_DEFAULTS_FILE_PATH.absolute()),
     str(RELATIVE_DEFAULTS_FILE_PATH.parent)),
]
for file_ in RELATIVE_TRANSLATIONS_PATH.glob("*.yml"):
    data_files.append((str(file_.absolute()), str(file_.parent)))

a = Analysis(
    ["../brainframe/cli/main.py"],
    pathex=[".."],
    binaries=[],
    datas=data_files,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name="brainframe",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
