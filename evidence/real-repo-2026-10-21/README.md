# Real repository trial — October 21, 2026

This trial uses six real public commits from SlothPulse itself at `39ecac6807d5b31bc93b3716bfa080c28c0c3534`, rather than the synthetic export-worker fixture. Development of this project was AI assisted. This is an agent-assisted repository trial, not evidence of the owner preparing or delivering a real team standup.

## Reproduction

```bash
python3 slothpulse.py --repo /path/to/slothpulse \
  --since 2026-10-21T00:00:00-07:00 --author Teng \
  --output /tmp/slothpulse-real.md --report /tmp/slothpulse-real.json
```

The recorded input HEAD has six matching commits. Later commits will change that context; use a checkout of the recorded HEAD for comparable input. No error was supplied. Run with local downloaded `gemma:latest` and the setup in the main README. The original model was not loaded according to `ollama ps` before the first invocation; the repeat followed immediately. No explicit unload was used to create a controlled cold-start benchmark.

| Invocation | External process time | CLI time | Generation attempts |
| --- | ---: | ---: | ---: |
| Initially unloaded | 13.619 s | 13.54 s | 1 |
| Immediate repeat | 8.720 s | 8.62 s | 1 |

Environment: Apple M5 / 16 GB, Python 3.14.5, Ollama 0.40.8, model `a72c7f4d0a15`. Timing excludes installation/model download and any user review. This is two invocations of one input, not a representative latency study.

## Review found a semantic status error

Both invocations generated six completed-work summaries, no reported blockers, and no suggested follow-ups. Both passed the source/shape validator. In both outputs, C3 summarized “submission handoff” as “submitted,” although the DEV entry was still a draft.

An AI-assisted comparison of the six summaries to their sources identified one status claim requiring correction. This is **one item out of six completed-work items**; it is not a word-level edit percentage or a human edit-effort measurement. Source validation does not establish factual truth.

- `initially-unloaded.json`, `.md`, `.txt`: raw first-run report, saved digest, and stdout.
- `repeat.json`, `.md`, `.txt`: raw immediate-repeat artifacts.
- `preview.txt`: exact sanitized evidence preview before inference.
- `trial.json`: process timings and input HEAD.
- `review.json`: reviewer type, exact status correction, and unmeasured human metrics.
- `reviewed.md`: explicitly labeled derivative with that one correction. Raw outputs remain unchanged.

No manual-writing baseline, human review duration, team-chat use, time saved, performance-review benefit, or human edit percentage was measured. The tool does not automatically collect yesterday’s errors; relevant errors must be supplied. For morning standups choose the relevant prior workday window explicitly; `--since today` starts at the current day’s midnight and may miss yesterday’s work. The window is still capped at eight commits.
