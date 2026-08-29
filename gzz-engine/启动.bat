@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Gzz 编码引擎
echo.
echo ==========================================
echo   Gzz 编码引擎 v1.1  事现鉴 SXJ 编码体系
echo ==========================================
echo.
python gzz_cli.py %*
pause
