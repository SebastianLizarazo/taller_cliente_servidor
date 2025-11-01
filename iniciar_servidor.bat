@echo off
REM Script de inicio rápido para el servidor
REM Autor: Sistema de Inventario

echo ============================================================
echo INICIANDO SERVIDOR DE INVENTARIO
echo ============================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.7 o superior
    pause
    exit /b 1
)

echo Python detectado:
python --version
echo.

REM Mostrar IP del equipo
echo Tu IP local es:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do echo   %%a
echo.

echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar el servidor
python servidor.py

pause
