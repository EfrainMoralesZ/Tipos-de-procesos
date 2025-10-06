# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ProcesosV3.py'],
    pathex=[],
    binaries=[],
    datas=[('datos\\codigos_cumple.xlsx', 'datos'), ('datos\\base_general.json', 'datos'), ('datos\\codigos_cumple.json', 'datos'), ('datos\\config.json', 'datos'), ('img', 'img')],
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
    a.binaries,
    a.datas,
    [],
    name='TiposDeProceso',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['img\\icono.ico'],
)
