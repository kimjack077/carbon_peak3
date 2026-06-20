# 碳管理预测分析平台
## 基于 LEAP、Kaya & STIRPAT 三模型情景模拟系统
### 产品需求文档（PRD）v2.0

| 文档属性 | 内容 |
|---|---|
| 文档版本 | v2.0（基于代码实现更新） |
| 编制日期 | 2025年 |
| 适用对象 | 开发部、产品部、数据科学团队 |
| 数据来源 | 企业 2019–2024 年能耗与产值年报 |
| 保密级别 | 公司内部机密 |

---

## 目录

1. [文档说明与背景](#1-文档说明与背景)
2. [产品概述](#2-产品概述)
3. [算法规格详解](#3-算法规格详解)
4. [功能需求](#4-功能需求)
5. [可视化需求详细规格](#5-可视化需求详细规格)
6. [页面结构与交互流程](#6-页面结构与交互流程)
7. [API 接口规格](#7-api-接口规格)
8. [数据规格](#8-数据规格)
9. [非功能需求](#9-非功能需求)
10. [技术架构](#10-技术架构)
11. [验收标准](#11-验收标准)
- [附录 A：情景参数影响机制说明](#附录-a情景参数影响机制说明)
- [附录 B：预设情景建议](#附录-b预设情景建议)

---

## 1. 文档说明与背景

### 1.1 编写目的

本文档为"碳管理预测分析平台"的产品需求说明书，旨在为开发团队提供完整、清晰、可执行的功能规格与技术要求，确保系统按期高质量交付。

本平台面向企业碳资产管理人员，通过历史能耗数据建立三模型预测体系（LEAP、Kaya、STIRPAT），支持多情景分析与碳达峰时间识别，为企业碳中和路径规划提供科学决策支持。

### 1.2 背景与动机

我国已明确提出"2030年前碳达峰、2060年前碳中和"的双碳目标。作为高能耗企业，需要：

- 量化未来碳排放轨迹，识别碳达峰时间节点
- 模拟不同政策情景下的排放变化
- 制定科学的能源结构转型策略
- 满足监管机构对碳核查与信息披露的合规要求

本系统基于 2019-2024 年历史数据进行建模，使用 LEAP、Kaya 和 STIRPAT 三种主流算法进行情景推演。

### 1.3 核心数据

本系统使用以下关键数据字段：

| 年份 | 综合能源消费量（万吨标准煤） | 工业总产值（万元） | CO₂排放量（万吨） | 可再生能源占比 |
|---|---|---|---|---|
| 2019年 | 1,370 | 6,973,354 | 6,638 | 12% |
| 2020年 | 1,046 | 6,678,682 | 4,893 | 13% |
| 2021年 | 1,120 | 8,100,000 | 5,100 | 14% |
| 2022年 | 980.15 | 8,878,583 | 4,818.77 | 15% |
| 2023年 | 1,098.94 | 9,961,672 | 5,351.33 | 16% |
| 2024年 | 1,081.95 | 10,404,978 | 5,273.54 | 17% |

### 1.4 术语说明

| 术语 | 定义 |
|---|---|
| 碳达峰 | 二氧化碳排放量在某年达到历史最高值，此后持续下降的转折点 |
| LEAP 模型 | Long-range Energy Alternatives Planning System，长期能源替代规划系统 |
| Kaya 模型 | Kaya Identity，碳排放恒等式分解模型（卡亚恒等式） |
| STIRPAT 模型 | Stochastic Impacts by Regression on Population, Affluence, and Technology，随机回归人口-富裕-技术模型 |
| 情景 | 在设定的一组假设参数下，对未来状态的一种可能性描述 |
| 能源效率改善率 | 单位产值所消耗的能源量每年下降的百分比 |
| 可再生能源占比提升率 | 可再生能源在综合能源消费中所占比例每年提升的百分点 |
| 煤炭占比下降率 | 煤炭在能源消费中占比每年下降的百分点 |
| 碳排放因子 | 消耗单位能源所产生的CO₂排放量 |
| 能源强度 | 单位工业总产值所消耗的综合能源量（万吨标准煤/万元） |
| 碳强度 | 单位工业总产值所产生的CO₂排放量（万吨CO₂/万元） |
| 弹性系数 | STIRPAT 模型中各驱动因子对碳排放的弹性（对数回归系数） |

---

## 2. 产品概述

### 2.1 产品定位

本平台定位为企业级碳排放预测与情景分析工具，核心价值在于：

- **三模型并行**：同时运行 LEAP、Kaya、STIRPAT 三种算法，交叉验证预测结果
- **情景驱动决策**：支持多情景自定义配置，对比不同路径下的碳排放轨迹
- **可视化洞察**：直观展示碳达峰时间、能源结构演变、产值增长趋势
- **AI 辅助决策**：基于历史数据趋势自动推荐参数，降低使用门槛
- **合规支撑**：输出可用于碳报告和监管申报的标准化数据

### 2.2 目标用户

| 用户角色 | 职责 | 主要使用场景 |
|---|---|---|
| 碳资产管理员 | 负责企业碳账本管理与排放核算 | 数据录入、情景设置、报告导出 |
| 战略规划分析师 | 制定企业中长期低碳转型战略 | 情景对比、碳达峰路径分析 |
| 能源管理工程师 | 优化能源消费结构与效率 | 能耗预测、能源结构分析 |
| 高层管理者 | 决策层审阅碳管理成效 | 查看汇总图表与达峰时间 |
| 合规/监管对接人员 | 对接外部监管和碳核查 | 导出标准报告 |

### 2.3 产品范围

**本期（v2.0）范围：**

- 历史数据管理（支持 CSV/Excel 上传，2019-2024 年数据）
- LEAP 模型情景模拟引擎
- Kaya 模型情景模拟引擎
- STIRPAT 模型情景模拟引擎（含弹性系数自动标定）
- 情景配置与管理（创建、复制、删除、对比）
- AI 参数推荐（基于历史趋势分析）
- 碳排放折线图（多情景叠加，标注碳达峰点）
- 工业总产值趋势图
- 能耗结构柱状图（含可再生/非可再生能源分拆）
- 情景对比面板（雷达图 + 对比表格）
- 数据明细表格（支持导出 CSV/Excel）
- 暗色/亮色主题切换

**本期不包含：** 外部数据接口、碳交易模块、移动端 App、多企业对比、PDF 报告导出（当前为 JSON 摘要）。

---

## 3. 算法规格详解

### 3.1 公共预测管道（prediction_utils.py）

三个模型共享一套预测基础设施，确保结果的一致性和可比性。

#### 3.1.1 驱动路径生成（driver_paths）

GDP 和能效采用 **smoothstep 过渡** 策略，平滑连接近期和远期增长率：

```
# GDP 增长路径
near_term_years = gdp_transition_years (默认 15 年)
远期增长率 = long_term_gdp_growth_rate (默认为近期增长率的 60%)

smoothstep(x) = 3x² - 2x³  (x ∈ [0, 1])
transition_weight = smoothstep(year / near_term_years)
applied_rate = near_term_rate × (1 - weight) + long_term_rate × weight

GDP(t) = GDP(t-1) × (1 + applied_rate)
```

能效改善率采用相同逻辑，过渡年数默认 12 年。

#### 3.1.2 能源结构路径（structure_paths）

可再生能源占比采用 **饱和指数曲线** 逼近目标值：

```
renewable_ratio(t) = target - (target - base) × decay^year
decay = 0.92 (每 5 年约减半差距)
target = min(base + renewable_increase_rate × forecast_years × 1.5, 0.95)
```

煤炭占比采用指数衰减逼近下限：

```
coal_ratio(t) = max(coal_floor, base × (1 - coal_decrease_rate)^year)
coal_floor = max(0.02, base_coal_ratio × 0.2)
```

#### 3.1.3 碳排放路径约束

为避免极端参数导致不合理的预测，系统施加年度排放变化约束：

| 约束 | 默认值 | 说明 |
|---|---|---|
| max_annual_emission_increase | 8% | 单年碳排放最大增幅 |
| max_annual_emission_decline | 12% | 单年碳排放最大降幅 |
| carbon_factor_decline_rate | 自动计算 | 碳排放因子年下降率上限 |

#### 3.1.4 碳达峰标注（annotate_peak）

```
peak_year = max(co2_emission) 对应年份

判断逻辑：
- 若 peak_year 不在最后一年 → status = "reached"（已达峰）
- 若 peak_year 在最后一年且末期排放 > 初始排放 × 1.005 → status = "not_reached"（未达峰）
- 若 peak_year 在第一年（基准年） → status = "base_year_peak"（基准年已达峰）
- 容差阈值：0.5%
```

---

### 3.2 LEAP 模型（长期能源替代规划模型）

#### 3.2.1 理论基础

LEAP（Long-range Energy Alternatives Planning System）是自底向上能源-环境-经济综合模型。本系统采用简化版本，通过燃料结构动力学预测碳排放。

#### 3.2.2 核心公式

```
CO₂(t) = calibration × carbon_multiplier(t) × [coal_energy(t) × 2.66 + other_fossil_energy(t) × 1.876]

其中：
  calibration = (base_co2 / base_energy) / base_fuel_factor  （锚定真实数据）
  carbon_multiplier(t) = (1 - carbon_factor_decline_rate)^t  （碳排放因子自然下降）

  coal_energy(t) = total_energy(t) × coal_ratio(t)
  other_fossil_energy(t) = total_energy(t) × (1 - renewable_ratio(t) - coal_ratio(t))
  total_energy(t) = GDP(t) × energy_intensity(t)

  OTHER_FOSSIL_EMISSION_FACTOR = 2.12 × 0.6 + 1.51 × 0.4 = 1.876
  （油品排放因子 2.12，权重 60%；天然气 1.51，权重 40%）
```

#### 3.2.3 排放因子

| 燃料类型 | 排放因子 (tCO₂/单位) | 说明 |
|---|---|---|
| 煤炭 | 2.66 | 固定值 |
| 油品 | 2.12 | 权重 60% |
| 天然气 | 1.51 | 权重 40% |
| 其他化石燃料 | 1.876 | 油品×0.6 + 天然气×0.4 |
| 可再生能源 | 0 | 零碳排放 |

---

### 3.3 Kaya 模型（卡亚恒等式模型）

#### 3.3.1 理论基础

Kaya 恒等式由日本学者茅阳一（Yoichi Kaya）于 1990 年提出，将碳排放分解为驱动因子的乘积。本系统采用简化版本，不考虑人口因子。

#### 3.3.2 核心公式

```
CO₂(t) = Energy(t) × Carbon_Intensity(t)

其中：
  Carbon_Intensity(t) = base_CI × (structure_index(t) / structure_index(base)) × carbon_multiplier(t)

  structure_index(t) = (1 - renewable_ratio(t)) × (0.58 + 0.42 × coal_ratio(t))
  structure_index(base) = (1 - renewable_ratio(base)) × (0.58 + 0.42 × coal_ratio(base))

  Energy(t) = GDP(t) × energy_intensity(t)
  energy_intensity(t) = base_EI × (1 - efficiency_improvement_rate)^t
```

#### 3.3.3 结构指数说明

结构指数 `0.58 + 0.42 × coal_ratio` 的含义：
- 0.58 代表非煤炭化石燃料（油品+天然气）的固定权重
- 0.42 代表煤炭的边际影响系数
- coal_ratio 越高，结构指数越大，碳强度越高

---

### 3.4 STIRPAT 模型（随机回归模型）

#### 3.4.1 理论基础

STIRPAT（Stochastic Impacts by Regression on Population, Affluence, and Technology）是经典 IPAT 模型的随机回归扩展。本系统采用对数线性形式，通过历史数据标定弹性系数。

#### 3.4.2 核心公式

```
CO₂(t) = base_CO₂ × scale_effect(t) × efficiency_effect(t) × structure_effect(t)

其中：
  scale_effect(t) = (GDP(t) / base_GDP) ^ elasticity_gdp
  efficiency_effect(t) = (EI(t) / base_EI) ^ elasticity_energy_intensity
  structure_effect(t) = (dirty_share(t) / base_dirty_share) ^ elasticity_structure

  dirty_share(t) = 1 - renewable_ratio(t)
  EI(t) = energy_intensity(t) = base_EI × (1 - efficiency_improvement_rate)^t
```

#### 3.4.3 弹性系数标定

当历史数据 ≥ 4 年时，系统自动通过 OLS 回归标定弹性系数：

```
ln(CO₂) = α + β₁ × ln(GDP) + β₂ × ln(EI) + β₃ × ln(dirty_share) + ε

标定后弹性系数范围约束：
  elasticity_gdp:              [0.2, 1.4]  默认 0.85
  elasticity_energy_intensity: [0.1, 1.4]  默认 0.55
  elasticity_structure:        [0.0, 1.4]  默认 0.35
```

#### 3.4.4 输出字段

STIRPAT 模型额外输出效应分解字段：

| 字段 | 说明 |
|---|---|
| scale_effect | 规模效应（GDP 增长带来的排放增量） |
| efficiency_effect | 效率效应（能效改善带来的排放减量） |
| structure_effect | 结构效应（能源结构优化带来的排放减量） |

---

### 3.5 三模型对比分析

| 维度 | LEAP 模型 | Kaya 模型 | STIRPAT 模型 |
|---|---|---|---|
| 理论框架 | 自底向上，能源供需结构 | 自顶向下，恒等式分解 | 统计回归，弹性系数 |
| 核心公式 | 燃料结构 × 排放因子 | GDP × 能源强度 × 碳强度 | 乘积弹性模型 |
| 适用场景 | 能源政策分析、供需预测 | 因子贡献分解 | 弹性分析、政策效果量化 |
| 优势 | 考虑燃料结构细节 | 逻辑清晰，便于理解 | 可量化各因子贡献 |
| 局限 | 需要更多假设 | 过于简化 | 需要足够历史数据 |
| 参数敏感性 | 能效改善率、可再生能源占比 | 产值增长率、能源强度 | 弹性系数、产值增长率 |
| 碳达峰判断 | 动态迭代，捕捉转折 | 解析式，求极值 | 乘积模型，求极值 |
| 数据要求 | ≥1 年 | ≥1 年 | ≥4 年（用于标定） |
| 共享管道 | ✅ driver_paths + structure_paths | ✅ driver_paths + structure_paths | ❌ 独立投影循环 |

---

## 4. 功能需求

### 4.1 功能模块总览

| 模块编号 | 模块名称 | 优先级 | 说明 |
|---|---|---|---|
| M01 | 数据管理模块 | P0（必须） | 上传/管理历史数据，支持 CSV 和 Excel |
| M02 | 情景配置模块 | P0（必须） | 创建/编辑/复制/删除/对比情景 |
| M03 | LEAP 模型引擎 | P0（必须） | 执行 LEAP 算法预测 |
| M04 | Kaya 模型引擎 | P0（必须） | 执行 Kaya 算法预测 |
| M05 | STIRPAT 模型引擎 | P0（必须） | 执行 STIRPAT 算法预测 |
| M06 | 碳排放折线图 | P0（必须） | 多情景碳排放曲线+达峰标注 |
| M07 | 工业总产值图表 | P0（必须） | 各情景产值增长预测折线图 |
| M08 | 能耗结构柱状图 | P0（必须） | 含可再生/非可再生能源分拆 |
| M09 | 数据明细表格 | P1（重要） | 逐年预测数据表格与导出 |
| M10 | 情景对比面板 | P1（重要） | 情景参数横向对比+雷达图 |
| M11 | AI 参数推荐 | P1（重要） | 基于历史趋势自动推荐参数 |

---

### 4.2 M01 — 数据管理模块

#### 4.2.1 功能描述

用户可上传 CSV 或 Excel 格式的历史数据，或使用系统预置的示例数据。系统自动识别列名映射（支持中英文列名），进行数据验证和趋势分析。

#### 4.2.2 数据存储规格

| 字段名 | 类型 | 说明 | 示例值（2024） |
|---|---|---|---|
| year | Integer | 年份 | 2024 |
| energy_consumption | Float | 综合能源消费量（万吨标准煤） | 1081.95 |
| gdp | Float | 工业总产值（万元） | 10404978.32 |
| co2_emission | Float | CO₂排放量（万吨） | 5273.54 |
| renewable_ratio | Float | 可再生能源占比（0-1） | 0.17 |
| coal_ratio | Float | 煤炭占比（0-1，可选） | 0.75（默认） |

#### 4.2.3 中文列名映射

系统支持以下中文列名自动映射：

| 中文列名 | 映射字段 |
|---|---|
| 年份 / 年度 / year | year |
| 生产总值 / GDP / 产值 / 工业总产值 | gdp |
| 能源消费 / 能耗 / 综合能源消费量 | energy_consumption |
| 碳排放 / CO2 / 二氧化碳排放 | co2_emission |

#### 4.2.4 派生参数（系统自动计算）

- `energy_intensity` = energy_consumption / gdp（能源强度）
- `carbon_intensity` = co2_emission / gdp（碳强度）
- `carbon_factor` = co2_emission / energy_consumption（单位能耗碳排放因子）

#### 4.2.5 数据验证规则

| 规则 | 说明 |
|---|---|
| 必需列 | year, energy_consumption, gdp, co2_emission |
| 数值范围 | energy_consumption, gdp, co2_emission 必须为正数 |
| renewable_ratio | 裁剪到 [0, 0.95] |
| coal_ratio | 裁剪到 [0.02, 0.98] |
| 最少行数 | 1 行（建议 ≥4 年用于 STIRPAT 标定） |

---

### 4.3 M02 — 情景配置模块

#### 4.3.1 情景参数定义

| 参数名称 | 字段名 | 类型 | 取值范围 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 情景名称 | scenario_name | String | 1-50字 | 情景1 | 用户自定义标识 |
| 模型选择 | model_type | Enum | leap / kaya / stirpat | leap | 选择使用哪种算法 |
| 产值增长率 | gdp_growth_rate | Float | -5% ~ 20% | 5% | 年均工业总产值增长率 |
| 能效改善率 | efficiency_improvement_rate | Float | 0% ~ 15% | 3% | 单位产值能耗年下降率 |
| 可再生能源占比提升率 | renewable_increase_rate | Float | 0% ~ 8% | 1% | 可再生能源占比年提升百分点 |
| 煤炭占比下降率 | coal_decrease_rate | Float | 0% ~ 15% | 2% | 煤炭占比年下降百分点 |

**STIRPAT 专属参数：**

| 参数名称 | 字段名 | 类型 | 取值范围 | 默认值 | 说明 |
|---|---|---|---|---|---|
| GDP 弹性系数 | elasticity_gdp | Float | 0.2 ~ 1.4 | 0.85（自动标定） | GDP 对碳排放的弹性 |
| 能源强度弹性系数 | elasticity_energy_intensity | Float | 0.1 ~ 1.4 | 0.55（自动标定） | 能源强度对碳排放的弹性 |
| 结构弹性系数 | elasticity_structure | Float | 0.0 ~ 1.4 | 0.35（自动标定） | 能源结构对碳排放的弹性 |

#### 4.3.2 前端滑块范围（UI 限制）

| 参数 | 滑块最小值 | 滑块最大值 | 步长 |
|---|---|---|---|
| gdp_growth_rate | 0% | 15% | 0.5% |
| efficiency_improvement_rate | 0% | 10% | 0.5% |
| renewable_increase_rate | 0% | 5% | 0.2% |
| coal_decrease_rate | 0% | 5% | 0.2% |

#### 4.3.3 情景管理操作

- **新建情景**：点击"+ 新增情景"按钮，填写参数后保存
- **复制情景**：基于现有情景快速创建副本，便于微调参数进行对比
- **删除情景**：点击删除图标，确认后删除
- **情景列表**：以表格形式展示所有已保存情景，显示模型类型、关键参数值

#### 4.3.4 约束规则

- 同一模块内最多同时保存 **10 个**情景
- 情景名称不可重复
- 情景参数修改后需重新运行预测

---

### 4.4 M03/M04/M05 — 模型引擎

#### 4.4.1 触发方式

用户在情景设置页面点击**"开始预测"**按钮后，系统对所有已保存情景批量执行计算。

#### 4.4.2 预测年数

- 默认预测年数：36 年（从基准年至 2060 年）
- 可配置范围：1-100 年
- 前端硬编码：forecast_years = 36

#### 4.4.3 输出数据结构

每个情景计算完成后，生成以下逐年数据数组：

| 字段名 | 类型 | 说明 |
|---|---|---|
| year | Integer | 年份 |
| gdp | Float | 工业总产值（万元） |
| energy_consumption | Float | 综合能源消费量（万吨标准煤） |
| co2_emission | Float | 碳排放量（万吨） |
| renewable_ratio | Float | 可再生能源占比 |
| renewable_energy | Float | 可再生能源消费量（万吨标准煤） |
| non_renewable_energy | Float | 非可再生能源消费量（万吨标准煤） |
| coal_ratio | Float | 煤炭占比 |
| coal_energy | Float | 煤炭消费量（万吨标准煤） |
| other_fossil_energy | Float | 其他化石能源消费量（万吨标准煤） |
| energy_intensity | Float | 能源强度（万吨标煤/万元） |
| is_peak | Boolean | 是否为碳达峰年份 |
| peak_status | String | 达峰状态：reached / not_reached / base_year_peak |

**STIRPAT 额外输出：**

| 字段名 | 类型 | 说明 |
|---|---|---|
| scale_effect | Float | 规模效应 |
| efficiency_effect | Float | 效率效应 |
| structure_effect | Float | 结构效应 |

---

## 5. 可视化需求详细规格

### 5.1 M06 — 碳达峰分析图（核心图表）

#### 5.1.1 图表基本规格

| 属性 | 规格 |
|---|---|
| 图表类型 | 折线图（Line Chart） |
| 图表库 | Apache ECharts 5.x |
| 图表标题 | 碳达峰预测分析 |
| X 轴 | 年份（历史年份 + 预测年份） |
| Y 轴 | 碳排放量（万吨CO₂当量），自动调整量程 |
| 历史数据 | 实际值，灰色虚线连接 |
| 预测数据 | 每个情景一条曲线，颜色自动分配 |
| 图例 | 底部，显示情景名称 |
| 交互 | 悬停显示 Tooltip（年份、情景名、碳排放量） |

#### 5.1.2 碳达峰标注

- 每条情景曲线上，在碳达峰年份对应的数据点处绘制突出标记
- 标记旁显示文字标签，格式：`"{情景名} 达峰：{年份}年"`
- 图表顶部显示指标卡片：达峰年份、峰值排放量、减排比例、情景数量

### 5.2 M07 — 工业总产值图表

| 属性 | 规格 |
|---|---|
| 图表类型 | 折线图（Line Chart） |
| 图表标题 | 工业总产值趋势（万元） |
| X 轴 | 年份 |
| Y 轴 | 工业总产值（万元），自动调整量程 |
| 历史数据 | 实际值（灰色虚线） |
| 预测曲线 | 每个情景一条曲线（颜色与碳排放图一致） |

### 5.3 M08 — 能耗结构柱状图

#### 5.3.1 图表规格

| 属性 | 规格 |
|---|---|
| 图表类型 | 堆叠柱状图（Stacked Bar Chart） / 趋势折线图（可切换） |
| 图表标题 | 综合能源消费趋势（万吨标准煤） |
| X 轴 | 年份（历史 + 预测期） |
| Y 轴 | 能源消费量（万吨标准煤） |
| 堆叠层1 | **非可再生能源**，高度 = total_energy × (1 - renewable_ratio) |
| 堆叠层2 | **可再生能源**，高度 = total_energy × renewable_ratio |
| 交互 | 悬停显示 Tooltip（年份、情景名、可再生量、非可再生量、占比%） |

#### 5.3.2 图表切换

支持两种视图切换：
- **堆叠柱状图**：直观展示各年能源结构
- **趋势折线图**：展示能耗变化趋势

### 5.4 图表全局要求

- **图表库**：Apache ECharts 5.x（支持中文、交互丰富）
- **主题**：支持暗色/亮色主题切换，图表颜色自适应
- **数据下载**：图表支持 PNG 图片导出
- **字体**：系统中文字体（微软雅黑 / PingFang SC）
- **加载状态**：计算运行期间显示加载动画
- **空状态**：若尚未运行预测，图表区显示空状态提示

---

## 6. 页面结构与交互流程

### 6.1 页面整体布局

系统采用 **Tab 页签** 结构，共 4 个主要页面：

| Tab | 名称 | 组件 | 说明 |
|---|---|---|---|
| Tab 1 | 数据来源 | DataUpload + DataImport | 历史数据管理，始终可用 |
| Tab 2 | 情景设置 | ScenarioManager + ParameterRecommend | 情景配置与 AI 推荐 |
| Tab 3 | 预测结果 | PredictionResults | 图表展示与数据表格 |
| Tab 4 | 情景对比 | ScenarioCompare | 多情景横向对比 |

**Tab 状态规则：**
- Tab 1 始终可用
- Tab 2-4 在数据加载完成后才可切换
- 数据加载后自动启用所有 Tab

### 6.2 Tab 1 — 数据来源

**组件：DataUpload.vue + DataImport.vue**

- 数据概览卡片：年份范围、记录数量
- 数据预览表格：year, gdp, energy_consumption, co2_emission, renewable_ratio
- 文件上传区域：支持 CSV / XLSX / XLS 格式
- 示例数据按钮：一键加载预置示例数据
- 下载模板按钮：下载示例 Excel 模板

### 6.3 Tab 2 — 情景设置

**组件：ScenarioManager.vue + ParameterRecommend.vue**

左侧 — 情景配置表单：
- 情景名称输入框
- 模型选择下拉框（LEAP / Kaya / STIRPAT）
- 参数滑块（产值增长率、能效改善率、可再生能源提升率、煤炭下降率）
- STIRPAT 弹性系数滑块（仅选择 STIRPAT 模型时显示）

右侧 — 情景列表表格：
- 已保存情景列表（名称、模型、参数摘要）
- 删除按钮
- "开始预测"按钮

底部 — AI 参数推荐面板（ParameterRecommend）：
- 左侧：4 个可编辑滑块 + 推荐理由文字
- 右侧：参数敏感性雷达图

### 6.4 Tab 3 — 预测结果

**组件：PredictionResults.vue**

顶部 — 指标卡片（4 张）：
- 达峰年份
- 峰值排放量
- 减排比例
- 情景数量

主区域 — 碳达峰折线图（ECharts）：
- 历史数据虚线 + 预测数据实线
- 达峰点标注

次区域 — 双图表：
- 工业总产值趋势图
- 能耗结构图（堆叠柱状图 / 趋势折线图可切换）

底部 — 数据明细表格：
- 逐年预测数据
- 历史/预测标签
- 支持导出 CSV

操作栏：
- 下载 CSV 按钮
- 导出图表按钮
- 返回情景设置按钮

### 6.5 Tab 4 — 情景对比

**组件：ScenarioCompare.vue**

- 情景选择：复选框选择要对比的情景
- 达峰年份对比柱状图
- 碳排放路径对比折线图
- 综合评估雷达图（达峰速度、减排效果、经济影响、可行性）
- 对比报告表格（达峰年份、峰值排放、减排率）

### 6.6 核心交互流程

**流程一：创建情景并运行预测**

1. 用户进入 Tab 1，上传数据或使用示例数据
2. 切换到 Tab 2，配置情景参数
3. 可选：查看 AI 参数推荐
4. 点击"开始预测"按钮
5. 系统批量计算所有情景
6. 切换到 Tab 3 查看结果
7. 切换到 Tab 4 进行情景对比

**流程二：调整参数并对比**

1. 在 Tab 2 中复制现有情景
2. 修改参数后保存
3. 重新运行预测
4. 在 Tab 4 中选择原始情景和修改后情景进行对比

---

## 7. API 接口规格

### 7.1 数据管理接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/upload | 上传 CSV 数据文件 |
| POST | /api/upload/custom | 上传 CSV/Excel，支持中文列名映射 |
| POST | /api/upload/example | 加载示例数据 |
| GET | /api/data/current | 获取当前数据预览 |
| GET | /api/data/trends | 历史趋势分析 + 参数建议 |
| POST | /api/data/validate | 验证列结构 |
| GET | /api/download/sample | 下载示例 Excel 模板 |

### 7.2 情景管理接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/scenarios | 获取所有情景列表 |
| POST | /api/scenarios | 创建新情景 |
| DELETE | /api/scenarios/{name} | 删除指定情景 |
| POST | /api/scenarios/copy | 复制情景 |
| POST | /api/scenarios/compare | 多情景对比数据 |
| GET | /api/models | 获取可用模型列表 |

### 7.3 预测接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/predict | 运行预测 |
| GET | /api/predict/status | 查询预测状态 |
| GET | /api/chart-data | 获取图表数据（前端 ECharts 渲染） |
| GET | /api/results/{name} | 获取指定情景结果 |
| GET | /api/results/{name}/download | 下载结果 CSV |

### 7.4 导出接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/charts/{name} | 获取生成的图表 PNG |
| GET | /api/export/excel/{name} | 导出 Excel 报告 |
| GET | /api/export/pdf/{name} | 导出 PDF（当前返回 JSON 摘要） |

### 7.5 智能推荐接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/recommend/parameters | AI 参数推荐（基于历史趋势） |

### 7.6 预测请求参数

```json
{
  "scenarios": ["情景一", "情景二"],
  "forecast_years": 36
}
```

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|---|---|---|---|---|
| scenarios | Array[String] | - | - | 要预测的情景名称列表 |
| forecast_years | Integer | 1-100 | 30 | 预测年数 |

### 7.7 情景创建请求参数

```json
{
  "name": "基准情景",
  "model_type": "leap",
  "gdp_growth_rate": 0.05,
  "efficiency_improvement_rate": 0.03,
  "renewable_increase_rate": 0.01,
  "coal_decrease_rate": 0.02
}
```

**STIRPAT 额外参数：**

```json
{
  "name": "STIRPAT情景",
  "model_type": "stirpat",
  "gdp_growth_rate": 0.05,
  "efficiency_improvement_rate": 0.03,
  "renewable_increase_rate": 0.01,
  "coal_decrease_rate": 0.02,
  "elasticity_gdp": 0.85,
  "elasticity_energy_intensity": 0.55,
  "elasticity_structure": 0.35
}
```

---

## 8. 数据规格

### 8.1 CSV 数据格式

**必需列：**

| 列名 | 类型 | 说明 | 单位 |
|---|---|---|---|
| year | Integer | 年份 | - |
| energy_consumption | Float | 综合能源消费量 | 万吨标准煤 |
| gdp | Float | 工业总产值 | 万元 |
| co2_emission | Float | CO₂排放量 | 万吨 |

**可选列：**

| 列名 | 类型 | 说明 | 默认值 |
|---|---|---|---|
| renewable_ratio | Float | 可再生能源占比 | 0.05 |
| coal_ratio | Float | 煤炭占比 | 0.75 |

### 8.2 情景配置存储

情景配置存储在 `backend/data/scenarios.json`，格式：

```json
{
  "情景名称": {
    "model_type": "leap",
    "gdp_growth_rate": 0.05,
    "efficiency_improvement_rate": 0.03,
    "renewable_increase_rate": 0.01,
    "coal_decrease_rate": 0.02
  }
}
```

---

## 9. 非功能需求

### 9.1 性能要求

| 场景 | 指标 | 目标值 |
|---|---|---|
| 单情景计算 | 响应时间 | < 500ms |
| 10个情景批量计算 | 总计算时间 | < 3秒 |
| 图表首次渲染 | 渲染时间 | < 1秒 |
| 页面首屏加载 | 加载时间 | < 2秒（良好网络） |

### 9.2 浏览器兼容性

- Chrome 90+（推荐）
- Edge 90+
- Firefox 88+
- Safari 14+
- 响应式布局，支持平板（1024px+）

### 9.3 数据精度

- 所有 Float 计算使用 64 位双精度浮点数（IEEE 754）
- 展示层四舍五入：能耗、产值保留 2 位小数；占比保留 1 位小数；碳排放保留 2 位小数
- 碳达峰判断容差：0.5%

### 9.4 主题支持

- 支持暗色（Dark）和亮色（Light）两种主题
- 主题切换实时生效，图表颜色自适应
- 主题偏好保存在 localStorage

---

## 10. 技术架构

### 10.1 前端技术栈

| 层次 | 技术 | 说明 |
|---|---|---|
| 框架 | Vue.js 2.x | 组件化开发 |
| UI 组件库 | Element UI | 企业级组件（滑块、下拉框、表格等） |
| 图表库 | Apache ECharts 5.x | 支持中文、堆叠图、折线图、雷达图 |
| 样式 | CSS Variables + 设计令牌 | 主题切换支持 |
| HTTP 客户端 | Axios | API 请求 |
| 构建工具 | Vue CLI (Webpack) | 开发与构建 |

### 10.2 后端技术栈

| 层次 | 技术 | 说明 |
|---|---|---|
| 框架 | Flask | REST API |
| 数据处理 | Pandas + NumPy | 数据加载、验证、计算 |
| 图表生成 | Matplotlib | 服务端图表生成（PNG） |
| 数据存储 | JSON 文件 | 情景配置持久化 |
| 文件处理 | openpyxl | Excel 文件读写 |

### 10.3 项目结构

```
carbon_peak3/
├── backend/
│   ├── app.py                    # Flask REST API 主程序
│   ├── model/
│   │   ├── simplified_leap.py    # LEAP 模型引擎
│   │   ├── simplified_kaya.py    # Kaya 模型引擎
│   │   ├── stirpat_model.py      # STIRPAT 模型引擎
│   │   ├── prediction_utils.py   # 公共预测管道
│   │   ├── simple_scenario_runner.py  # 统一预测调度器
│   │   └── simple_data_processor.py   # 数据加载与验证
│   ├── data/
│   │   ├── base_year_data.csv    # 基准年数据
│   │   ├── scenarios.json        # 情景配置
│   │   └── sample_data.xlsx      # 示例数据模板
│   └── output/                   # 预测结果输出
├── frontend/
│   ├── src/
│   │   ├── App.vue               # 主应用（4 Tab 结构）
│   │   ├── components/
│   │   │   ├── DataUpload.vue    # 数据上传
│   │   │   ├── DataImport.vue    # 文件导入
│   │   │   ├── ScenarioManager.vue    # 情景管理
│   │   │   ├── ParameterRecommend.vue # AI 参数推荐
│   │   │   ├── PredictionResults.vue  # 预测结果
│   │   │   ├── ScenarioCompare.vue    # 情景对比
│   │   │   ├── ThemeToggle.vue   # 主题切换
│   │   │   └── ...
│   │   └── utils/api.js          # API 接口封装
│   └── public/
├── start.bat                     # Windows 启动脚本
└── start.sh                      # Linux/Mac 启动脚本
```

### 10.4 数据流架构

```
用户上传数据 → DataUpload → /api/upload → base_year_data.csv
                                              ↓
用户配置情景 → ScenarioManager → /api/scenarios → scenarios.json
                                              ↓
点击"开始预测" → /api/predict → simple_scenario_runner.py
                                    ↓
                          ┌─────────┼─────────┐
                          ↓         ↓         ↓
                     LEAP引擎  Kaya引擎  STIRPAT引擎
                          ↓         ↓         ↓
                          └─────────┼─────────┘
                                    ↓
                           prediction_utils.py
                           (finalize_projection)
                                    ↓
                           /api/chart-data → ECharts
                           /api/results → 数据表格
```

---

## 11. 验收标准

| 编号 | 验收项目 | 验收标准 | 优先级 |
|---|---|---|---|
| AC-01 | 数据上传 | 可成功上传 CSV/Excel 文件，数据预览正确 | P0 |
| AC-02 | 示例数据 | 点击"使用示例数据"后正确加载预置数据 | P0 |
| AC-03 | 情景创建 | 可成功新建情景，填写所有参数，保存后出现在列表中 | P0 |
| AC-04 | 情景复制 | 可成功复制现有情景，参数继承正确 | P1 |
| AC-05 | LEAP 计算 | 选择 LEAP 模型运行后，碳排放数据符合公式计算结果 | P0 |
| AC-06 | Kaya 计算 | 选择 Kaya 模型运行后，碳排放数据符合卡亚恒等式计算结果 | P0 |
| AC-07 | STIRPAT 计算 | 选择 STIRPAT 模型运行后，碳排放数据符合弹性模型计算结果 | P0 |
| AC-08 | 多情景对比 | 同时保存 3 个以上情景，点击预测后折线图显示多条曲线 | P0 |
| AC-09 | 碳达峰标注 | 所有情景的碳达峰年份在折线图上正确标注 | P0 |
| AC-10 | 产值图表 | 正确展示各情景产值增长趋势 | P0 |
| AC-11 | 能耗图表 | 正确分拆可再生/非可再生能源，支持堆叠/趋势切换 | P0 |
| AC-12 | 情景对比 | 雷达图和对比表格正确展示多情景差异 | P1 |
| AC-13 | AI 推荐 | 参数推荐面板正确展示推荐值和雷达图 | P1 |
| AC-14 | 数据导出 | 可成功导出 CSV 和 Excel 文件 | P1 |
| AC-15 | 主题切换 | 暗色/亮色主题切换正常，图表颜色自适应 | P1 |
| AC-16 | 可再生能源约束 | 可再生能源占比达到 95% 上限后不再增加 | P0 |
| AC-17 | 性能 | 10 个情景批量计算完成时间 < 3 秒 | P1 |

---

## 附录 A：情景参数影响机制说明

### 产值增长率（gdp_growth_rate）

> - **LEAP**：通过增加能源消费量间接增加碳排放（`E = GDP × EI`，产值增加则需更多能源）
> - **Kaya**：直接乘入公式，`C = GDP × EI × CI`，产值增速越高，碳排放越高
> - **STIRPAT**：作为规模效应 `scale_effect = (GDP/base_GDP)^elasticity_gdp` 弹性放大
> - **反效果前提**：仅当能效改善率 + 可再生能源提升率的减碳效果超过产值增长带来的增碳效果，才能出现碳达峰

### 能效改善率（efficiency_improvement_rate）

> - **定义**：单位产值所消耗的能源量（能源强度 EI）每年下降的比率
> - **LEAP/Kaya**：`EI(t) = EI₀ × (1-η)^t`，随时间指数下降
> - **STIRPAT**：作为效率效应 `efficiency_effect = (EI/base_EI)^elasticity_energy_intensity`
> - **关键阈值**：当 `η > g`（能效改善率 > 产值增速），能源消费量会绝对下降

### 可再生能源占比提升率（renewable_increase_rate）

> - **定义**：每年可再生能源在综合能耗中的占比提升的**百分点数**
> - **影响机制**：可再生能源碳排放因子 = 0，占比越高，单位能耗碳排放越低
> - **LEAP**：通过 `renewable_energy = total_energy × renewable_ratio` 直接减少化石能源消费
> - **Kaya**：通过 `structure_index = (1 - renewable_ratio) × (0.58 + 0.42 × coal_ratio)` 降低碳强度
> - **STIRPAT**：通过 `dirty_share = 1 - renewable_ratio` 作为结构效应的驱动因子

### 煤炭占比下降率（coal_decrease_rate）

> - **定义**：煤炭在能源消费中占比每年下降的百分点
> - **影响机制**：煤炭排放因子（2.66）远高于其他化石燃料（1.876），降低煤炭占比可显著降低碳排放
> - **LEAP**：`coal_energy = total_energy × coal_ratio`，coal_ratio 指数衰减
> - **Kaya**：通过 `structure_index` 中的 `coal_ratio` 项降低碳强度

---

## 附录 B：预设情景建议（供产品初始化参考）

| 情景名称 | 模型 | 产值增长率 | 能效改善率 | 可再生能源提升率 | 煤炭下降率 | 情景描述 |
|---|---|---|---|---|---|---|
| 历史趋势情景 | LEAP | 8.3% | 5% | 1% | 2% | 延续历史增长趋势 |
| 基准情景 | Kaya | 4.5% | 5% | 1% | 1.6% | 政策无重大调整 |
| 政策加速情景 | LEAP | 5% | 10% | 1.5% | 2% | 政府大力推进能效改造 |
| 高增长情景 | LEAP | 7.75% | 10% | 1.5% | 2% | 产值快速扩张 |
| 保守情景 | LEAP | 5% | 3% | 1% | 2% | 经济增速放缓 |

---

*——— 文档结束 ———*

*碳管理预测分析平台 PRD v2.0 © 2025 机密文件*
