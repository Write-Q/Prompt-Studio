"""Prompt 组装算法的测试。

既单测 generate_service 里的纯函数（变量提取、渲染、卡片分组），
也通过 /api/generate 端点验证整体组装与缺失变量检测、错误映射。
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import database
from app.main import app
from app.models.schemas import ContextCardResponse
from app.services.generate_service import (
    CARD_TYPE_ORDER,
    build_prompt_by_rules,
    extract_variables,
    format_context_card_sections,
    render_template,
)


class GenerateAlgorithmTests(unittest.TestCase):
    """不依赖数据库的纯算法测试。"""

    def test_extract_variables_unique_and_ordered(self) -> None:
        variables = extract_variables("你好 {name}，欢迎 {city}，再说一次 {name}")
        self.assertEqual(variables, ["name", "city"])

    def test_render_uses_replace_not_format(self) -> None:
        # 模板里混入 JSON 花括号：str.format 会崩，str.replace 不受影响
        template = '请输出 JSON：{"name": value}，主题={topic}'
        result = render_template(template, {"topic": "AI"})
        self.assertIn('{"name": value}', result)  # 非变量花括号原样保留
        self.assertIn("主题=AI", result)
        self.assertNotIn("{topic}", result)

    def test_extract_skips_braces_with_spaces(self) -> None:
        # 含空格的花括号块不会被误判成变量
        self.assertEqual(extract_variables('{"name": value} 和 {topic}'), ["topic"])

    def test_sections_follow_card_type_order(self) -> None:
        cards = [
            self._card("checklist", "清单卡"),
            self._card("background", "背景卡"),
            self._card("rule", "规则卡"),
        ]
        sections = format_context_card_sections(cards)
        labels = [s.splitlines()[0] for s in sections]
        # 顺序应按 CARD_TYPE_ORDER（background 在 rule 在 checklist 之前）
        self.assertEqual(labels, ["【背景资料】", "【写作规则】", "【检查清单】"])
        self.assertEqual(CARD_TYPE_ORDER[0], "background")

    def test_build_prompt_joins_template_and_sections(self) -> None:
        prompt = build_prompt_by_rules(
            "正文 {x}", {"x": "值"}, [self._card("background", "背景卡")]
        )
        self.assertTrue(prompt.startswith("正文 值"))
        self.assertIn("【背景资料】", prompt)
        self.assertIn("背景卡", prompt)

    @staticmethod
    def _card(card_type: str, title: str) -> ContextCardResponse:
        return ContextCardResponse(
            id=1,
            type=card_type,
            title=title,
            tags=[],
            content="内容",
            created_at="2026-05-25T00:00:00",
            updated_at="2026-05-25T00:00:00",
        )


class GenerateEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = Path(tempfile.mkdtemp(prefix="ps_gen_"))
        self._orig_db = database.DB_PATH
        self._orig_dir = database.DATA_DIR
        database.DATA_DIR = self._tmpdir
        database.DB_PATH = self._tmpdir / "test.db"
        database.init_db()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        database.DB_PATH = self._orig_db
        database.DATA_DIR = self._orig_dir
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _new_template(self, content: str) -> int:
        response = self.client.post(
            "/api/templates",
            json={"title": "模板", "tags": [], "content": content},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["id"]

    def _new_card(self) -> int:
        response = self.client.post(
            "/api/context-cards",
            json={"type": "background", "title": "背景", "tags": [], "content": "背景内容"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["id"]

    def test_generate_renders_and_appends_card(self) -> None:
        template_id = self._new_template("写一篇关于 {主题} 的文章")
        card_id = self._new_card()
        response = self.client.post(
            "/api/generate",
            json={
                "template_id": template_id,
                "variables": {"主题": "时间管理"},
                "context_card_ids": [card_id],
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("时间管理", data["final_prompt"])
        self.assertIn("【背景资料】", data["final_prompt"])
        self.assertEqual(data["missing_variables"], [])

    def test_missing_variables_detected(self) -> None:
        template_id = self._new_template("{标题} 和 {正文}")
        response = self.client.post(
            "/api/generate",
            json={"template_id": template_id, "variables": {"标题": "x"}, "context_card_ids": []},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["missing_variables"], ["正文"])

    def test_generate_template_not_found_returns_404(self) -> None:
        response = self.client.post(
            "/api/generate",
            json={"template_id": 9999, "variables": {}, "context_card_ids": []},
        )
        self.assertEqual(response.status_code, 404)

    def test_generate_card_not_found_returns_404(self) -> None:
        template_id = self._new_template("正文 {x}")
        response = self.client.post(
            "/api/generate",
            json={"template_id": template_id, "variables": {"x": "v"}, "context_card_ids": [9999]},
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
