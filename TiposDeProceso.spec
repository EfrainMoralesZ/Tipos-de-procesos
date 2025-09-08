# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ProcesosV2.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img'), ('resources', 'resources'), ('theme', 'theme'), ('Dar Formato JSON', 'Dar Formato JSON'), ('Guardar Archivos Generados', 'Guardar Archivos Generados'), ('archivos', 'archivos')],
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
