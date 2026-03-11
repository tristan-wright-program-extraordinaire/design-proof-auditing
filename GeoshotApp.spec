# -*- mode: python ; coding: utf-8 -*-

import os
import shutil

a = Analysis(
    ['src/index.py'],
    pathex=[],
    binaries=[],
    datas=[('./gui', 'gui'),('./python_sdk_tokens.txt','.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GeoshotApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GeoshotApp',
)
app = BUNDLE(
    coll,
    name='GeoshotApp.app',
    icon=None,
    bundle_identifier=None,
)

def copy_custom_lib_to_frameworks():
    src_folder = './.venv/lib/python3.9/site-packages/zohocrmsdk'

    dest_folder = os.path.join('dist', 'GeoshotApp.app', 'Contents', 'Frameworks', 'zohocrmsdk')

    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder)
    shutil.copytree(src_folder, dest_folder)

copy_custom_lib_to_frameworks()