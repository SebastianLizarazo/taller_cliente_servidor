@echo off
REM Script de inicio rápido para el cliente
REM Autor: Sistema de Inventario

echo ============================================================
echo INICIANDO CLIENTE DE INVENTARIO
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

REM Iniciar el cliente
python cliente.py

pause
