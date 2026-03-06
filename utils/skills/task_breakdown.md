# task_breakdown

## 用途
将用户输入的任务描述拆解为：
- O（Objective）：任务目标
- K（Key Results）：可执行关键结果列表

## 输入
- `user_content`（文本）：用户任务描述

## 输出
JSON 对象：
- `objective`：字符串
- `key_results`：字符串数组（最多 5 条）

## 失败与约束
- 输入为空时输出兜底目标与兜底 K

## 示例
输入：
“把前端任务模式打通并落盘 okras”

输出（示例）：
```json
{
  "objective": "完成任务：把前端任务模式打通并落盘 okras",
  "key_results": ["把前端任务模式打通并落盘 okras"]
}
```
