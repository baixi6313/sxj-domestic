@echo off
chcp 65001 >nul
echo === SXJ 国内版推送脚本 ===
echo.

cd /d "C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn_domestic"

set /p MSG=请输入本次更新说明：
if "%MSG%"=="" set MSG=Update SXJ domestic version

git add -A
git commit -m "%MSG%"
git push origin main

echo.
echo === 推送完成 ===
echo 1-2分钟后网站将自动更新
echo 访问：https://baixi6313.github.io/sxj-domestic/
pause
