"""
练习 3.2 · Plan-and-Solve 的 Planner
======================================

知识点：第 13 节《Plan-and-Solve 范式》

要求：补全 make_plan 函数
  - 输入：用户问题（str）
  - 输出：步骤列表（list[str]），每个元素是一个具体步骤描述

实现思路：让 LLM 把问题拆成步骤，要求输出 JSON 数组。
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _env import chat, get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def make_plan(question: str) -> list[str]:
    """目标：让 LLM 把 question 拆解成有序步骤列表。

    Plan-and-Solve 的核心思路：先让模型"规划"，再让别的环节"执行"。
    规划要拿得到，关键在于 —— 让模型输出结构化的格式（JSON），我们才能解析。
    """
    # TODO ① 写一段 system prompt，让模型拆解问题并以 JSON数组 格式输出
    system_prompt = ...  # 【提示🔔】提示词需包含两件事：(1) 把问题拆成 3-6 个步骤 (2) 严格以 JSON数组 格式输出  （⚠️ 格式是数组，每一个元素代表其中的一个子步骤）

    # 调用模型（已实现）
    msg = chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        client=client,
        model=MODEL,
    )
    content = msg.content

    # 清理掉模型可能带的 ```json ... ``` 包裹（已实现，细节不是重点）
    clean = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    # TODO ② 把清洗后的字符串解析成 Python 列表
    plan = ...  # 【提示🔔】用 json.loads() 把 JSON 字符串转成 Python 对象

    return plan


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：简单任务
    plan = make_plan("帮我写一个 Python 的冒泡排序并测试它")
    assert isinstance(plan, list), f"应该返回列表，实际: {type(plan)}"
    assert len(plan) >= 2, f"至少应该有 2 步，实际: {len(plan)} 步"
    assert all(isinstance(s, str) for s in plan), "每个步骤应该是字符串"
    print(f"[测试1] 计划有 {len(plan)} 步:")
    for i, step in enumerate(plan, 1):
        print(f"  {i}. {step}")

    # 测试 2：复杂任务
    plan2 = make_plan("查北京和上海的天气，对比哪个更适合周末出游，给出推荐理由")
    assert len(plan2) >= 3, f"复杂任务至少 3 步，实际: {len(plan2)} 步"
    print(f"\n[测试2] 计划有 {len(plan2)} 步:")
    for i, step in enumerate(plan2, 1):
        print(f"  {i}. {step}")

    # 测试 3：步骤内容不为空
    for step in plan + plan2:
        assert len(step.strip()) > 0, "步骤内容不应该为空"

    print("\n✅ PASSED: make_plan 全部测试通过")
