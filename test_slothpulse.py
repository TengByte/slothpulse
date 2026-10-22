"""Boundary checks for Git input, Ollama responses, and digest persistence."""

import argparse
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


def sample_evidence():
    return {"commits": [{"id": "C1", "hash": "a1b2c3d", "author": "Demo", "date": "2026-10-21", "subject": "Handle empty jobs"}],
            "errors": [{"id": "E1", "source": "--error", "text": "KeyError: result"}],
            "scope": "today", "redactions": 0, "warning": None}


def sample_plan():
    return {"completed": [{"text": "Handle empty jobs.", "evidence": ["C1"]}],
            "blockers": [{"text": "KeyError: result", "evidence": ["E1"]}],
            "next_steps": [{"text": "Inspect the missing result field.", "evidence": ["E1"]}]}


class EvidenceTests(unittest.TestCase):
    def test_source_keyed_response_binds_each_error_to_its_followup(self):
        raw = {"completed": {"C1": "Handle empty jobs."}, "blockers": {"E1": {"summary": "KeyError: result", "next_step": "Inspect the job's result field."}}, "next_steps": []}
        plan = slothpulse.normalize_plan(raw, sample_evidence())
        self.assertEqual(plan["completed"][0]["evidence"], ["C1"])
        self.assertEqual(plan["next_steps"][0]["evidence"], ["E1"])
        raw["completed"]["C99"] = "Unknown work"
        with self.assertRaises(ValueError):
            slothpulse.normalize_plan(raw, sample_evidence())

    def test_error_followup_cannot_be_attached_to_an_unrelated_commit(self):
        raw = {"completed": {"C1": "Handle empty jobs."}, "blockers": {"E1": {"summary": "KeyError: result", "next_step": "Inspect the result field."}}, "next_steps": [{"text": "Fix the reported error", "evidence": ["C1"]}]}
        with self.assertRaises(ValueError):
            slothpulse.normalize_plan(raw, sample_evidence())

    def test_unknown_source_and_wrong_kind_are_rejected(self):
        for section, reference in [("completed", "C99"), ("completed", "E1"), ("blockers", "C1")]:
            plan = sample_plan()
            plan[section][0]["evidence"] = [reference]
            with self.subTest(section=section, reference=reference):
                with self.assertRaises(ValueError):
                    slothpulse.validate_plan(plan, sample_evidence())

    def test_missing_commit_blocker_or_error_followup_is_rejected(self):
        for section in ("completed", "blockers", "next_steps"):
            plan = sample_plan()
            plan[section] = []
            with self.subTest(section=section):
                with self.assertRaises(ValueError):
                    slothpulse.validate_plan(plan, sample_evidence())

    def test_common_credentials_are_masked_before_context_is_created(self):
        raw = "API_KEY=demo_fake_value_123456\nAuthorization: Bearer demo_bearer_1234567890\n" + "ghp_" + "DEMO" * 10
        with tempfile.TemporaryDirectory() as folder:
            evidence = slothpulse.collect_evidence(folder, [("demo", raw)])
        serialized = json.dumps(evidence)
        for value in ("demo_fake_value_123456", "demo_bearer_1234567890", "DEMO" * 10):
            self.assertNotIn(value, serialized)
        self.assertGreaterEqual(evidence["redactions"], 3)

    def test_private_key_block_is_masked(self):
        value, count = slothpulse.redact("-----BEGIN PRIVATE KEY-----\ndemo_fake_key\n-----END PRIVATE KEY-----")
        self.assertEqual(value, "[REDACTED]")
        self.assertEqual(count, 1)

    def test_rendered_model_text_cannot_add_headings_or_external_links(self):
        plan = sample_plan()
        plan["completed"][0]["text"] = "## Surprise\n[remote](https://example.invalid)"
        digest = slothpulse.render_digest(plan, sample_evidence())
        self.assertEqual([line for line in digest.splitlines() if line.startswith("#")], slothpulse.HEADINGS)
        self.assertIn("[^C1]: Commit `a1b2c3d`", digest)
        self.assertNotIn("[remote](", digest)

    def test_preview_calls_no_model_and_writes_no_digest(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = os.path.join(folder, "digest.md")
            with mock.patch("slothpulse.urllib.request.build_opener") as transport, mock.patch("sys.stdout", new_callable=io.StringIO) as stdout, mock.patch("sys.stderr", new_callable=io.StringIO):
                status = slothpulse.main(["--repo", folder, "--preview", "-e", "API_KEY=demo_fake_value_123456", "--output", destination])
            self.assertEqual(status, 0)
            transport.assert_not_called()
            self.assertFalse(os.path.exists(destination))
            self.assertNotIn("demo_fake_value_123456", stdout.getvalue())

    def test_cloud_model_metadata_is_rejected_before_prompt_transmission(self):
        info = {"model_info": {"family": "remote"}, "remote_host": "https://example.invalid", "remote_model": "remote"}
        with mock.patch("slothpulse.urllib.request.build_opener") as build:
            build.return_value.open.return_value = io.BytesIO(json.dumps(info).encode())
            with self.assertRaisesRegex(RuntimeError, "Cloud models are disabled"):
                slothpulse.generate_plan(sample_evidence(), "remote:cloud")
            self.assertEqual(build.return_value.open.call_count, 1)
            request = build.return_value.open.call_args[0][0]
            self.assertTrue(request.full_url.endswith("/api/show"))
            self.assertEqual(json.loads(request.data), {"model": "remote:cloud"})

    def test_invalid_model_plan_is_retried_once_then_rejected(self):
        plan = sample_plan()
        plan["blockers"] = []
        with mock.patch("slothpulse.assert_local_model"), mock.patch("slothpulse.generate_digest", return_value=json.dumps(plan)) as generate, mock.patch("sys.stderr", new_callable=io.StringIO):
            with self.assertRaisesRegex(RuntimeError, "No digest was saved"):
                slothpulse.generate_plan(sample_evidence(), "gemma:latest")
            self.assertEqual(generate.call_count, 2)

    def test_invalid_plan_does_not_create_output_files(self):
        with tempfile.TemporaryDirectory() as folder:
            output, report = os.path.join(folder, "digest.md"), os.path.join(folder, "report.json")
            with mock.patch("slothpulse.collect_evidence", return_value=sample_evidence()), mock.patch("slothpulse.generate_plan", side_effect=RuntimeError("Invalid evidence")), mock.patch("sys.stdout", new_callable=io.StringIO), mock.patch("sys.stderr", new_callable=io.StringIO):
                status = slothpulse.main(["--output", output, "--report", report])
            self.assertEqual(status, 1)
            self.assertFalse(os.path.exists(output))
            self.assertFalse(os.path.exists(report))

    def test_error_file_and_stdin_preserve_multiline_input(self):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as trace:
            trace.write("Traceback:\nKeyError: result\n")
            trace.flush()
            args = argparse.Namespace(error="-", error_file=trace.name)
            with mock.patch("sys.stdin", io.StringIO("ValueError: demo\n")):
                errors = slothpulse.read_errors(args)
        self.assertEqual(len(errors), 2)
        self.assertIn("\nKeyError", errors[1][1])

    def test_output_and_report_paths_must_differ(self):
        with mock.patch("sys.stderr", new_callable=io.StringIO), mock.patch("slothpulse.collect_evidence") as collect:
            self.assertEqual(slothpulse.main(["--output", "same.md", "--report", "same.md"]), 1)
            collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
