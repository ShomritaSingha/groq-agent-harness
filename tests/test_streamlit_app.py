"""Run with: uv run python -m unittest discover -s tests"""

import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from groq import AuthenticationError, RateLimitError
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "ap.py"


class ChatAppTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.dotenv = patch("dotenv.load_dotenv")
        self.dotenv.start()
        self.addCleanup(self.dotenv.stop)
        self.groq = patch("groq.Groq")
        self.client_class = self.groq.start()
        self.addCleanup(self.groq.stop)
        self.create = self.client_class.return_value.__enter__.return_value.chat.completions.create
        self.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello!"))]
        )

    def test_chat_history_clear_and_session_isolation(self):
        app = AppTest.from_file(str(APP)).run()
        self.assertFalse(app.exception)
        app.chat_input[0].set_value("Hello").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.chat_message), 2)
        self.assertEqual(app.session_state.messages[-1]["content"], "Hello!")
        app.chat_input[0].set_value("Remember my greeting?").run()
        request = self.create.call_args.kwargs
        self.assertEqual(request["model"], "openai/gpt-oss-120b")
        self.assertEqual([m["role"] for m in request["messages"]], ["system", "user", "assistant", "user"])
        other = AppTest.from_file(str(APP)).run()
        self.assertEqual(other.session_state.messages, [])
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.messages, [])

    def test_missing_key_disables_input(self):
        os.environ.pop("GROQ_API_KEY", None)
        with patch("streamlit.runtime.secrets.Secrets.get", return_value=""):
            app = AppTest.from_file(str(APP)).run()
        self.assertFalse(app.exception)
        self.assertTrue(app.chat_input[0].disabled)
        self.client_class.assert_not_called()

    def test_streamlit_secret_is_used(self):
        os.environ.pop("GROQ_API_KEY", None)
        with patch("streamlit.runtime.secrets.Secrets.get", return_value="cloud-test-key"):
            app = AppTest.from_file(str(APP)).run()
            app.chat_input[0].set_value("Hello").run()
        self.assertFalse(app.exception)
        self.assertEqual(self.client_class.call_args.kwargs["api_key"], "cloud-test-key")

    def test_api_errors_leave_history_unchanged_and_hide_raw_error(self):
        for exception, status, output in (
            (AuthenticationError, 401, "error"),
            (RateLimitError, 429, "warning"),
        ):
            with self.subTest(status=status):
                response = httpx.Response(status, request=httpx.Request("POST", "https://api.groq.com"))
                self.create.side_effect = exception("private-error-detail", response=response, body=None)
                app = AppTest.from_file(str(APP)).run()
                app.chat_input[0].set_value("Hello").run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state.messages, [])
                self.assertTrue(getattr(app, output))
                self.assertNotIn("private-error-detail", getattr(app, output)[0].value)


if __name__ == "__main__":
    unittest.main()
