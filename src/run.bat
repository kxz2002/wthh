@echo off
chcp 65001 >nul
echo ========================================
echo 家庭圈用户识别模型 - 快速启动
echo ========================================
echo.

echo [1/2] 检查依赖包...
python -c "import pandas, numpy, sklearn, flask, openpyxl, networkx" 2>nul
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
) else (
    echo 依赖包检查通过
)

echo.
echo [2/2] 运行主程序...
python main.py

echo.
echo ========================================
echo 处理完成！
echo ========================================
echo.
echo 要启动Web可视化界面，请运行: python app.py
echo.
pause

