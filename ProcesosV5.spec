# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

# Archivos semilla que ProcesosV5.inicializar_datos_externos() copia junto al .exe
# la primera vez que se ejecuta. No se empaquetan los debug_*.json ni el historial.
ARCHIVOS_DATOS = [
    'codigos_cumple.xlsx',
    'base_general.json',
    'codigos_cumple.json',
    'config.json',
    'reglas.json',
]
datas = [(os.path.join('Datos', f), 'datos') for f in ARCHIVOS_DATOS
         if os.path.exists(os.path.join('Datos', f))]

# Imágenes (logo, logo empresarial e ícono de ventana)
datas += [
    ('img/icono.ico', 'img'),
    ('img/Logo.png', 'img'),
    ('img/logo_empresarial.png', 'img'),
]

# Temas y recursos de customtkinter
datas += collect_data_files('customtkinter')


a = Analysis(
    ['ProcesosV5.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Módulos propios que se importan dentro de funciones
        'Configurar',
        'Dashboard',
        'Reglas',
        'Editor_Codigos',
        # Motores de pandas.read_excel / to_excel
        'openpyxl',
        'xlrd',
    ],
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
    name='ProcesosV5',
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
