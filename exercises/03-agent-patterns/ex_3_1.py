"""
练习 3.1 · ReAct 输出解析器
============================

知识点：第 12 节《ReAct 范式》

要求：补全 parse_react_output 函数
  - 输入：模型输出的文本（包含 Thought / Action / Action Input）
  - 输出：(thought, action, action_input) 三元组

模型输出格式示例：
  Thought: 用户想知道天气，我需要调用天气工具
  Action: get_weather
  Action Input: {"city": "北京"}
"""

import re


def parse_react_output(text: str) -> tuple[str, str, str]:
    """目标：从 ReAct 格式文本中提取 Thought、Action、Action Input。

    ReAct 的核心是让模型按"思考→行动→输入"三段式输出，下游再解析这三段去执行工具。
    返回 (thought, action, action_input)，某段没出现就返回空串 ""。
    """
    # 已实现：提取 Thought（到下一个 Action: 之前，否则到结尾）
    m = re.search(r"Thought:\s*(.*?)(?=Action:|$)", text, re.DOTALL)
    thought = m.group(1).strip() if m else ""

    # TODO ① 仿照上面提取 Action（在 Action: 和 Action Input: 之间）
    m = re.search(r"Action:\s*(.*?)(?=Action Input:|$)", text, re.DOTALL)  # 【提示🔔】套用 Thought 的正则结构，把前后关键字换成 Action: 和 Action Input:
    action = m.group(1).strip() if m else ""

    # TODO ② 提取 Action Input（Action Input: 之后到结尾的所有内容）
    m = re.search(r"Action Input:\s*(.*)", text, re.DOTALL)  # 【提示🔔】Action Input 是最后一段，只需匹配 Action Input: 后面到字符串末尾
    action_input = m.group(1).strip() if m else ""

    return thought, action, action_input


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：标准格式
    text1 = """Thought: 用户想知道北京天气，我需要调用天气工具。
Action: get_weather
Action Input: {"city": "北京"}"""

    t, a, ai = parse_react_output(text1)
    print(t, a, ai, sep="\n")
    assert "天气" in t, f"Thought 应该包含'天气'，实际: {t!r}"
    assert a == "get_weather", f"Action 应该是 get_weather，实际: {a!r}"
    assert "北京" in ai, f"Action Input 应该包含'北京'，实际: {ai!r}"

    # 测试 2：模型在 Thought 前面多说了一句
    text2 = """好的，让我想想。
Thought: 需要计算 17+25
Action: calculator
Action Input: {"expression": "17+25"}"""

    t, a, ai = parse_react_output(text2)
    assert "计算" in t or "17" in t, f"Thought 解析失败: {t!r}"
    assert a == "calculator", f"Action 应该是 calculator，实际: {a!r}"

    # 测试 3：没有 Action（最终回答）
    text3 = """Thought: 我已经知道答案了，直接回答用户。"""

    t, a, ai = parse_react_output(text3)
    assert len(t) > 0, "Thought 应该有内容"
    assert a == "", f"没有 Action 时应该返回空字符串，实际: {a!r}"
    assert ai == "", f"没有 Action Input 时应该返回空字符串，实际: {ai!r}"

    # 测试 4：返回类型
    result = parse_react_output("Thought: test\nAction: foo\nAction Input: bar")
    assert isinstance(result, tuple) and len(result) == 3, "应该返回三元组"

    print("✅ PASSED: parse_react_output 全部测试通过")
