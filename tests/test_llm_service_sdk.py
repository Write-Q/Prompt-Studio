import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.models.schemas import LlmAnswerRequest
from app.services import llm_service


class DeepSeekSdkIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.original_api_key = os.environ.get(llm_service.DEEPSEEK_API_KEY_ENV)
        os.environ[llm_service.DEEPSEEK_API_KEY_ENV] = "test-key"

    def tearDown(self):
        if self.original_api_key is None:
            os.environ.pop(llm_service.DEEPSEEK_API_KEY_ENV, None)
        else:
            os.environ[llm_service.DEEPSEEK_API_KEY_ENV] = self.original_api_key

    def test_post_chat_completion_uses_deepseek_openai_compatible_client(self):
        fake_completion = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="DeepSeek answer"),
                )
            ]
        )

        with patch("app.services.llm_service.OpenAI") as openai_class:
            client = openai_class.return_value
            client.chat.completions.create.return_value = fake_completion

            answer = llm_service._post_chat_completion(
                {
                    "model": "deepseek-v4-flash",
                    "messages": [{"role": "user", "content": "hello"}],
                    "temperature": 0.7,
                }
            )

        self.assertEqual(answer, "DeepSeek answer")
        openai_class.assert_called_once_with(
            api_key="test-key",
            base_url=llm_service.DEEPSEEK_BASE_URL,
        )
        client.chat.completions.create.assert_called_once_with(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": "hello"}],
            temperature=0.7,
            stream=False,
            timeout=60,
        )

    def test_stream_deepseek_answer_reads_sdk_delta_chunks(self):
        fake_stream = [
            SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content="Hello")),
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content=None)),
                ]
            ),
            SimpleNamespace(choices=[]),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content=" world")),
                ]
            ),
        ]

        with patch("app.services.llm_service.OpenAI") as openai_class:
            client = openai_class.return_value
            client.chat.completions.create.return_value = fake_stream

            chunks = list(
                llm_service.stream_deepseek_answer(
                    LlmAnswerRequest(
                        prompt="hello",
                        model="deepseek-v4-flash",
                        temperature=0.7,
                    )
                )
            )

        self.assertEqual(chunks, ["Hello", " world"])
        client.chat.completions.create.assert_called_once_with(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": "hello"}],
            temperature=0.7,
            stream=True,
            timeout=60,
        )


if __name__ == "__main__":
    unittest.main()
