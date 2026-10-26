@echo off
REM ============================================================
REM  Compila ProcesosV5 en un solo .exe usando ProcesosV5.spec
REM  Resultado: dist\ProcesosV5.exe
REM ============================================================
setlocal
chcp 65001 >nul
cd /d "%~dp0"

REM --- Usar entorno virtual si existe ---
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

REM --- Verificar Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro Python en el PATH.
    pause
    exit /b 1
)

REM --- Verificar / instalar PyInstaller ---
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no esta instalado. Instalando...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar PyInstaller.
        pause
        exit /b 1
    )
)

REM --- Cerrar los .exe de dist si estan abiertos (si no, no se pueden borrar) ---
for %%F in ("dist\*.exe") do taskkill /f /im "%%~nxF" >nul 2>&1

REM --- Limpiar compilaciones anteriores ---
REM     Se borran todos los .exe de dist (incluye versiones viejas como ProcesosV4.exe);
REM     la carpeta dist\datos se conserva.
echo Limpiando compilaciones anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist\*.exe" del /f /q "dist\*.exe"

REM --- Compilar ---
echo.
echo Compilando ProcesosV5...
python -m PyInstaller --noconfirm --clean ProcesosV5.spec
if errorlevel 1 (
    echo.
    echo [ERROR] La compilacion fallo. Revisa los mensajes de arriba.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Compilacion terminada: dist\ProcesosV5.exe
echo  Al ejecutarse por primera vez crea la carpeta "datos"
echo  junto al .exe con los archivos iniciales.
echo ============================================================
pause
endlocal
