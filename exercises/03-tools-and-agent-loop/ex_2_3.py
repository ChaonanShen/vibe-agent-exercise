"""
练习 2.3 · 最小 Agent Loop
============================

知识点：第 9 节《最小 Agent Loop》

要求：补全 agent_loop 函数
  - 给模型工具列表 + 用户问题
  - while 循环：模型返回 tool_calls → 执行 → 结果回传 → 继续
  - 模型不再调工具 → 返回最终文本回答

关键理解：Agent = LLM + Tools + Loop
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _env import chat, get_model_id, make_client

client = make_client()
MODEL = get_model_id()

# ---------- 工具定义 ----------

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "计算两个数字的和",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数"},
                    "b": {"type": "number", "description": "第二个数"},
                },
                "required": ["a", "b"],
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """执行工具（已实现，不用改）"""
    if name == "get_time":
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif name == "add":
        return str(args["a"] + args["b"])
    else:
        return f"未知工具: {name}"


def agent_loop(question: str, max_iterations: int = 5) -> str:
    """目标：最小 Agent Loop — 让 LLM 反复"思考-用工具-思考"，直到给出最终答案。

    把上一题的"两次调用"扩展成"任意多次"，关键就是 while/for 循环 + 一个退出条件。
    """
    messages = [{"role": "user", "content": question}]

    for i in range(max_iterations):
        # 调一次模型（已实现）
        msg = chat(messages, tools=TOOLS_SCHEMA, client=client, model=MODEL)

        # TODO ① 循环的退出条件：模型这一轮没有再请求工具，说明它已经给出了最终回答
        if ...:  # 【提示🔔】msg.tool_calls 为空说明模型不再请求工具，已给出最终回答
            return msg.content

        # 把模型这条带工具请求的回复加回历史（已实现）
        messages.append(msg)

        # TODO ② 模型一次可能并行请求多个工具，这里要遍历每一个 tool_call
        for tc in ...:  # 【提示🔔】待执行的工具调用列表挂在 msg.tool_calls 上
            # 解析参数 → 执行工具 → 把结果回传给模型（已实现）
            args = json.loads(tc.function.arguments)
            result = execute_tool(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        # 继续下一轮：模型会看到刚刚的工具结果，再决定下一步

    # 兜底：达到最大轮次仍未给出最终回答，返回一个提示字符串
    # 想想（不用填）：为什么 Agent Loop 必须设这个上限？——防止模型陷入死循环、烧光 API 额度
    return "达到最大迭代次数，Agent 未能完成任务"


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：需要调工具的问题
    answer = agent_loop("现在几点了？")
    assert isinstance(answer, str), "返回值应该是字符串"
    assert len(answer) > 3, f"回答太短了: {answer!r}"
    print(f"[测试1] 问: 现在几点了？ → 答: {answer}")

    # 测试 2：需要计算的问题
    answer2 = agent_loop("请帮我算 17 + 25 等于多少")
    assert "42" in answer2, f"17+25=42，但模型回答: {answer2}"
    print(f"[测试2] 问: 17+25=? → 答: {answer2}")

    # 测试 3：max_iterations 保护
    answer3 = agent_loop("你好", max_iterations=1)
    assert isinstance(answer3, str), "即使只跑 1 轮也应该返回字符串"
    print(f"[测试3] 问: 你好 → 答: {answer3}")

    print("\n✅ PASSED: agent_loop 全部测试通过")
