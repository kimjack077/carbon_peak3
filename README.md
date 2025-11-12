# 碳达峰预测系统

<div align="center">

![Carbon Peak Prediction System](https://img.shields.io/badge/Carbon%20Peak-Prediction%20System-green)
![Vue.js](https://img.shields.io/badge/Vue.js-2.6-4FC08D)
![Flask](https://img.shields.io/badge/Flask-2.0-000000)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB)
![License](https://img.shields.io/badge/License-MIT-blue)

基于LEAP模型算法的碳排放达峰预测系统，支持多情景分析和可视化展示

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [API文档](#api文档) • [贡献指南](#贡献指南)

</div>

## 📋 目录

- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [使用指南](#使用指南)
- [数据格式](#数据格式)
- [模型参数](#模型参数)
- [API文档](#api文档)
- [部署指南](#部署指南)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## ✨ 功能特性

### 🎯 核心功能
- **多情景预测**：支持创建和管理多个预测情景
- **碳达峰分析**：精确预测碳排放达峰时间和峰值
- **能源结构分析**：分析煤炭、电力、清洁能源占比变化
- **可视化展示**：交互式图表展示预测结果
- **数据导入导出**：支持CSV格式数据导入和结果导出

### 📊 分析能力
- **趋势预测**：基于历史数据预测未来发展趋势
- **情景对比**：多情景结果对比分析
- **敏感性分析**：参数变化对结果的影响分析
- **实时计算**：参数调整后实时重新计算

### 🔧 技术特性
- **响应式设计**：适配不同屏幕尺寸
- **实时更新**：数据和图表实时同步
- **错误处理**：完善的错误提示和处理机制
- **性能优化**：图表渲染和数据处理优化

## 🏗️ 技术架构

### 前端技术栈
- **Vue.js 2.6**：渐进式JavaScript框架
- **Element UI**：企业级UI组件库
- **ECharts 5.6**：数据可视化图表库
- **Axios**：HTTP客户端库

### 后端技术栈
- **Flask 2.0**：轻量级Web框架
- **Pandas**：数据分析和处理
- **NumPy**：科学计算库
- **Matplotlib**：数据可视化库

### 系统架构
```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Vue.js 前端   │ ◄──────────────► │   Flask 后端    │
│                 │                 │                 │
│ ├─ 数据上传     │                 │ ├─ API 接口     │
│ ├─ 情景管理     │                 │ ├─ 数据处理     │
│ ├─ 预测结果     │                 │ ├─ 模型计算     │
│ └─ 图表展示     │                 │ └─ 结果输出     │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   数据存储      │
                                    │                 │
                                    │ ├─ CSV 文件     │
                                    │ ├─ JSON 配置    │
                                    │ └─ 预测结果     │
                                    └─────────────────┘
```

## 🚀 快速开始

### 环境要求
- **Node.js** >= 14.0
- **Python** >= 3.8
- **npm** 或 **yarn**

### 1. 克隆项目
```bash
git clone https://github.com/your-username/carbon_peak.git
cd carbon_peak
```

### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
python app.py
```
后端将在 `http://127.0.0.1:5000` 启动

### 3. 启动前端
```bash
cd frontend
npm install
npm run serve
```
前端将在 `http://localhost:8080` 启动

### 4. 访问系统
打开浏览器访问 `http://localhost:8080`

## 📁 项目结构

```
carbon_peak/
├── 📁 frontend/                    # Vue.js 前端应用
│   ├── 📁 public/                  # 静态资源
│   ├── 📁 src/
│   │   ├── 📁 components/          # Vue 组件
│   │   │   ├── 📄 DataUpload.vue   # 数据上传组件
│   │   │   ├── 📄 ScenarioManager.vue # 情景管理组件
│   │   │   └── 📄 PredictionResults.vue # 预测结果组件
│   │   ├── 📄 App.vue              # 主应用组件
│   │   └── 📄 main.js              # 应用入口
│   ├── 📄 package.json             # 依赖配置
│   └── 📄 vue.config.js            # Vue 配置
├── 📁 backend/                     # Flask 后端应用
│   ├── 📁 data/                    # 数据文件目录
│   │   ├── 📄 scenarios.json       # 情景配置
│   │   ├── 📄 base_year_data.csv   # 基准年数据
│   │   └── 📄 sample_data.csv      # 示例数据
│   ├── 📁 model/                   # 预测模型
│   │   ├── 📄 data_processor.py    # 数据处理
│   │   ├── 📄 energy_demand.py     # 能源需求预测
│   │   ├── 📄 carbon_emission.py   # 碳排放计算
│   │   └── 📄 scenario_runner.py   # 情景运行器
│   ├── 📁 output/                  # 输出结果目录
│   ├── 📁 utils/                   # 工具函数
│   │   └── 📄 plot_results.py      # 图表生成
│   ├── 📄 app.py                   # Flask 主应用
│   └── 📄 requirements.txt         # Python 依赖
├── 📄 README.md                    # 项目文档
└── 📄 .gitignore                   # Git 忽略文件
```

## 📖 使用指南

### 1. 数据上传
- 支持CSV格式的历史数据上传
- 提供示例数据快速开始
- 数据验证和格式检查

### 2. 情景管理
- 创建多个预测情景
- 设置关键参数（GDP增长率、人口增长率等）
- 删除和修改现有情景

### 3. 运行预测
- 选择要运行的情景
- 设置预测年数（5-100年）
- 实时查看预测进度

### 4. 结果分析
- 碳排放达峰预测图表
- 能源结构变化分析
- 详细数据表格展示
- 结果导出功能

## 📊 数据格式

### 输入数据格式
系统接受CSV格式的基准年数据，包含以下字段：

```csv
year,sector,population,gdp,energy_intensity,energy_share_coal,energy_share_elec
2020,工业,140000,10.5,1.2,0.65,0.25
2020,交通,140000,10.5,0.8,0.45,0.35
2020,建筑,140000,10.5,0.6,0.30,0.50
2020,其他,140000,10.5,0.4,0.20,0.60
```

### 字段说明
- **year**: 年份
- **sector**: 部门（工业、交通、建筑、其他）
- **population**: 人口（万人）
- **gdp**: GDP（万亿元）
- **energy_intensity**: 能源强度（万吨标煤/万亿元）
- **energy_share_coal**: 煤炭占比（0-1）
- **energy_share_elec**: 电力占比（0-1）

## ⚙️ 模型参数

### 核心参数
- **GDP增长率**：影响未来经济发展速度
  - 范围：0-20%
  - 默认：5%/年
  - 示例：0.05表示5%/年

- **人口增长率**：影响未来人口规模
  - 范围：-2%-5%
  - 默认：-0.99%/年（反映中国当前人口下降趋势）
  - 示例：-0.0099表示-0.99%/年

- **能效提升率**：影响单位GDP能耗下降速度
  - 范围：0-10%
  - 默认：2%/年
  - 示例：0.02表示2%/年

- **煤炭占比降低率**：影响能源结构调整速度
  - 范围：0-10%
  - 默认：2%/年
  - 示例：0.02表示2%/年

### 预测方法
- **线性回归**：基于历史趋势的线性预测
- **指数平滑**：考虑近期数据权重的平滑预测

## 🔌 API文档

### 基础信息
- **Base URL**: `http://127.0.0.1:5000/api`
- **Content-Type**: `application/json`

### 主要接口

#### 1. 数据上传
```http
POST /upload
Content-Type: multipart/form-data

参数：
- file: CSV文件

响应：
{
  "message": "File uploaded successfully",
  "years": [2020, 2021, 2022],
  "sectors": ["工业", "交通", "建筑", "其他"],
  "rows": 12
}
```

#### 2. 情景管理
```http
# 创建情景
POST /scenarios
{
  "name": "情景名称",
  "gdp_growth_rate": 0.05,
  "population_growth_rate": -0.0099,
  "efficiency_improvement_rate": 0.02,
  "coal_reduction_rate": 0.02,
  "trend_method": "linear_regression"
}

# 获取所有情景
GET /scenarios

# 删除情景
DELETE /scenarios/{scenario_name}
```

#### 3. 预测运行
```http
POST /predict
{
  "scenarios": ["情景1", "情景2"],
  "forecast_years": 30
}
```

#### 4. 结果获取
```http
# 获取预测结果
GET /results/{scenario_name}

# 获取图表数据
GET /chart-data

# 下载结果
GET /results/{scenario_name}/download
```

## 🚀 部署指南

### 开发环境
按照[快速开始](#快速开始)部分的说明即可

### 生产环境

#### 前端部署
```bash
cd frontend
npm run build
# 将 dist/ 目录部署到 Web 服务器
```

#### 后端部署
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Docker 部署
```dockerfile
# Dockerfile 示例
FROM python:3.8-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

## ❓ 常见问题

### Q: 图表显示异常或缩在左侧？
A: 这通常是图表初始化时容器尺寸问题，系统已内置多重resize机制，刷新页面或切换tab即可恢复。

### Q: 人口增长率可以设置负数吗？
A: 可以，系统支持-2%到5%的人口增长率，负数表示人口下降，符合中国当前实际情况。

### Q: 预测结果不准确怎么办？
A: 预测准确性取决于输入数据质量和参数设置，建议：
- 使用高质量的历史数据
- 根据实际情况调整参数
- 创建多个情景进行对比分析

### Q: 如何导出预测结果？
A: 在预测结果页面点击"下载数据"按钮，或使用API接口下载CSV格式结果。

## 🤝 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 前端：遵循 Vue.js 官方风格指南
- 后端：遵循 PEP 8 Python 代码规范
- 提交信息：使用清晰的提交信息

### 问题反馈
- 使用 GitHub Issues 报告 bug
- 提供详细的复现步骤
- 包含系统环境信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页：[GitHub Repository](https://github.com/your-username/carbon_peak)
- 问题反馈：[GitHub Issues](https://github.com/your-username/carbon_peak/issues)
- 邮箱：your-email@example.com

---

<div align="center">

**如果这个项目对您有帮助，请给它一个 ⭐️**

Made with ❤️ by [Your Name]

</div>
