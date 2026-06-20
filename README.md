# 碳管理预测分析平台

> 基于 LEAP、Kaya & STIRPAT 三模型情景模拟的碳排放预测与分析系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-2.x-brightgreen.svg)](https://vuejs.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-red.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🔗 **在线演示**：[http://49.232.213.79:56789](http://49.232.213.79:56789)

## 产品简介

碳管理预测分析平台面向企业碳资产管理人员，通过历史能耗数据建立三模型预测体系（LEAP、Kaya、STIRPAT），支持多情景分析与碳达峰时间识别，为企业碳中和路径规划提供科学决策支持。

**核心价值：**

- **双模型并行** — LEAP 和 Kaya 两种算法交叉验证，提升预测可信度
- **情景驱动决策** — 支持多情景自定义配置，对比不同路径下的碳排放轨迹
- **可视化洞察** — 直观展示碳达峰时间、能源结构演变、产值增长趋势
- **合规支撑** — 输出可用于碳报告和监管申报的标准化数据

## 功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| M01 数据管理 | 历史数据管理（2022-2024年），支持 CSV 上传和预置数据 | ✅ |
| M02 情景配置 | 创建/编辑/删除/对比情景，支持 LEAP 和 Kaya 模型选择 | ✅ |
| M03 LEAP 引擎 | 长期能源替代规划模型，自底向上能源供需结构预测 | ✅ |
| M04 Kaya 引擎 | 卡亚恒等式模型，GDP × 能源强度 × 碳强度分解分析 | ✅ |
| M06 碳排放图 | 多情景碳排放曲线叠加，标注碳达峰点 | ✅ |
| M07 产值趋势 | 工业总产值增长预测折线图 | ✅ |
| M08 能耗结构 | 可再生/非可再生能源堆叠柱状图 | ✅ |
| M09 数据表格 | 逐年预测数据明细，支持导出 CSV | ✅ |
| M10 情景对比 | 情景参数横向对比面板 | ✅ |

## 模型说明

### LEAP 模型（长期能源替代规划）

自底向上能源-环境-经济综合模型，通过分析能源供需结构演变预测未来能耗与排放。

```
碳排放 = 能源消费量 × 碳排放因子 × (1 - 可再生能源占比)

逐年迭代：
1. GDP(t) = GDP(t-1) × (1 + 产值增长率)
2. EI(t) = EI(t-1) × (1 - 能效改善率)
3. E(t) = GDP(t) × EI(t)
4. R(t) = min(R(t-1) + 可再生提升率, 0.95)
5. C(t) = E(t) × f₀ × (1 - R(t))
```

### Kaya 模型（卡亚恒等式）

自顶向下恒等式分解模型，将碳排放分解为产值、能源强度、碳强度三个驱动因子。

```
CO₂(t) = GDP(t) × EI(t) × CI(t)

其中：
- GDP(t) = 工业总产值（现价）
- EI(t)  = 能源强度 = 能源消费量 / 产值
- CI(t)  = 碳强度 = f₀ × (1 - R(t))
```

### 模型对比

| 维度 | LEAP | Kaya |
|------|------|------|
| 理论框架 | 自底向上，能源供需结构 | 自顶向下，恒等式分解 |
| 适用场景 | 能源政策分析、供需预测 | 因子贡献分解、政策效果量化 |
| 优势 | 考虑能源结构细节 | 逻辑清晰，便于理解 |
| 参数敏感性 | 能效改善率、可再生能源占比 | 产值增长率、能源强度 |

## 情景参数

| 参数 | 字段名 | 取值范围 | 默认值 | 说明 |
|------|--------|----------|--------|------|
| 情景名称 | scenario_name | 1-50字 | 情景1 | 用户自定义标识 |
| 模型选择 | model_type | LEAP / Kaya | LEAP | 选择预测算法 |
| 产值增长率 | gdp_growth_rate | -5% ~ 20% | 5% | 年均工业总产值增长率 |
| 能效改善率 | efficiency_improvement_rate | 0% ~ 15% | 3% | 单位产值能耗年下降率 |
| 可再生能源提升率 | renewable_increase_rate | 0% ~ 8% | 1% | 可再生能源占比年提升百分点 |
| 煤炭占比下降率 | coal_decrease_rate | 0% ~ 15% | 2% | 煤炭占比年下降百分点 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│  前端 (Vue.js 2 + Element UI + ECharts)                      │
│  ├── DataUpload.vue     数据上传与管理                        │
│  ├── ScenarioManager.vue 情景配置与管理                       │
│  └── PredictionResults.vue 可视化图表与数据表格               │
└─────────────────────────────────────────────────────────────┘
                            ↕ REST API
┌─────────────────────────────────────────────────────────────┐
│  后端 (Flask + Pandas + NumPy)                               │
│  ├── app.py             REST API 端点                        │
│  ├── model/                                                 │
│  │   ├── simplified_leap.py    LEAP 模型引擎                 │
│  │   ├── simplified_kaya.py    Kaya 模型引擎                 │
│  │   ├── stirpat_model.py      STIRPAT 弹性系数模型          │
│  │   └── simple_scenario_runner.py 统一预测接口              │
│  └── data/                                                  │
│      ├── base_year_data.csv   基准年数据                     │
│      └── scenarios.json       情景配置存储                   │
└─────────────────────────────────────────────────────────────┘
```

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

## 使用流程

1. **上传数据** — 上传 CSV 历史数据或使用系统预置的示例数据
2. **创建情景** — 配置模型类型和预测参数，可创建多个情景
3. **运行预测** — 点击"开始预测"按钮，批量计算所有情景
4. **分析结果** — 查看碳排放曲线、产值趋势、能耗结构图表
5. **识别达峰** — 图表自动标注各情景的碳达峰年份
6. **导出数据** — 下载图表（PNG）或导出预测数据（CSV）

## CSV 数据格式

系统要求 CSV 文件包含以下列：

| 列名 | 说明 | 必需 |
|------|------|------|
| year | 年份 | ✅ |
| energy_consumption | 综合能源消费量（万吨标准煤） | ✅ |
| gdp | 工业总产值（万元） | ✅ |
| co2_emission | CO₂排放量（万吨CO₂当量） | ✅ |
| renewable_ratio | 可再生能源占比（可选） | ❌ |
| coal_ratio | 煤炭占比（可选） | ❌ |

## 项目结构

```
carbon_peak3/
├── backend/                    # 后端服务
│   ├── app.py                 # Flask REST API
│   ├── model/                 # 预测模型
│   │   ├── simplified_leap.py # LEAP 模型
│   │   ├── simplified_kaya.py # Kaya 模型
│   │   ├── stirpat_model.py   # STIRPAT 模型
│   │   └── simple_scenario_runner.py
│   ├── data/                  # 数据文件
│   │   ├── base_year_data.csv # 基准年数据
│   │   └── scenarios.json     # 情景配置
│   └── output/                # 预测结果输出
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── App.vue            # 主应用
│   │   ├── components/        # Vue 组件
│   │   └── utils/api.js       # API 接口
│   └── public/
├── start.bat                   # Windows 启动脚本
├── start.sh                    # Linux/Mac 启动脚本
└── 碳管理预测分析平台_PRD_v1.0.md  # 产品需求文档
```

## 预设情景参考

| 情景名称 | 模型 | 产值增长率 | 能效改善率 | 可再生能源提升率 | 描述 |
|----------|------|-----------|-----------|----------------|------|
| 基准情景 | Kaya | 5% | 2% | 0.5%/年 | 延续历史趋势 |
| 政策加速情景 | LEAP | 5% | 4% | 2%/年 | 大力推进能效改造 |
| 高增长情景 | Kaya | 8% | 1% | 0.3%/年 | 产值快速扩张 |
| 碳中和路径 | LEAP | 4% | 6% | 3%/年 | 激进减碳路径 |
| 保守情景 | Kaya | 3% | 1.5% | 0.5%/年 | 经济增速放缓 |

## 开发

```bash
# 后端测试
cd backend
pytest

# 前端检查
cd frontend
npm run lint

# E2E 测试
npm run test:e2e
```

## 参与贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License

---

*碳管理预测分析平台 © 2025*
