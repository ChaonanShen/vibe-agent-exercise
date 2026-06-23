"""
练习 3.3 · Reflection 评审循环
================================

知识点：第 14 节《Reflection 范式》

要求：补全 draft / review / revise 三个 prompt + reflect_and_revise 主循环

Reflection 范式的精髓：**同一个 LLM，通过不同的 system prompt 扮演不同角色**
  - draft：作者   —— 写初稿
  - review：评审员 —— 找问题，并按约定格式输出（让我们能程序化判断是否通过）
  - revise：修订者 —— 拿着评审意见改稿
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _env import chat, get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def draft(task: str) -> str:
    """让 LLM 扮演【作者】生成初稿。"""
    msg = chat(
        messages=[
            # TODO ① 让模型进入【作者】角色：根据任务要求写出一段内容
            {"role": "system", "content": ...},  # 提示：一句话点明身份 + 要做的事即可，比如"你是…，请根据任务…"
            {"role": "user", "content": task},
        ],
        client=client,
        model=MODEL,
    )
    return msg.content


def review(task: str, content: str) -> tuple[bool, str]:
    """让 LLM 扮演【评审员】，返回 (是否通过, 评审意见)。

    关键约定：模型必须**第一行只写 PASS 或 FAIL**，后面再写意见 —— 这样下面才能用
    `text.split("\\n")[0]` 解析出 bool。这条格式约束就是 Reflection 能闭环的基础。
    """
    msg = chat(
        messages=[
            # TODO ② 让模型进入【评审员】角色，并强制约定输出格式
            {"role": "system", "content": ...},  # 提示：身份之外，必须硬性约定"第一行只写 PASS 或 FAIL"——否则下面 split 首行解析不出 bool
            {"role": "user", "content": f"任务: {task}\n\n待评审内容:\n{content}"},
        ],
        client=client,
        model=MODEL,
    )
    text = msg.content

    # 解析约定格式：第一行包含 PASS → 通过（已实现）
    passed = "PASS" in text.split("\n")[0].upper()

    return passed, text


def revise(task: str, content: str, feedback: str) -> str:
    """让 LLM 扮演【修订者】，根据评审意见改写并输出完整版本。"""
    msg = chat(
        messages=[
            # TODO ③ 让模型进入【修订者】角色：基于评审意见改写，输出修订后的完整版本
            {"role": "system", "content": ...},  # 提示：和 draft 不同，这次有"原稿+评审意见"两份输入，要交代清楚是"参考意见改写"而非"重新写一份"
            {"role": "user", "content": f"任务: {task}\n\n当前内容:\n{content}\n\n评审意见:\n{feedback}"},
        ],
        client=client,
        model=MODEL,
    )
    return msg.content


def reflect_and_revise(task: str, max_rounds: int = 3) -> str:
    """Reflection 主循环 — 起草 → 评审 → 修订 → ... → 返回最终版本。"""
    # 先生成初稿（已实现）
    content = draft(task)

    # 评审 → 不通过就修订 → 再评审，直到通过或用完轮次
    for i in range(max_rounds):
        passed, feedback = review(task, content)
        if passed:
            break

        # TODO ④ 没通过：把评审意见反馈给 LLM，让它改出新版本，覆盖掉旧的 content
        content = ...  # 想想：上面三个函数里，哪个负责"根据反馈改稿"？它需要哪三个输入？

    return content


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：基本功能
    result = reflect_and_revise("写一个 Python 函数，计算斐波那契数列第 n 项，要求有 docstring 和类型注解")
    assert isinstance(result, str), "应该返回字符串"
    assert len(result) > 20, f"结果太短了: {result!r}"
    assert "def" in result or "fib" in result.lower(), "结果应该包含函数定义"
    print(f"[测试1] 最终结果 ({len(result)} 字符):")
    print(result[:200] + "..." if len(result) > 200 else result)

    # 测试 2：review 函数基本工作
    passed, feedback = review("写一首五言绝句", "床前明月光，疑是地上霜。举头望明月，低头思故乡。")
    assert isinstance(passed, bool), "passed 应该是 bool"
    assert isinstance(feedback, str), "feedback 应该是字符串"
    print(f"\n[测试2] review 结果: passed={passed}, feedback={feedback[:50]}...")

    # 测试 3：max_rounds 参数生效
    result2 = reflect_and_revise("用一句话解释什么是 AI", max_rounds=1)
    assert isinstance(result2, str) and len(result2) > 0, "max_rounds=1 也应该返回结果"

    print("\n✅ PASSED: reflect_and_revise 全部测试通过")
