# SlothPulse 🦥

**Your standup, with receipts.** A local, privacy-first Python CLI that turns Git activity and user-reported errors into a Gemma-written Markdown draft. Every item points back to supplied evidence. No external Python packages.

[DEV contest entry](https://dev.to/tengbyte/slothpulse-i-wrote-the-code-gemma-can-draft-the-standup-2bhp) · [Interactive recorded demo](https://slothpulse.chicangel12.chatgpt.site) · [Watch the 48-second demo](#demo) · [Captured draft](demo-assets/digest.md) · [Measurements](BENCHMARK.md) · [Build decisions](BUILD_LOG.md)

## Demo

Play the 48-second demo directly below, with English narration.

https://github.com/user-attachments/assets/5bdbd9c7-d788-4cda-9394-b79f1ff9f0cf

[Watch with English captions](https://tengli.dev/posts/slothpulse-source-bindings.html#demo) · [Explore the source receipts](https://slothpulse.chicangel12.chatgpt.site/#replay) · [Download MP4](https://raw.githubusercontent.com/TengByte/slothpulse/main/demo-assets/demo.mp4)

## Features

- **Local inference:** downloaded Gemma weights through Ollama at `localhost:11434`; remote model metadata is rejected before project context is sent. HTTP proxies are bypassed.
- **Auto Git context:** at most eight recent commits, with optional time and author filters. No source files or diffs are read.
- **Preview and masking:** inspect sanitized evidence without calling a model or writing a file. Common credential patterns are masked before inference.
- **Source references:** commit summaries stay attached to commit IDs; each reported error gets a blocker and suggested investigation. Unknown or missing sources fail validation.
- **Markdown output:** exactly three sections, deterministic rendering, timestamped append to `~/.slothpulse/digest.md` or your chosen file.

## Quick start

You need Python **3.8+**, Git, and [Ollama](https://ollama.com/download). The CLI itself uses only Python's standard library. The tested Gemma download is about **5 GB**; allow memory and disk space for the model.

Start Ollama with cloud features disabled. If another Ollama server is running, close it before starting this one:

```bash
OLLAMA_NO_CLOUD=1 ollama serve
```

In another terminal, download and try Gemma:

```bash
ollama run gemma
# When ready, type /bye to leave the model's interactive chat.
git clone https://github.com/TengByte/slothpulse.git
cd slothpulse
python3 slothpulse.py --repo /path/to/your/repo --since today --preview
python3 slothpulse.py --repo /path/to/your/repo --since today \
  -e "AttributeError: 'NoneType' object has no attribute 'get'"
```

If your Python 3 executable is named `python`, use `python slothpulse.py -e "error text"`.

SlothPulse allows 120 seconds per generation attempt and retries an invalid plan once. A rejected plan never reaches the digest file.

## Everyday use

```bash
# Git accepts author patterns; this is a filter, not identity verification.
python3 slothpulse.py -r /path/to/repo --since today --author "Your Name"

# Prefer a file or stdin for sensitive input so it does not become a literal
# argument in your shell history/process list.
python3 slothpulse.py --error-file error.txt --preview
cat error.txt | python3 slothpulse.py -e -

# Choose output paths and an optional inspectable JSON report.
python3 slothpulse.py --error-file error.txt \
  --output ./standup.md --report ./standup-report.json

# Gemma is the tested default; other downloaded local models can be selected.
python3 slothpulse.py --model gemma:latest
```

Without `--since`, context is the **latest eight commits**, which may span multiple days. The retained “What I Did Today” heading is accompanied by an explicit scope note. With `--since today`, Git uses local midnight and its usual commit-date semantics. Author dates shown in receipts can differ from Git's filtering date. Even a filtered window is capped at eight commits; this is a recap, not a complete activity audit.

Each draft has:

```markdown
### 🛠️ What I Did Today
- Fixed issue where export job IDs were lost during retries. [^C1]

### 🐛 Blockers & Bugs
- User-reported: KeyError: 'result' while downloading job results. [^E1]

### 🚀 Next Steps
- Suggested: Investigate the origin of the KeyError and potential data access issues in worker.py. [^E1]
```

Commit receipts contain the hash, author, date, and subject. Error receipts retain an error signature and label its cause unverified. `--report` includes the sanitized trace and full validated plan.

## Checks and limits

Gemma returns JSON keyed by required source IDs. Python checks source coverage, reference types, bounded text, and error follow-ups, then renders Markdown. A second invalid response fails with an actionable message and no digest append.

**A valid reference does not prove a sentence is true.** Commit subjects are incomplete evidence; a traceback rarely proves a root cause. Review the draft before sharing it. SlothPulse does not inspect diffs, run suggested commands, post to chat, or make project changes.

Masking covers common token, password, bearer, private-key, and credential-in-URL shapes. It is a best-effort convenience, not a comprehensive secret scanner. Preview first. Reports and digests can still contain confidential project information; keep them in an appropriate local location.

The CLI's HTTP calls are limited to the local Ollama server (`/api/show`, then `/api/generate`). The local server and its metadata must be trusted. Use `OLLAMA_NO_CLOUD=1` as an additional server-side control. Installation and model download need internet access. The public demo uses a synthetic repository and a deliberately fake key; it has no connection to your files or model.

## Reproduce the demo

```bash
python3 make_demo.py /tmp/slothpulse-example
python3 slothpulse.py --repo /tmp/slothpulse-example --since today \
  --author "Teng Demo" --error-file /tmp/slothpulse-example/error.txt --preview
python3 slothpulse.py --repo /tmp/slothpulse-example --since today \
  --author "Teng Demo" --error-file /tmp/slothpulse-example/error.txt \
  --output /tmp/slothpulse-example/digest.md --report /tmp/slothpulse-example/run.json
```

Use a new empty fixture directory. Fixture dates are generated relative to the day you run it. See [DEMO.md](DEMO.md) for recording provenance.

## Verification

```bash
python3 -m unittest -v             # no model required
python3 benchmark.py --runs 3     # nine real Gemma runs; updates demo-assets/
```

The recorded final benchmark passed **9/9 structural and workflow checks**. Median process times: **7.668 s** for commits plus an error, **6.495 s** for commits only, **3.926 s** for an error only, on Apple M5 / 16 GB. These are small synthetic measurements, not a semantic accuracy score or a time-saved study. Full method and raw data: [BENCHMARK.md](BENCHMARK.md).

GitHub Actions runs the standard-library suite on Python 3.8 and 3.14. The suite covers failed inference, unknown references, remote models, masking, preview behavior, and output boundaries.

## Troubleshooting

| Message | Action |
| --- | --- |
| Could not inspect/connect to Ollama | Start the local server, then run `ollama run gemma`. |
| Model not found | Run `ollama pull gemma:latest`, or pull the name passed to `--model`. |
| Cannot verify local metadata / cloud models disabled | Choose downloaded local weights and a supported Ollama server. |
| No evidence available | Check the repository, time/author filters, or provide an error. |
| Model output failed evidence checks | No digest was saved. Try shorter relevant input or review model compatibility. |

## Open source

Built for [Hacktoberfest 2026 Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19), targeting **Best Use of Gemma**. Code is [MIT licensed](LICENSE); Gemma and Ollama retain their own licenses and terms. Contributions that demonstrate a failure with a small synthetic fixture are especially welcome.
