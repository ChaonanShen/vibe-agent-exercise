"""
练习 2.2 · ToolRegistry 注册与调用
====================================

知识点：第 8 节《ToolRegistry》

核心思路：让"注册一个函数 → 它就变成 LLM 可用的工具"成为可能。
  1) register：把函数收集起来
  2) to_schemas：把每个函数自动翻译成 LLM 看得懂的 schema
  3) invoke：LLM 说要调用谁，就找到谁去执行

填空只聚焦上面 3 件事的主线，反射细节（inspect 取参数等）已经实现好了。
"""

import inspect
from typing import Any, Callable


class MiniToolRegistry:
    # Python 类型 → JSON Schema 类型名（已提供，to_schemas 里用 self._TYPE_MAP 查表即可）
    _TYPE_MAP = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }

    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, func: Callable) -> Callable:
        """目标：把 func 收进 self._tools，键是函数名，并把 func 原样返回（这样才能当装饰器用）。"""
        # TODO ① 把 func 放进字典，键是它的函数名
        self._tools[func.__name__] = func  # 【提示🔔】函数名通过 func 的 __name__ 属性获取
        return func

    def to_schemas(self) -> list[dict]:
        """目标：把每个注册的函数翻译成 OpenAI tools 格式的 schema。

        反射相关的细节（取签名、判断默认值）已经写好，无需深究。
        """
        schemas = []
        for name, func in self._tools.items():
            sig = inspect.signature(func)  # 已实现：拿到函数签名

            properties = {}
            required = []
            for param_name, param in sig.parameters.items():
                # 查类型映射表，没注解就当字符串（已实现）
                prop_type = self._TYPE_MAP.get(param.annotation, "string")
                properties[param_name] = {"type": prop_type}

                # 没有默认值 → 必填（已实现）
                if param.default is inspect.Parameter.empty:
                    required.append(param_name)

            # TODO ② 把这个函数的"自我介绍"组装成 LLM 能看懂的 schema
            schema = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": func.__doc__,  # 【提示🔔】函数的文档字符串（docstring）通过 func.__doc__ 获取
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            }
            schemas.append(schema)
        return schemas

    def invoke(self, name: str, args: dict) -> Any:
        """目标：LLM 说要调 name 这个工具、给了 args 字典 → 这里负责真正执行。"""
        # TODO ③ 按名字找到函数，并把 args 作为关键字参数传进去执行
        return self._tools[name](**args)  # 【提示🔔】从 self._tools 取出函数名对应的函数，用 ** 语法把 args 字典拆成关键字参数传进去


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    registry = MiniToolRegistry()

    @registry.register
    def get_weather(city: str, unit: str = "celsius") -> str:
        """查询指定城市的天气"""
        return f"{city}: 晴，25°{unit[0].upper()}"

    @registry.register
    def add(a: int, b: int) -> int:
        """计算两个整数的和"""
        return a + b

    # 测试 register
    assert "get_weather" in registry._tools, "get_weather 应该被注册"
    assert "add" in registry._tools, "add 应该被注册"

    # 测试 to_schemas
    schemas = registry.to_schemas()
    assert len(schemas) == 2, f"应该有 2 个 schema，实际 {len(schemas)}"

    weather_schema = next(s for s in schemas if s["function"]["name"] == "get_weather")
    assert weather_schema["type"] == "function"
    assert "city" in weather_schema["function"]["parameters"]["properties"]
    assert "city" in weather_schema["function"]["parameters"]["required"]
    # unit 有默认值，不应该在 required 里
    assert "unit" not in weather_schema["function"]["parameters"]["required"]

    add_schema = next(s for s in schemas if s["function"]["name"] == "add")
    assert add_schema["function"]["description"] == "计算两个整数的和"
    props = add_schema["function"]["parameters"]["properties"]
    assert props["a"]["type"] == "integer"
    assert props["b"]["type"] == "integer"

    # 测试 invoke
    result = registry.invoke("get_weather", {"city": "北京"})
    assert "北京" in result, f"get_weather 返回应该包含'北京'，实际: {result}"

    result = registry.invoke("add", {"a": 3, "b": 5})
    assert result == 8, f"add(3,5) 应该等于 8，实际: {result}"

    print("✅ PASSED: MiniToolRegistry 全部测试通过")
