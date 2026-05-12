import tempfile
import unittest
from pathlib import Path

from app import database
from app.models.schemas import GenerateRequest, KnowledgeSnippetCreate, PromptTemplateCreate
from app.services.common import deserialize_tags, serialize_tags
from app.services.generate_service import extract_variables, generate_prompt, render_template
from app.services.snippet_service import create_snippet
from app.services.template_service import create_template


class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.old_data_dir = database.DATA_DIR
        self.old_db_path = database.DB_PATH
        database.DATA_DIR = Path(self.temp_dir.name)
        database.DB_PATH = database.DATA_DIR / "test.db"
        database.init_db()

    def tearDown(self):
        database.DATA_DIR = self.old_data_dir
        database.DB_PATH = self.old_db_path
        self.temp_dir.cleanup()

    def history_count(self):
        with database.get_connection() as connection:
            return connection.execute("SELECT COUNT(*) FROM generation_history").fetchone()[0]


class PromptRuleTests(ServiceTestCase):
    def test_extract_variables_keeps_first_seen_order(self):
        content = "请用{语气}处理{输入内容}，再检查{语气}。"

        self.assertEqual(extract_variables(content), ["语气", "输入内容"])

    def test_render_template_keeps_missing_placeholders(self):
        content = "请用{语气}总结：{输入内容}"

        self.assertEqual(render_template(content, {"语气": "简洁"}), "请用简洁总结：{输入内容}")

    def test_generate_prompt_formats_snippets_with_titles(self):
        template = create_template(
            PromptTemplateCreate(title="总结", content="总结：{输入内容}")
        )
        snippet = create_snippet(
            KnowledgeSnippetCreate(title="输出原则", content="使用清单。")
        )

        result = generate_prompt(
            GenerateRequest(
                template_id=template.id,
                variables={"输入内容": "项目进展"},
                snippet_ids=[snippet.id],
            )
        )

        self.assertIn("参考知识片段：\n- 输出原则\n使用清单。", result.final_prompt)

    def test_generate_prompt_does_not_save_history_when_variables_missing(self):
        template = create_template(
            PromptTemplateCreate(title="总结", content="总结：{输入内容}")
        )

        result = generate_prompt(
            GenerateRequest(template_id=template.id, variables={}, snippet_ids=[])
        )

        self.assertEqual(result.missing_variables, ["输入内容"])
        self.assertIsNone(result.history_id)
        self.assertEqual(self.history_count(), 0)


class CommonServiceTests(unittest.TestCase):
    def test_tags_round_trip_as_json(self):
        self.assertEqual(deserialize_tags(serialize_tags(["写作", "总结"])), ["写作", "总结"])

    def test_tags_fall_back_to_comma_text(self):
        self.assertEqual(deserialize_tags("写作，总结"), ["写作", "总结"])


if __name__ == "__main__":
    unittest.main()
