import json
import os
import urllib.error
import urllib.request
from collections.abc import Iterator

from app.models.schemas import LlmAnswerRequest, LlmAnswerResponse


DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY_ENV = "DEEPSEEK_API_KEY"


class LlmConfigError(Exception):
    """
    大模型配置错误。

    例如：没有配置 DEEPSEEK_API_KEY。
    """


class LlmRequestError(Exception):
    """
    大模型请求错误。

    例如：网络失败、接口返回非 2xx、响应结构异常。
    """


def _get_deepseek_api_key() -> str:
    """
    从环境变量读取 DeepSeek API Key。

    注意：不要把 API Key 写死在代码里，也不要从前端传入。
    """
    api_key = os.getenv(DEEPSEEK_API_KEY_ENV, "").strip()
    if not api_key:
        raise LlmConfigError(
            f"请先配置环境变量 {DEEPSEEK_API_KEY_ENV}，再调用大模型回答接口"
        )

    return api_key


def ask_deepseek(payload: LlmAnswerRequest) -> LlmAnswerResponse:
    """
    调用 DeepSeek Chat Completions 接口生成回答。

    当前设计很克制：只把最终 Prompt 作为 user message 发给模型。
    后续如果要扩展 system prompt、流式输出、多轮对话，可以继续拆分。
    """
    api_key = _get_deepseek_api_key()
    request_body = {
        "model": payload.model,
        "messages": [
            {
                "role": "user",
                "content": payload.prompt,
            }
        ],
        "temperature": payload.temperature,
    }
    request_bytes = json.dumps(request_body, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=request_bytes,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_text = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        error_text = error.read().decode("utf-8", errors="replace")
        raise LlmRequestError(f"DeepSeek 接口返回错误：{error.code} {error_text}") from error
    except urllib.error.URLError as error:
        raise LlmRequestError(f"DeepSeek 请求失败：{error.reason}") from error
    except TimeoutError as error:
        raise LlmRequestError("DeepSeek 请求超时，请稍后再试") from error

    try:
        response_data = json.loads(response_text)
        answer = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, json.JSONDecodeError) as error:
        raise LlmRequestError("DeepSeek 响应结构异常，无法解析回答内容") from error

    return LlmAnswerResponse(model=payload.model, answer=answer)


def _iter_deepseek_stream(response) -> Iterator[str]:
    """
    逐行解析 DeepSeek 的 SSE 流。

    DeepSeek 流式返回的每一行通常形如：
    data: {"choices":[{"delta":{"content":"..."}}]}

    我们只把 delta.content 里的最终回答文本继续传给前端。
    """
    try:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()

            # DeepSeek 文档说明可能会返回空行或 keep-alive 注释，要跳过。
            if not line or line.startswith(":"):
                continue

            if not line.startswith("data:"):
                continue

            data_text = line.removeprefix("data:").strip()
            if data_text == "[DONE]":
                break

            try:
                chunk = json.loads(data_text)
            except json.JSONDecodeError:
                continue

            choices = chunk.get("choices") or []
            if not choices:
                continue

            delta = choices[0].get("delta") or {}
            content = delta.get("content")
            if content:
                yield content
    finally:
        response.close()


def stream_deepseek_answer(payload: LlmAnswerRequest) -> Iterator[str]:
    """
    调用 DeepSeek 流式回答接口。

    与 ask_deepseek 的区别：
    - ask_deepseek 等完整回答结束后一次性返回
    - stream_deepseek_answer 会边收到文本边 yield 给路由层
    """
    api_key = _get_deepseek_api_key()
    request_body = {
        "model": payload.model,
        "messages": [
            {
                "role": "user",
                "content": payload.prompt,
            }
        ],
        "temperature": payload.temperature,
        "stream": True,
    }
    request_bytes = json.dumps(request_body, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=request_bytes,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )

    try:
        response = urllib.request.urlopen(request, timeout=60)
    except urllib.error.HTTPError as error:
        error_text = error.read().decode("utf-8", errors="replace")
        raise LlmRequestError(f"DeepSeek 接口返回错误：{error.code} {error_text}") from error
    except urllib.error.URLError as error:
        raise LlmRequestError(f"DeepSeek 请求失败：{error.reason}") from error
    except TimeoutError as error:
        raise LlmRequestError("DeepSeek 请求超时，请稍后再试") from error

    return _iter_deepseek_stream(response)
