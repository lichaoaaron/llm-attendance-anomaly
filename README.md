# 基于大模型的考勤异常识别与绩效辅助评估系统

面向企业考勤管理场景，提供考勤流水清洗、异常规则识别（迟到、早退、缺卡、
加班）以及基于考勤数据的绩效辅助评估能力。核心逻辑仅依赖 Python 标准库，
可离线运行；大模型用于生成异常的自然语言解释，默认使用规则模板兜底。

## 功能特性

- **考勤流水清洗**：按「员工 + 日期」分组，去重、排序并配对进出记录，估算在岗时长。
- **异常规则识别**：识别迟到、早退、缺卡、加班四类异常，并按严重程度分级。
- **自然语言解释**：为每条异常生成可读解释（可切换真实大模型）。
- **绩效辅助评估**：计算考勤率、平均迟到、加班时长，给出辅助性结论。

## 快速开始

```bash
# 清洗流水
python -m attendance_anomaly --data data/sample_attendance.json clean

# 识别异常（含解释）
python -m attendance_anomaly --data data/sample_attendance.json detect

# 绩效辅助摘要（应出勤天数可配置）
python -m attendance_anomaly --data data/sample_attendance.json summarize --work-days 5
```

## 接入真实大模型

```bash
export AA_LLM_PROVIDER=openai_compatible
export AA_LLM_API_BASE=https://your-endpoint
export AA_LLM_API_KEY=sk-xxx
export AA_LLM_MODEL=your-model
```

## 目录结构

```
attendance-anomaly-system/
├── src/attendance_anomaly/
│   ├── models/                # 数据模型
│   ├── services/              # 清洗、异常引擎、绩效评估、LLM 客户端
│   ├── cli.py                 # 命令行入口
│   ├── config.py              # 配置
│   └── data_loader.py         # 数据加载
├── data/                      # 示例数据
└── tests/                     # 单元测试
```

## 运行测试

```bash
python -m unittest discover -s tests
```
