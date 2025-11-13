# 碳达峰预测系统

基于 LEAP 和 Kaya 模型的碳排放预测与情景分析系统。

## 功能特点

- **双模型预测**：支持 LEAP 模型和 Kaya 恒等式扩展模型
- **情景分析**：可创建和管理多种达峰情景（积极达峰、基准达峰等）
- **数据可视化**：交互式图表展示碳排放和能源消费趋势
- **历史数据分析**：基于历史数据的趋势分析和未来预测

## 技术栈

- **后端**：Flask + Pandas + NumPy
- **前端**：Vue.js + Chart.js
- **语言**：Python 3.8+ / JavaScript

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+

### 一键启动

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

启动后访问 `http://localhost:8080`

### 手动启动

**后端：**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py
```

**前端：**
```bash
cd frontend
npm install
npm run serve
```

## 使用说明

1. 访问 `http://localhost:8080`
2. 在情景管理页面创建或编辑预测情景
3. 上传历史数据或使用预置数据
4. 查看预测结果和可视化图表

## 项目结构

```
carbon_peak3/
├── backend/              # 后端服务
│   ├── app.py           # Flask 主程序
│   ├── model/           # LEAP & Kaya 预测模型
│   ├── data/            # 基准数据和情景配置
│   └── output/          # 预测结果输出
├── frontend/             # 前端应用
│   ├── src/             # Vue 组件和逻辑
│   └── public/          # 静态资源
├── start.bat            # Windows 启动脚本
└── start.sh             # Linux/Mac 启动脚本
```

## 开发者

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License
