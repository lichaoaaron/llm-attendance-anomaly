# 使用指南

本文档介绍「基于大模型的考勤异常识别与绩效辅助评估系统」命令行工具的使用方式。

## 快速开始

```bash
PYTHONPATH=src python -m attendance_anomaly --data data/sample_attendance.json <子命令>
```

## 子命令

### clean — 清洗流水

把打卡流水按「员工 + 日期」去重配对，输出每日出勤汇总。

```bash
python -m attendance_anomaly --data data/sample_attendance.json clean
```

### detect — 识别异常

识别迟到、早退、缺卡、加班四类异常，并生成自然语言解释。

```bash
python -m attendance_anomaly --data data/sample_attendance.json detect
```

### summarize — 绩效辅助摘要

输出每位员工的出勤率、平均迟到、加班时长与结论。

```bash
python -m attendance_anomaly --data data/sample_attendance.json summarize --work-days 5
```

### metrics — 出勤衍生指标

输出出勤稳定性、平均到岗时刻、到岗波动等指标。

```bash
python -m attendance_anomaly --data data/sample_attendance.json metrics
```

### notify — 生成异常通知

为识别出的异常生成面向员工的通知文案。

```bash
python -m attendance_anomaly --data data/sample_attendance.json notify
```

### report — 导出报告到标准输出

```bash
python -m attendance_anomaly --data data/sample_attendance.json report --format csv
python -m attendance_anomaly --data data/sample_attendance.json report --format html
```

### monthly-report — 月度考勤结算

输出指定月份的出勤、异常、加班、请假结算结果。

```bash
python -m attendance_anomaly --data data/sample_attendance.json monthly-report --year-month 2026-09
```

## 节假日配置

`data/holidays_2026.json` 提供 2026 年节假日与调休配置，可通过 `ConfigLoader` 加载并初始化 `WorkingCalendar`：

```python
from pathlib import Path
from attendance_anomaly.config_loader import ConfigLoader
from attendance_anomaly.models.holiday import WorkingCalendar

holidays = ConfigLoader().load_holidays(Path("data/holidays_2026.json"))
calendar = WorkingCalendar(holidays)
```

## 接入真实大模型

```bash
export AA_LLM_PROVIDER=openai_compatible
export AA_LLM_API_BASE=https://your-endpoint
export AA_LLM_API_KEY=sk-xxx
export AA_LLM_MODEL=your-model
```

## 数据格式

打卡流水为 JSON 数组，字段如下：

```json
[
  {"employee_id": "A001", "date": "2026-09-14", "punch_time": "09:00", "punch_type": "in"},
  {"employee_id": "A001", "date": "2026-09-14", "punch_time": "18:00", "punch_type": "out"}
]
```

同时支持 CSV 导入，表头可为中文（员工编号/日期/打卡时间/打卡类型）。
