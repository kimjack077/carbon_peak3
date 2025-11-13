@echo off
echo ========================================
echo   简化版碳达峰预测系统启动脚本
echo ========================================
echo.

echo [1/2] 启动后端服务 (端口 5001)...
start "碳达峰预测-后端(简化版)" cmd /k "python simple_app.py"
timeout /t 3 /nobreak > nul

echo [2/2] 启动前端服务 (端口 8080)...
start "碳达峰预测-前端" cmd /k "cd frontend && npm run serve"
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 后端地址: http://localhost:5001
echo 前端地址: http://localhost:8080
echo.
echo 请等待服务启动完成后，在浏览器中访问前端地址
echo 选择"简化版预测"标签页开始使用
echo.
echo 按任意键关闭此窗口...
pause > nul
