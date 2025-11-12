# 碳达峰预测系统 (Carbon Peak Prediction System)

这是一个基于LEAP和Kaya模型的碳达峰预测系统，用于分析和预测不同情景下的碳排放和能源消费情况。

## 项目概述

本系统提供了两种预测模型：
- **LEAP模型**：基于Long-range Energy Alternatives Planning系统的方法
- **Kaya模型**：基于Kaya恒等式的扩展模型

系统支持多种情景分析，包括积极达峰、基准达峰等不同情景，并提供了直观的可视化界面。

## 功能特点

- 多模型预测：支持LEAP和Kaya两种预测模型
- 情景管理：可以创建、编辑和删除不同的预测情景
- 数据可视化：提供碳排放和能源消费的图表展示
- 历史数据分析：基于历史数据进行趋势分析和预测

## 技术架构

- **后端**：Python Flask框架
- **前端**：Vue.js框架
- **数据处理**：Pandas、NumPy
- **可视化**：Chart.js

## 安装与运行

### 环境要求

- Python 3.8+
- Node.js 14+
- npm 6+

### 后端设置

1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 运行后端服务：
   ```bash
   python app.py
   ```

### 前端设置

1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 运行前端服务：
   ```bash
   npm run serve
   ```

### 快速启动

使用提供的脚本快速启动整个系统：

- Windows:
  ```bash
  start.bat
  ```

- Linux/Mac:
  ```bash
  ./start.sh
  ```

## 使用说明

1. 打开浏览器访问 `http://localhost:8080`
2. 在"情景管理"页面创建或编辑预测情景
3. 在"数据上传"页面上传历史数据
4. 在"预测结果"页面查看预测结果和图表

## 项目结构

```
carbon_peak3/
├── backend/                 # 后端代码
│   ├── app.py              # Flask应用主文件
│   ├── model/              # 预测模型
│   │   ├── kaya_model.py   # Kaya模型实现
│   │   └── leap_model.py   # LEAP模型实现
│   ├── data/               # 数据文件
│   └── output/             # 输出结果
├── frontend/               # 前端代码
│   ├── src/                # Vue源码
│   └── public/             # 静态资源
└── docs/                   # 文档
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 更新日志

### v1.0.0 (2024-XX-XX)
- 初始版本发布
- 实现LEAP和Kaya预测模型
- 添加情景管理功能
- 实现数据可视化界面