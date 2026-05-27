"""上下文卡片路由的集成测试。

通过 FastAPI TestClient 走完整的 HTTP 链路（路由 → 服务 → SQLite），
每个用例使用独立的临时数据库，互不影响。
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import database
from app.main import app


class ContextCardsRoutesTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = Path(tempfile.mkdtemp(prefix="ps_cards_"))
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

    def _create(self, **overrides) -> dict:
        payload = {
            "type": "background",
            "title": "背景卡片",
            "tags": ["测试", "背景"],
            "content": "这是一段背景资料。",
        }
        payload.update(overrides)
        response = self.client.post("/api/context-cards", json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_create_context_card(self) -> None:
        card = self._create()
        self.assertIsInstance(card["id"], int)
        self.assertEqual(card["type"], "background")
        self.assertEqual(card["title"], "背景卡片")
        self.assertEqual(card["tags"], ["测试", "背景"])
        self.assertNotIn("seed_key", card)
        self.assertTrue(card["created_at"])

    def test_tags_accept_chinese_separators(self) -> None:
        # 中文顿号 / 全角逗号 / 半角逗号都应被规整成 list[str]
        card = self._create(tags="规划、效率，计划")
        self.assertEqual(card["tags"], ["规划", "效率", "计划"])

    def test_list_filters_by_type(self) -> None:
        self._create(type="background", title="背景")
        self._create(type="rule", title="规则")
        self._create(type="rule", title="规则二")

        all_cards = self.client.get("/api/context-cards").json()
        self.assertEqual(len(all_cards), 3)

        rules = self.client.get("/api/context-cards", params={"type": "rule"}).json()
        self.assertEqual(len(rules), 2)
        self.assertTrue(all(c["type"] == "rule" for c in rules))

    def test_list_filters_by_keyword(self) -> None:
        self._create(title="日程规划", content="安排一天的事项")
        self._create(title="无关卡片", content="其它内容")
        hits = self.client.get("/api/context-cards", params={"keyword": "日程"}).json()
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["title"], "日程规划")

    def test_get_missing_card_returns_404(self) -> None:
        response = self.client.get("/api/context-cards/9999")
        self.assertEqual(response.status_code, 404)

    def test_update_context_card(self) -> None:
        card = self._create()
        response = self.client.put(
            f"/api/context-cards/{card['id']}",
            json={
                "type": "rule",
                "title": "改成规则",
                "tags": ["新标签"],
                "content": "更新后的内容。",
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        updated = response.json()
        self.assertEqual(updated["type"], "rule")
        self.assertEqual(updated["title"], "改成规则")
        self.assertEqual(updated["tags"], ["新标签"])

    def test_update_missing_card_returns_404(self) -> None:
        response = self.client.put(
            "/api/context-cards/9999",
            json={"type": "rule", "title": "x", "tags": [], "content": "y"},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_context_card(self) -> None:
        card = self._create()
        response = self.client.delete(f"/api/context-cards/{card['id']}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"success": True})
        self.assertEqual(self.client.get(f"/api/context-cards/{card['id']}").status_code, 404)

    def test_delete_missing_card_returns_404(self) -> None:
        self.assertEqual(self.client.delete("/api/context-cards/9999").status_code, 404)

    def test_create_rejects_empty_title(self) -> None:
        response = self.client.post(
            "/api/context-cards",
            json={"type": "background", "title": "   ", "tags": [], "content": "内容"},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
