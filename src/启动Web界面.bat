@echo off
chcp 65001 >nul
echo ========================================
echo 启动家庭圈用户识别系统 - Web界面
echo ========================================
echo.
echo 正在启动Web服务器...
echo 启动后请在浏览器中访问: http://127.0.0.1:5000
echo.
echo 按 Ctrl+C 停止服务器
echo.
python app.py

