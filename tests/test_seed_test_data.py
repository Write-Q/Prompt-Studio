"""示例数据注入脚本 seed_test_data 的测试。

把脚本与数据库都指向临时库，验证：种子模板 / 卡片全部写入、
五种卡片类型齐全、以及脚本可重复执行（幂等，再跑一次数量不变）。
"""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

import seed_test_data as seed
from app import database


class SeedTestDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = Path(tempfile.mkdtemp(prefix="ps_seed_"))
        self._orig_db = database.DB_PATH
        self._orig_dir = database.DATA_DIR
        self._orig_seed_db = seed.DB_PATH
        database.DATA_DIR = self._tmpdir
        database.DB_PATH = self._tmpdir / "test.db"
        seed.DB_PATH = database.DB_PATH

    def tearDown(self) -> None:
        database.DB_PATH = self._orig_db
        database.DATA_DIR = self._orig_dir
        seed.DB_PATH = self._orig_seed_db
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _run_seed(self) -> None:
        # 脚本会向 stdout 打印统计信息，测试时静默掉
        with contextlib.redirect_stdout(io.StringIO()):
            seed.main()

    def _count(self, table: str) -> int:
        with database.get_connection() as connection:
            return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_seed_inserts_all_templates_and_cards(self) -> None:
        self._run_seed()
        self.assertEqual(self._count("prompt_templates"), len(seed.TEMPLATES))
        self.assertEqual(self._count("context_cards"), len(seed.CONTEXT_CARDS))

    def test_card_types_cover_all_five(self) -> None:
        self._run_seed()
        with database.get_connection() as connection:
            rows = connection.execute("SELECT DISTINCT type FROM context_cards").fetchall()
        types = {row[0] for row in rows}
        self.assertEqual(types, {"background", "rule", "format", "example", "checklist"})

    def test_seed_is_idempotent(self) -> None:
        self._run_seed()
        templates_after_first = self._count("prompt_templates")
        cards_after_first = self._count("context_cards")

        self._run_seed()
        self.assertEqual(self._count("prompt_templates"), templates_after_first)
        self.assertEqual(self._count("context_cards"), cards_after_first)


if __name__ == "__main__":
    unittest.main()
