@echo off
chcp 65001 >nul
echo ========================================
echo   需求结构化分析管道 v5.2
echo   Requirements Structuring Pipeline
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python环境检查通过
echo.

echo [2/3] 检查依赖...
if not exist "requirements.txt" (
    echo ⚠️  警告: 未找到requirements.txt
) else (
    echo ✅ 依赖清单存在
)
echo.

echo [3/3] 启动Streamlit UI...
echo.
echo ========================================
echo   启动中，请稍候...
echo   访问地址以 boot.py 输出为准
echo ========================================
echo.

python interfaces\boot.py ui

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，请检查错误信息
    pause
)
