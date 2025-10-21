@echo off
echo 推送项目到GitHub
echo ==================

REM 请将下面的GitHub用户名替换为您自己的用户名
set GITHUB_USERNAME=your-github-username
set REPO_NAME=net-lease-line-monitor

echo 请确保您已经在GitHub上创建了名为 %REPO_NAME% 的仓库
echo 如果还没有创建，请先在 https://github.com/new 上创建
pause

echo 设置远程仓库...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo 推送代码到GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo 推送成功！
    echo 您可以通过以下链接访问您的仓库：
    echo https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
) else (
    echo.
    echo 推送失败，请检查：
    echo 1. 是否已在GitHub上创建了仓库
    echo 2. GitHub用户名是否正确
    echo 3. 网络连接是否正常
)

pause