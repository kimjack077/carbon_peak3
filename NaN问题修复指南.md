# NaN 值导致前端图表无法显示 - 修复指南

## 问题描述

前端显示空白，浏览器控制台出现大量错误：
```
情景 "15238" 的数据不完整，跳过
情景 "15239" 的数据不完整，跳过
...
TypeError: data.years is not iterable
```

## 根本原因

后端 `/api/chart-data` 返回的数据中，`energy_mix.elec` 数组包含大量 `NaN` 值：

```json
{
  "energy_mix": {
    "coal": [3973.42, 4044.15, ...],
    "elec": [1915.76, 2171.86, 2424.36, NaN, NaN, NaN, ...],  // ❌ 预测数据部分全是 NaN
    "other": [3121.97, 3445.02, ...]
  }
}
```

**原因**：
- 历史数据（2022-2024）有 `power_share` 列
- 预测数据（2025-2054）没有 `power_share` 列
- 合并后，预测部分的 `power_share` 为 NaN
- 计算时 `NaN * 任何数 = NaN`

## 修复步骤

### 第 1 步：验证后端代码已修改

打开 `backend/app.py`，检查第 402、410 行附近是否有 `.fillna(0)`：

```python
# 应该是这样：
'coal': (energy_total * combined_df['mix_coal'].fillna(0)).tolist(),
'elec': (energy_total * combined_df['power_share'].fillna(0)).tolist(),

# 而不是：
'coal': (energy_total * combined_df['mix_coal']).tolist(),
'elec': (energy_total * combined_df['power_share']).tolist(),
```

✅ 如果已经有 `.fillna(0)`，继续下一步  
❌ 如果没有，说明修改没有保存，请重新编辑

### 第 2 步：重启后端

**方法 1：** 在后端终端按 `Ctrl+C` 停止，然后重新运行：
```bash
cd D:\software\carbon_peak3\backend
python app.py
```

**方法 2：** 关闭后端终端窗口，重新打开并运行：
```bash
cd D:\software\carbon_peak3\backend
python app.py
```

### 第 3 步：验证修复

运行测试脚本：
```bash
cd D:\software\carbon_peak3
python test_nan_fix.py
```

**预期输出**：
```
检查情景: 2028年达峰情景
  ✅ coal: 无 NaN 值 (33 个数据点)
  ✅ elec: 无 NaN 值 (33 个数据点)
  ✅ other: 无 NaN 值 (33 个数据点)

检查情景: 2030年达峰情景
  ✅ coal: 无 NaN 值 (33 个数据点)
  ✅ elec: 无 NaN 值 (33 个数据点)
  ✅ other: 无 NaN 值 (33 个数据点)

...

🎉 所有数据都没有 NaN 值！
```

如果仍然显示有 NaN，说明后端没有重启或修改没有生效。

### 第 4 步：刷新前端

在浏览器中：
1. 按 `Ctrl + Shift + R`（或 `Cmd + Shift + R`）强制刷新页面
2. 或者按 `F12` 打开开发者工具，右键刷新按钮，选择"清空缓存并硬性重新加载"

### 第 5 步：验证前端显示

打开浏览器开发者工具（F12），查看 Console 标签页：

**✅ 成功标志**：
- 没有"情景 15238"、"情景 15239"这样的错误
- 没有"data.years is not iterable"错误
- 图表正常显示

**❌ 如果仍然失败**：
- 查看 Network 标签页，找到 `chart-data` 请求
- 点击查看响应内容，检查是否还有 `NaN` 值
- 如果有，说明后端修改没有生效，回到第 1 步

## 其他可能的问题

### 问题1：前端缓存

**症状**：后端已修复，但前端仍显示旧数据

**解决**：
1. 清除浏览器缓存：`Ctrl + Shift + Delete`
2. 或者使用无痕模式/隐私模式打开前端

### 问题2：前端代码需要重新编译

**症状**：使用生产模式（`npm run build`）

**解决**：
```bash
cd D:\software\carbon_peak3\frontend
npm run build
```

然后重新启动前端服务器。

### 问题3：端口冲突

**症状**：后端重启失败，提示端口被占用

**解决**：
```powershell
# 查找占用 5000 端口的进程
netstat -ano | findstr :5000

# 结束进程（替换 PID 为实际的进程ID）
taskkill /PID <PID> /F

# 重新启动后端
cd D:\software\carbon_peak3\backend
python app.py
```

## 验证清单

- [ ] `backend/app.py` 已添加 `.fillna(0)`
- [ ] 后端已重启
- [ ] 运行 `test_nan_fix.py` 通过
- [ ] 前端已强制刷新
- [ ] 浏览器控制台没有错误
- [ ] 碳达峰图表正常显示
- [ ] 能源结构图表正常显示

## 技术细节

### 修复前的数据流：

```
历史数据 (2022-2024)
  ├─ power_share: [0.27, 0.29, 0.31]
  
预测数据 (2025-2054)
  ├─ power_share: 不存在
  
合并后
  ├─ power_share: [0.27, 0.29, 0.31, NaN, NaN, ..., NaN]
  
计算 elec
  ├─ energy * power_share
  ├─ [1000*0.27, 1100*0.29, 1200*0.31, 1300*NaN, ...]
  └─ [270, 319, 372, NaN, NaN, ..., NaN]  ❌
```

### 修复后的数据流：

```
合并后
  ├─ power_share: [0.27, 0.29, 0.31, NaN, NaN, ..., NaN]
  └─ .fillna(0)
      └─ [0.27, 0.29, 0.31, 0, 0, ..., 0]
  
计算 elec
  ├─ energy * power_share.fillna(0)
  ├─ [1000*0.27, 1100*0.29, 1200*0.31, 1300*0, ...]
  └─ [270, 319, 372, 0, 0, ..., 0]  ✅
```

**注意**：预测数据的 `elec` 值为 0 是正确的，因为模型使用了油气合并的方式，而不是单独的电力数据。

## 需要帮助？

如果按照以上步骤仍然无法解决，请提供：
1. `test_nan_fix.py` 的完整输出
2. 浏览器控制台的完整错误信息
3. 后端终端的输出
