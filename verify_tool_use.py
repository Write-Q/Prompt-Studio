"""手动验证 Tool Use（函数调用）是否打通（需联网 + DeepSeek API Key）。

运行：
    $env:DEEPSEEK_API_KEY="你的 Key"
    .\.venv\Scripts\python.exe verify_tool_use.py
    # 提示：库里要有数据才有东西可检索，可先跑 seed_test_data.py

脚本发两个问题，观察模型「自己决定要不要调工具」：
  1. 需要检索的问题 —— 预期会调用工具
  2. 闲聊问题       —— 预期直接回答，不调工具
"""

from app.models.schemas import LlmChatRequest
from app.services.llm_service import LlmConfigError, LlmRequestError, chat_with_tools


def _run(prompt: str) -> None:
    print("=" * 64)
    print(f"用户：{prompt}")
    response = chat_with_tools(LlmChatRequest(prompt=prompt))
    print(f"轮数：{response.rounds}   工具调用次数：{len(response.tool_calls)}")
    for index, call in enumerate(response.tool_calls, start=1):
        preview = call.result if len(call.result) <= 120 else call.result[:120] + "..."
        print(f"  [{index}] 工具={call.name}  参数={call.arguments}")
        print(f"      结果={preview}")
    print(f"回答：{response.answer}\n")


def main() -> None:
    try:
        _run("帮我找几张和公文写作有关的上下文卡片，并说明各自用途")
        _run("你好，用一句话介绍你自己")
    except LlmConfigError as error:
        print(f"[配置错误] {error}")
    except LlmRequestError as error:
        print(f"[请求失败] {error}")


if __name__ == "__main__":
    main()
