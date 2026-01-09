@echo off
title VisualFlow - Iniciando...
echo.
echo ======================================
echo   VisualFlow - Script de Inicializacao
echo ======================================
echo.

REM Executar o script PowerShell
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"
