# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from brainframe.cli.frozen_utils import RELATIVE_TRANSLATIONS_PATH


assert Path("brainframe").is_dir(), \
    "PyInstaller must be run from the root directory of the project"

# Package translation files in with the executable
data_files = []
for file_ in RELATIVE_TRANSLATIONS_PATH.glob("*.yml"):
    data_files.append((str(file_.absolute()), str(file_.parent)))

a = Analysis(["../brainframe/cli/main.py"],
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
             noarchive=False)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=None)

exe = EXE(pyz,
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
          console=True )
