#!/bin/bash

echo "========================================"
echo "碳达峰预测系统启动脚本"
echo "========================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "错误: npm 未安装"
    exit 1
fi

echo ""
echo "正在启动后端服务..."
cd backend

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 启动后端
echo "启动Flask服务器..."
python app.py &
BACKEND_PID=$!

echo ""
echo "等待后端启动..."
sleep 3

echo ""
echo "正在启动前端服务..."
cd ../frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装Node.js依赖..."
    npm install
fi

# 启动前端
echo "启动Vue开发服务器..."
npm run serve &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "系统启动完成！"
echo "前端地址: http://localhost:8080"
echo "后端地址: http://127.0.0.1:5000"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
