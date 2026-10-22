---
title: "SlothPulse: I wrote the code. Gemma can draft the standup."
published: false
cover_image: https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/066m62f38lvloc1c8mxu.png
tags: devchallenge, hf26challenge, gemma, python
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## 💡 What I Built

After a day of writing code, “what did you do today?” shouldn’t require another Git archaeology session.

I built **SlothPulse** to turn recent commits and a terminal error into a standup draft using **Gemma running locally through Ollama**. One command produces three Markdown sections: completed work, blockers, and suggested next steps.

Every item has a receipt pointing back to its source, so you can check anything suspicious before sharing the draft. The note stays in a local file.

## 🎥 Demo

**[Open the recorded demo →](https://slothpulse.chicangel12.chatgpt.site)** — click a source badge to inspect its commit or error, or watch the 48-second video.

[![SlothPulse: your standup, with receipts](https://raw.githubusercontent.com/TengByte/slothpulse/main/demo-assets/poster.png)](https://slothpulse.chicangel12.chatgpt.site/#replay)

```bash
python3 slothpulse.py --since today --error-file error.txt
```

An excerpt from the [actual saved draft](https://github.com/TengByte/slothpulse/blob/main/demo-assets/digest.md):

```markdown
### 🛠️ What I Did Today
- Fixed issue where export job IDs were lost during retries. [^C1]

### 🐛 Blockers & Bugs
- User-reported: KeyError: 'result' while downloading job results. [^E1]

### 🚀 Next Steps
- Suggested: Investigate the origin of the KeyError and potential data access issues in worker.py. [^E1]
```

The full captured run summarizes five commits and one traceback in **10.33 seconds inside the CLI**. The fixture uses fictional authors and a deliberately fake key; the tiny worker really raises the captured error. The video replays timestamped output, including the measured wait.

## 💻 Code

{% github TengByte/slothpulse no-readme %}

[Setup and source](https://github.com/TengByte/slothpulse) · [Exact input and output](https://github.com/TengByte/slothpulse/blob/main/demo-assets/run.json) · [Build log](https://github.com/TengByte/slothpulse/blob/main/BUILD_LOG.md)

## 🛠️ How I Built It

The first version produced a tidy recap—and attributed a pasted error to SlothPulse itself, although its source was unspecified. That unsupported connection mattered more than the formatting.

I moved the model’s response to JSON with **required source keys**. Every commit gets a `C` key. Each reported error gets an `E` object containing both its summary and investigation step. Python assigns their references and renders the Markdown.

That pairing came from another real failure: an error investigation cited an unrelated commit. Both IDs existed, so checking whether a source was known had missed the problem. Keeping the error and its follow-up together removes that particular mismatch.

The CLI validates coverage and reference types, retries an invalid plan once, and saves no digest if the second attempt fails. A valid reference still cannot prove that a sentence is correct; human review stays in the workflow.

The application uses Python’s standard library: `subprocess` for Git, `urllib.request` for Ollama, and `json` for the response contract. No external Python packages. The code is MIT licensed.

## 🔒 Why Does Open Innovation Matter?

Commit subjects and traces can contain private project details. Downloaded Gemma weights let the recap run on the same machine as that context, without a hosted inference account or API key. The model download needs internet access; generation stays local.

SlothPulse checks model metadata before sending context, rejects cloud-backed models, and bypasses HTTP proxies. The tested Ollama server runs with `OLLAMA_NO_CLOUD=1`. These checks trust the local server and its metadata.

Before generating, `--preview` shows the sanitized input without a model call or file write. Common credential patterns are masked, but masking is best effort: preview it, and treat saved notes as potentially confidential.

## 🦥 The Lazy Payoff

The chore becomes **reviewing a draft instead of assembling one from scattered context**. The output is ordinary Markdown, ready to edit wherever I keep my notes.

I ran three synthetic scenarios three times each on an **Apple M5 / 16 GB** with local `gemma:latest`:

| Input | Median process time |
| --- | ---: |
| Five commits + one error | 7.668 s |
| Five commits only | 6.495 s |
| Error only | 3.926 s |

All nine final runs passed the structural and workflow checks; 23 unit tests cover failure boundaries. These are generation timings on a small synthetic batch, not a measurement of human time saved or factual accuracy. [Raw results and reproduction steps](https://github.com/TengByte/slothpulse/blob/main/BENCHMARK.md).

## 🏆 Prize Categories

* **Best Use of Gemma** — local Gemma drafts the summaries and investigation steps.

*Codex assisted with implementation, testing, demo preparation, and this article. More engineering notes: [tengli.dev](https://tengli.dev/).*
