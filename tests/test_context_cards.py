import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

import app.database as database
from app.models.schemas import ContextCardCreate, ContextCardUpdate, GenerateRequest, GenerationHistoryCreate
from app.services.context_card_service import (
    ContextCardNotFoundError,
    create_context_card,
    delete_context_card,
    get_context_card_by_id,
    list_context_cards,
    update_context_card,
)
from app.services.generate_service import generate_prompt
from app.services.history_service import create_history, list_history


class ContextCardTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = Path(self.temp_dir.name) / "app.db"
        database.init_db()

        with database.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO prompt_templates (
                    title, category, tags, content, description, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Context card template",
                    "test",
                    "[]",
                    "Write about {topic}",
                    "",
                    "2026-05-13 00:00:00",
                    "2026-05-13 00:00:00",
                ),
            )
            connection.commit()
            self.template_id = cursor.lastrowid

    def tearDown(self):
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_context_card_crud_filters_and_tags(self):
        card = create_context_card(
            ContextCardCreate(
                type="rule",
                title="Tone rule",
                tags="writing, concise",
                content="Be direct.",
            )
        )

        self.assertEqual(card.type, "rule")
        self.assertEqual(card.tags, ["writing", "concise"])
        self.assertFalse(hasattr(card, "source"))
        self.assertEqual(list_context_cards(type="rule")[0].id, card.id)
        self.assertEqual(list_context_cards(tag="concise")[0].id, card.id)
        self.assertEqual(list_context_cards(keyword="direct")[0].id, card.id)

        updated = update_context_card(
            card.id,
            ContextCardUpdate(
                type="format",
                title="Output format",
                tags=["format"],
                content="Use bullets.",
            ),
        )

        self.assertEqual(updated.type, "format")
        self.assertEqual(get_context_card_by_id(card.id).title, "Output format")
        self.assertTrue(delete_context_card(card.id))

        with self.assertRaises(ContextCardNotFoundError):
            get_context_card_by_id(card.id)

    def test_context_card_type_must_be_known(self):
        with self.assertRaises(ValidationError):
            ContextCardCreate(
                type="free",
                title="Invalid",
                tags=[],
                content="Nope.",
            )

    def test_generate_prompt_groups_selected_cards_by_type(self):
        example = create_context_card(
            ContextCardCreate(type="example", title="Sample", tags=[], content="Input -> Output")
        )
        rule = create_context_card(
            ContextCardCreate(type="rule", title="Tone", tags=[], content="Be concise.")
        )
        output_format = create_context_card(
            ContextCardCreate(type="format", title="Format", tags=[], content="Use bullets.")
        )

        result = generate_prompt(
            GenerateRequest(
                template_id=self.template_id,
                variables={"topic": "AI"},
                context_card_ids=[example.id, rule.id, output_format.id],
            )
        )

        self.assertEqual(
            result.final_prompt,
            "Write about AI\n\n"
            "【写作规则】\n- Tone\nBe concise.\n\n"
            "【输出格式】\n- Format\nUse bullets.\n\n"
            "【参考示例】\n- Sample\nInput -> Output",
        )
        self.assertEqual(result.context_card_ids, [example.id, rule.id, output_format.id])

    def test_missing_variables_preview_does_not_save_history(self):
        card = create_context_card(
            ContextCardCreate(type="background", title="Project", tags=[], content="Context.")
        )

        result = generate_prompt(
            GenerateRequest(
                template_id=self.template_id,
                variables={},
                context_card_ids=[card.id],
            )
        )

        self.assertEqual(result.missing_variables, ["topic"])
        self.assertIn("【背景资料】", result.final_prompt)
        self.assertIsNone(result.history_id)
        self.assertEqual(list_history(limit=10), [])

    def test_manual_history_save_stores_context_card_ids(self):
        card = create_context_card(
            ContextCardCreate(type="checklist", title="Review", tags=[], content="Check facts.")
        )

        history = create_history(
            GenerationHistoryCreate(
                template_id=self.template_id,
                variables={"topic": "quality"},
                context_card_ids=[card.id],
                final_prompt="Saved prompt.",
            )
        )

        self.assertEqual(history.context_card_ids, [card.id])
        self.assertEqual(list_history(limit=1)[0].context_card_ids, [card.id])


if __name__ == "__main__":
    unittest.main()
