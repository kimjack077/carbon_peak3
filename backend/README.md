# 碳达峰预测系统 - 后端

这是碳达峰预测系统的后端服务，使用 Flask 框架构建。

## 使用 uv 启动后端

1. 确保已安装 uv：
```bash
pip install uv
```

2. 在 backend 目录下运行以下命令启动后端服务：
```bash
uv run app.py
```

或者使用以下命令安装依赖并启动：
```bash
uv sync
uv run python app.py
```

## API 端点

- `POST /api/upload` - 上传基准年数据
- `GET /api/upload/example` - 使用示例数据
- `POST /api/scenarios` - 创建预测情景
- `GET /api/scenarios` - 获取所有预测情景
- `DELETE /api/scenarios/<scenario_name>` - 删除预测情景
- `POST /api/predict` - 运行预测
- `GET /api/predict/status` - 获取预测状态
- `GET /api/charts/<chart_name>` - 获取生成的图表
- `GET /api/results/<scenario_name>` - 获取预测结果数据
- `GET /api/results/<scenario_name>/download` - 下载预测结果数据
- `GET /api/chart-data` - 获取图表数据

## 项目结构

- `app.py` - 主应用文件
- `model/` - 模型模块
  - `carbon_emission.py` - 碳排放模型
  - `data_processor.py` - 数据处理器
  - `energy_demand.py` - 能源需求模型
  - `energy_mix.py` - 能源结构模型
  - `scenario_runner.py` - 情景运行器
- `utils/` - 工具模块
  - `plot_results.py` - 结果绘图工具
- `data/` - 数据目录
- `output/` - 输出目录