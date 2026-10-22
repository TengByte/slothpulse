# Local verification and real Gemma output

Captured on October 21, 2026 from real local CLI invocations.

- Hardware: Apple M5, 16 GB RAM
- Runtime: Python 3.14.5; Ollama 0.40.8
- Model: `gemma:latest`, ID `a72c7f4d0a15`, 5.0 GB download
- Inference: Ollama reported 100% GPU execution
- Input repository: this repository at `fcf3bec`
- Output file: `~/.slothpulse/digest.md`

| Scenario | Elapsed | Result |
| --- | ---: | --- |
| repository with error | 5.87 s | Passed |
| repository without error | 3.08 s | Passed |
| non repository with error | 4.24 s | Passed |

The model was unloaded with `ollama stop gemma:latest` before the first measured invocation. These are individual measurements, not a performance guarantee. Installation and model download time are excluded.

Each successful invocation exited with code 0, produced exactly the three required Markdown headings, and appended its response with a timestamp to the digest file. The no-error case reported no blockers. The non-repository case reported no evidence of completed work rather than inventing commits.

A real request for a missing model exited with code 1, displayed an `ollama pull` instruction, and left the digest unchanged. Before installing Ollama, a real CLI invocation also exited cleanly with a connection-refused setup message.

## Captured input

```bash
python3 slothpulse.py -e "AttributeError: 'NoneType' object has no attribute 'get'"
```

## Captured model response

```markdown
### 🛠️ What I Did Today
Completed development of the SlothPulse local developer digest CLI.


### 🐛 Blockers & Bugs
A user-reported error occurred: `AttributeError: 'NoneType' object has no attribute 'get'`.


### 🚀 Next Steps
Investigate the `AttributeError` and determine its cause.
```

## Automated boundary checks

`python3 -m unittest -v`: 10 tests passed. These cover reading the latest eight commits, a non-repository path, the local JSON API contract, proxy bypass, connection failures, missing models, server errors, malformed/empty responses, and timestamped UTF-8 append behavior.

The automated API checks use simulated responses; the three measured scenarios above use the downloaded Gemma model. Full execution was checked on Python 3.14.5. Both Python source files also passed a Python 3.8 syntax compatibility check; an actual Python 3.8 runtime was not exercised.
