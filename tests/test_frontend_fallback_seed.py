"""前端入口与“空库回退 / 种子数据可见”的衔接测试。

验证三件事：
1. 前端单页入口 /app/ 能被静态托管正常返回；
2. 数据库为空时，各列表接口优雅地返回空数组而非报错；
3. 注入种子数据后，前端依赖的列表接口能拿到这些数据。
"""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

import seed_test_data as seed
from app import database
from app.main import app

from fastapi.testclient import TestClient


class FrontendFallbackSeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = Path(tempfile.mkdtemp(prefix="ps_front_"))
        self._orig_db = database.DB_PATH
        self._orig_dir = database.DATA_DIR
        self._orig_seed_db = seed.DB_PATH
        database.DATA_DIR = self._tmpdir
        database.DB_PATH = self._tmpdir / "test.db"
        seed.DB_PATH = database.DB_PATH
        database.init_db()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        database.DB_PATH = self._orig_db
        database.DATA_DIR = self._orig_dir
        seed.DB_PATH = self._orig_seed_db
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_frontend_entry_is_served(self) -> None:
        response = self.client.get("/app/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))

    def test_empty_db_lists_return_empty_arrays(self) -> None:
        for path in ("/api/templates", "/api/context-cards", "/api/history"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, f"{path}: {response.text}")
            self.assertEqual(response.json(), [], path)

    def test_seeded_data_visible_to_frontend(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            seed.main()

        templates = self.client.get("/api/templates", params={"limit": 500}).json()
        cards = self.client.get("/api/context-cards", params={"limit": 500}).json()
        self.assertEqual(len(templates), len(seed.TEMPLATES))
        self.assertEqual(len(cards), len(seed.CONTEXT_CARDS))


if __name__ == "__main__":
    unittest.main()
