import tempfile
import unittest
from pathlib import Path

import app.database as database
from app.models.schemas import GenerateRequest, GenerationHistoryCreate
from app.main import app
from app.services.generate_service import generate_prompt
from app.services.history_service import create_history, list_history


class ManualHistorySaveTest(unittest.TestCase):
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
                    "Manual save template",
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

    def test_manual_save_keeps_exact_final_prompt_without_required_variables(self):
        payload = GenerationHistoryCreate(
            template_id=self.template_id,
            variables={},
            snippet_ids=[],
            final_prompt="Exact prompt the user chose to save.",
        )

        created = create_history(payload)
        history = list_history(limit=10)

        self.assertEqual(created.final_prompt, "Exact prompt the user chose to save.")
        self.assertEqual(history[0].id, created.id)
        self.assertEqual(history[0].variables, {})

    def test_generate_prompt_only_previews_even_when_variables_are_complete(self):
        result = generate_prompt(
            GenerateRequest(
                template_id=self.template_id,
                variables={"topic": "manual saving"},
                snippet_ids=[],
            )
        )

        self.assertEqual(result.final_prompt, "Write about manual saving")
        self.assertEqual(result.missing_variables, [])
        self.assertIsNone(result.history_id)
        self.assertEqual(list_history(limit=10), [])

    def test_history_save_route_accepts_plain_and_slash_paths(self):
        route_methods = {
            route.path: route.methods
            for route in app.routes
            if hasattr(route, "methods")
        }

        self.assertIn("POST", route_methods["/api/history"])
        self.assertIn("POST", route_methods["/api/history/"])


if __name__ == "__main__":
    unittest.main()
