@echo off
echo ========================================
echo 碳达峰预测系统启动脚本
echo ========================================

echo.
echo 正在启动后端服务...
cd backend
start "Carbon Peak Backend" cmd /k "python app.py"

echo.
echo 等待后端启动...
timeout /t 3 /nobreak >nul

echo.
echo 正在启动前端服务...
cd ..\frontend
start "Carbon Peak Frontend" cmd /k "npm run serve"

echo.
echo ========================================
echo 系统启动完成！
echo 前端地址: http://localhost:8080
echo 后端地址: http://127.0.0.1:5000
echo ========================================
echo.
echo 按任意键退出...
pause >nul
