"""生成记录“手动保存”相关路由的测试。

覆盖 POST /api/history（含带斜杠变体）、模板不存在的 404、
变量与卡片 id 的 JSON 快照往返、列表 / 详情 / 删除。
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import database
from app.main import app


class HistoryManualSaveTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = Path(tempfile.mkdtemp(prefix="ps_history_"))
        self._orig_db = database.DB_PATH
        self._orig_dir = database.DATA_DIR
        database.DATA_DIR = self._tmpdir
        database.DB_PATH = self._tmpdir / "test.db"
        database.init_db()
        self.client = TestClient(app)
        self.template_id = self._new_template()

    def tearDown(self) -> None:
        database.DB_PATH = self._orig_db
        database.DATA_DIR = self._orig_dir
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _new_template(self) -> int:
        response = self.client.post(
            "/api/templates",
            json={"title": "模板", "tags": [], "content": "正文 {x}"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["id"]

    def _payload(self, **overrides) -> dict:
        payload = {
            "template_id": self.template_id,
            "variables": {"x": "值"},
            "context_card_ids": [1, 2],
            "final_prompt": "组装好的最终 Prompt",
        }
        payload.update(overrides)
        return payload

    def test_manual_save_creates_history(self) -> None:
        response = self.client.post("/api/history", json=self._payload())
        self.assertEqual(response.status_code, 201, response.text)
        data = response.json()
        self.assertEqual(data["template_id"], self.template_id)
        self.assertEqual(data["variables"], {"x": "值"})
        self.assertEqual(data["context_card_ids"], [1, 2])
        self.assertEqual(data["final_prompt"], "组装好的最终 Prompt")
        self.assertTrue(data["created_at"])

    def test_trailing_slash_variant_also_works(self) -> None:
        response = self.client.post("/api/history/", json=self._payload())
        self.assertEqual(response.status_code, 201, response.text)

    def test_save_with_unknown_template_returns_404(self) -> None:
        response = self.client.post("/api/history", json=self._payload(template_id=9999))
        self.assertEqual(response.status_code, 404)

    def test_detail_round_trips_json_snapshot(self) -> None:
        created = self.client.post("/api/history", json=self._payload()).json()
        detail = self.client.get(f"/api/history/{created['id']}")
        self.assertEqual(detail.status_code, 200, detail.text)
        data = detail.json()
        self.assertEqual(data["variables"], {"x": "值"})
        self.assertEqual(data["context_card_ids"], [1, 2])

    def test_list_returns_newest_first(self) -> None:
        first = self.client.post("/api/history", json=self._payload(final_prompt="第一条")).json()
        second = self.client.post("/api/history", json=self._payload(final_prompt="第二条")).json()
        items = self.client.get("/api/history").json()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["id"], second["id"])
        self.assertEqual(items[1]["id"], first["id"])

    def test_detail_missing_returns_404(self) -> None:
        self.assertEqual(self.client.get("/api/history/9999").status_code, 404)

    def test_delete_history(self) -> None:
        created = self.client.post("/api/history", json=self._payload()).json()
        response = self.client.delete(f"/api/history/{created['id']}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"success": True})
        self.assertEqual(self.client.get(f"/api/history/{created['id']}").status_code, 404)

    def test_delete_missing_returns_404(self) -> None:
        self.assertEqual(self.client.delete("/api/history/9999").status_code, 404)


if __name__ == "__main__":
    unittest.main()
