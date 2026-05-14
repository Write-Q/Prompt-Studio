import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import app.database as database
import seed_test_data
from app.services.generate_service import extract_variables


class SeedTestDataTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db_path = database.DB_PATH
        self.original_seed_db_path = seed_test_data.DB_PATH
        self.db_path = Path(self.temp_dir.name) / "app.db"
        database.DB_PATH = self.db_path
        seed_test_data.DB_PATH = self.db_path

    def tearDown(self):
        database.DB_PATH = self.original_db_path
        seed_test_data.DB_PATH = self.original_seed_db_path
        self.temp_dir.cleanup()

    def _rows(self, table: str):
        with database.get_connection() as connection:
            return connection.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()

    def test_seed_data_has_expected_size_keys_types_and_template_variables(self):
        self.assertEqual(len(seed_test_data.TEMPLATES), 10)
        self.assertEqual(len(seed_test_data.CONTEXT_CARDS), 30)

        template_keys = [item["seed_key"] for item in seed_test_data.TEMPLATES]
        card_keys = [item["seed_key"] for item in seed_test_data.CONTEXT_CARDS]
        self.assertEqual(len(template_keys), len(set(template_keys)))
        self.assertEqual(len(card_keys), len(set(card_keys)))

        type_counts = {}
        for card in seed_test_data.CONTEXT_CARDS:
            self.assertNotIn("source", card)
            type_counts[card["type"]] = type_counts.get(card["type"], 0) + 1
        self.assertEqual(
            type_counts,
            {"background": 5, "rule": 7, "format": 7, "example": 6, "checklist": 5},
        )

        expected_titles = {
            "日程规划助手",
            "学习笔记整理",
            "资料总结与重点提取",
            "文章润色改写",
            "工作周报整理",
            "会议纪要整理",
            "沟通表达优化",
            "旅行攻略规划",
            "商品对比决策",
            "一周饮食计划",
        }
        self.assertEqual({template["title"] for template in seed_test_data.TEMPLATES}, expected_titles)

        forbidden_fragments = {"大白话", "专业说明"}
        allowed_variables = {
            "计划周期",
            "可用时间",
            "精力状态",
            "待安排事项",
            "学习主题",
            "学习目标",
            "学习材料",
            "资料类型",
            "总结目的",
            "目标读者",
            "资料内容",
            "原文",
            "改写目标",
            "保留要求",
            "角色",
            "周期",
            "工作记录",
            "会议主题",
            "参会对象",
            "会议记录",
            "沟通对象",
            "沟通目标",
            "原始表达",
            "目的地",
            "出行天数",
            "预算范围",
            "偏好限制",
            "同行人和特殊需求",
            "购买需求",
            "候选商品",
            "关键标准",
            "当前顾虑",
            "饮食目标",
            "人数",
            "忌口限制",
            "现有食材和烹饪条件",
        }
        for template in seed_test_data.TEMPLATES:
            self.assertTrue(template["seed_key"])
            self.assertTrue(template["title"])
            self.assertTrue(template["content"])
            self.assertTrue(template["description"])
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, template["description"])
                self.assertNotIn(fragment, template["content"])
            self.assertNotIn("{输入内容}", template["content"])
            variables = extract_variables(template["content"])
            self.assertTrue(variables)
            self.assertLessEqual(set(variables), allowed_variables)

    def test_seed_main_replaces_old_builtin_rows_and_preserves_user_rows(self):
        database.init_db()
        with database.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO prompt_templates (
                    seed_key, title, category, tags, content, description, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "prompt_task_brief_builder",
                    "Prompt 需求澄清与模板生成",
                    "旧种子",
                    "[]",
                    "应该被清理的旧版 seed_key 内容",
                    "旧版内置模板",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                ),
            )
            cursor.execute(
                """
                INSERT INTO prompt_templates (
                    title, category, tags, content, description, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "通用任务分析",
                    "旧分类",
                    "[]",
                    "旧模板内容",
                    "旧说明",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                ),
            )
            cursor.execute(
                """
                INSERT INTO prompt_templates (
                    title, category, tags, content, description, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Prompt 需求澄清与模板生成",
                    "旧种子",
                    "[]",
                    "应该被清理的旧版种子内容",
                    "旧版内置模板",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                ),
            )
            cursor.execute(
                """
                INSERT INTO prompt_templates (
                    title, category, tags, content, description, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "用户自己的模板",
                    "私人",
                    json.dumps(["private"], ensure_ascii=False),
                    "不要覆盖我",
                    "用户创建",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                ),
            )
            cursor.execute(
                """
                INSERT INTO context_cards (
                    seed_key, type, title, tags, content, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "context_promptstudio_model",
                    "background",
                    "PromptStudio 工作台使用模型",
                    "[]",
                    "旧 seed_key 卡片内容",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                ),
            )
            cursor.execute(
                """
                INSERT INTO context_cards (
                    type, title, tags, content, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "background",
                    "PromptStudio 工作台使用模型",
                    "[]",
                    "旧卡片内容",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                ),
            )
            cursor.execute(
                """
                INSERT INTO context_cards (
                    type, title, tags, content, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "rule",
                    "用户自己的卡片",
                    json.dumps(["private"], ensure_ascii=False),
                    "不要覆盖我",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                ),
            )
            connection.commit()

        with redirect_stdout(io.StringIO()):
            seed_test_data.main()
            seed_test_data.main()

        templates = self._rows("prompt_templates")
        cards = self._rows("context_cards")

        self.assertEqual(len(templates), 11)
        self.assertEqual(len(cards), 31)
        self.assertNotIn("Prompt 需求澄清与模板生成", [row["title"] for row in templates])
        self.assertNotIn("prompt_task_brief_builder", [row["seed_key"] for row in templates])
        self.assertNotIn("context_promptstudio_model", [row["seed_key"] for row in cards])

        seeded_template = next(row for row in templates if row["seed_key"] == "daily_schedule_planner")
        self.assertEqual(seeded_template["title"], "日程规划助手")
        self.assertNotEqual(seeded_template["content"], "旧模板内容")

        seeded_card = next(row for row in cards if row["seed_key"] == "background_promptstudio_daily_use")
        self.assertEqual(seeded_card["title"], "PromptStudio 日常使用方式")
        self.assertNotEqual(seeded_card["content"], "旧卡片内容")

        user_template = next(row for row in templates if row["title"] == "用户自己的模板")
        self.assertIsNone(user_template["seed_key"])
        self.assertEqual(user_template["content"], "不要覆盖我")

        user_card = next(row for row in cards if row["title"] == "用户自己的卡片")
        self.assertIsNone(user_card["seed_key"])
        self.assertEqual(user_card["content"], "不要覆盖我")

    def test_init_db_migrates_legacy_context_cards_table_without_source_column(self):
        database.DATA_DIR.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database.DB_PATH)
        try:
            connection.execute(
                """
                CREATE TABLE context_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    tags TEXT,
                    source TEXT,
                    content TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT,
                    seed_key TEXT
                )
                """
            )
            connection.execute(
                """
                INSERT INTO context_cards (
                    type, title, tags, source, content, created_at, updated_at, seed_key
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "rule",
                    "旧卡片",
                    "[]",
                    "旧来源",
                    "旧内容",
                    "2026-05-13T00:00:00",
                    "2026-05-13T00:00:00",
                    None,
                ),
            )
            connection.commit()
        finally:
            connection.close()

        database.init_db()

        with database.get_connection() as migrated:
            columns = {row["name"] for row in migrated.execute("PRAGMA table_info(context_cards)")}
            row = migrated.execute("SELECT title, content, seed_key FROM context_cards").fetchone()

        self.assertNotIn("source", columns)
        self.assertEqual(row["title"], "旧卡片")
        self.assertEqual(row["content"], "旧内容")
        self.assertIsNone(row["seed_key"])


if __name__ == "__main__":
    unittest.main()
