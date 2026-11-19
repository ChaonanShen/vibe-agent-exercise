"""
练习 2.1 · 手搓 Function Calling 消息流
=========================================

知识点：第 7 节《Function Calling 协议》

要求：补全 run_tool_call 函数
  - 给模型一个 calculator 工具
  - 让模型决定是否调用
  - 手动执行工具
  - 把结果回传，拿到最终回答

你需要理解 4 条消息的完整流转。
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _env import chat, get_model_id, make_client

client = make_client()
MODEL = get_model_id()

# 工具的 schema
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算一个数学表达式，返回结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如 '2 + 3 * 4'",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]


def execute_calculator(expression: str) -> str:
    """执行计算（已实现，不用改）"""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


def run_tool_call(question: str) -> str:
    """目标：完成一次完整的 Function Calling 流程，返回模型最终回答。

    流程：用户提问 → 模型决定是否调工具 → 执行工具 → 结果回传 → 拿到最终回答。
    """
    messages = [{"role": "user", "content": question}]

    # TODO ① 第一次调用：必须把工具交给模型，让它自己决定是否使用
    msg = chat(messages, tools=TOOLS, client=client, model=MODEL)  # 把工具列表传进去

    # TODO ② 模型没请求工具 → 直接返回它的回答（tool_calls 为空说明模型直接回复了文本）
    if not msg.tool_calls:
        return msg.content  # 【提示🔔】msg 是模型返回对象，它携带了模型的回复内容，取 .content 字段

    # 取出工具调用、解析出参数（已实现）
    tool_call = msg.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    # TODO ③ 调用工具函数执行计算——表达式参数已经帮你解析好了
    result = execute_calculator(args["expression"])  # 【提示🔔】工具调用的参数需要从 args 解析，关键字段是 expression，取 args["expression"]

    # 先把模型刚刚那条回复加回历史（已实现）
    messages.append(msg)
    # TODO ④ 追加一条"工具结果"消息回传模型
    messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})  # 【提示🔔】role 四选一 user/assistant/system/tool 该用哪个？ | content 该传什么（提示：上一步的 result）？ | tool_call_id 如何拿到（提示：tool_call 的哪个属性）？

    # TODO ⑤ 第二次调用：把包含工具结果的 messages 再发给模型拿最终答案——Agent 循环的雏形
    msg2 = chat(messages, client=client, model=MODEL)  # 【提示🔔】第一个参数：整个对话历史（含刚追加的工具结果）
    return msg2.content


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：简单计算
    answer = run_tool_call("请帮我算一下 123 乘以 456 等于多少")
    assert "56088" in re.sub(r"\D", "", answer), f"123×456=56088，但模型回答: {answer}"

    # 测试 2：返回类型
    answer2 = run_tool_call("7 + 8 等于多少？")
    assert isinstance(answer2, str), "返回值应该是字符串"
    assert "15" in re.sub(r"\D", "", answer2), f"7+8=15，但模型回答: {answer2}"

    print("✅ PASSED: run_tool_call 全部测试通过")
