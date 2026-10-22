"""Boundary checks for Git input, Ollama responses, and digest persistence."""

import io
import json
import os
import subprocess
import tempfile
import unittest
import urllib.error
from unittest import mock

import slothpulse


class GitHistoryTests(unittest.TestCase):
    def test_reads_only_the_eight_most_recent_commits_from_target_repo(self):
        with tempfile.TemporaryDirectory() as repo:
            subprocess.run(["git", "init", "-q", repo], check=True)
            for index in range(9):
                subprocess.run(
                    [
                        "git", "-c", "user.name=SlothPulse Demo",
                        "-c", "user.email=demo@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                        "commit", "-q", "--allow-empty", "-m", "Change {}".format(index),
                    ],
                    cwd=repo,
                    check=True,
                )
            history = slothpulse.get_git_log(repo)
            self.assertEqual(len(history.splitlines()), 8)
            self.assertIn("SlothPulse Demo: Change 8", history)
            self.assertNotIn("Change 0", history)

    def test_non_repository_is_reported_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIn("Git history unavailable", slothpulse.get_git_log(folder))


class OllamaTests(unittest.TestCase):
    def setUp(self):
        self.patch = mock.patch("slothpulse.urllib.request.build_opener")
        self.build_opener = self.patch.start()
        self.addCleanup(self.patch.stop)
        self.opener = self.build_opener.return_value

    def reply(self, body):
        self.opener.open.return_value = io.BytesIO(body)

    def test_sends_non_streaming_json_to_local_endpoint_without_proxy(self):
        self.reply(json.dumps({"response": "  ### Digest 🦥  "}).encode("utf-8"))
        self.assertEqual(slothpulse.generate_digest("Git context", "gemma:latest"), "### Digest 🦥")
        request = self.opener.open.call_args[0][0]
        self.assertEqual(request.full_url, "http://localhost:11434/api/generate")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data), {
            "model": "gemma:latest", "prompt": "Git context", "stream": False,
        })
        self.assertEqual(self.build_opener.call_args[0][0].proxies, {})

    def test_connection_failure_gives_local_setup_instruction(self):
        self.opener.open.side_effect = urllib.error.URLError("Connection refused")
        with self.assertRaisesRegex(RuntimeError, "ollama run gemma"):
            slothpulse.generate_digest("context", "gemma:latest")

    def test_missing_model_gives_download_instruction(self):
        self.opener.open.side_effect = urllib.error.HTTPError(
            slothpulse.OLLAMA_URL, 404, "Not Found", {}, None
        )
        with self.assertRaisesRegex(RuntimeError, "ollama pull gemma:latest"):
            slothpulse.generate_digest("context", "gemma:latest")

    def test_server_failure_is_not_reported_as_a_connection_failure(self):
        self.opener.open.side_effect = urllib.error.HTTPError(
            slothpulse.OLLAMA_URL, 500, "Internal Server Error", {}, None
        )
        with self.assertRaisesRegex(RuntimeError, "HTTP 500"):
            slothpulse.generate_digest("context", "gemma:latest")

    def test_invalid_json_is_reported_cleanly(self):
        self.reply(b"not JSON")
        with self.assertRaisesRegex(RuntimeError, "unreadable response"):
            slothpulse.generate_digest("context", "gemma:latest")

    def test_empty_or_invalid_response_is_rejected(self):
        for body in [[], {}, {"response": " "}, {"response": 123}]:
            with self.subTest(body=body):
                self.reply(json.dumps(body).encode("utf-8"))
                with self.assertRaises(RuntimeError):
                    slothpulse.generate_digest("context", "gemma:latest")

    def test_backend_error_is_reported(self):
        self.reply(b'{"error":"model failed to load"}')
        with self.assertRaisesRegex(RuntimeError, "model failed to load"):
            slothpulse.generate_digest("context", "gemma:latest")


class DigestStorageTests(unittest.TestCase):
    def test_appends_timestamped_utf8_digest_without_overwriting_history(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = os.path.join(folder, ".slothpulse")
            with mock.patch("slothpulse.os.path.expanduser", return_value=destination):
                path = slothpulse.save_digest("First digest 🦥")
                slothpulse.save_digest("Second digest 🛠️")
            with open(path, encoding="utf-8") as saved:
                content = saved.read()
            self.assertEqual(content.count("\n---\n"), 2)
            self.assertEqual(content.count("## Digest: "), 2)
            self.assertIn("First digest 🦥", content)
            self.assertIn("Second digest 🛠️", content)


if __name__ == "__main__":
    unittest.main()
