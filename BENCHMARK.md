# Measurements, method, and limits

Captured October 21, 2026. Raw records: [benchmark.json](demo-assets/benchmark.json). Full first-run evidence and plan: [run.json](demo-assets/run.json).

## Environment

- Apple M5, 16 GB RAM; macOS arm64
- Python 3.14.5; Ollama 0.40.8
- Downloaded `gemma:latest`, model ID `a72c7f4d0a15`, approximately 5.0 GB
- Ollama reported 100% GPU execution; server started with `OLLAMA_NO_CLOUD=1`
- Generation options: temperature 0, seed 42, context 8192, maximum predicted tokens 1800

## Final results

| Scenario | Run 1 | Run 2 | Run 3 | Median | Checks |
| --- | ---: | ---: | ---: | ---: | --- |
| Five commits + one error | 10.396 s | 7.668 s | 7.583 s | 7.668 s | 3/3 |
| Five commits only | 7.243 s | 6.495 s | 6.310 s | 6.495 s | 3/3 |
| One error, no repository | 5.175 s | 3.871 s | 3.926 s | 3.926 s | 3/3 |

All nine final runs exited successfully on their first generation attempt. The 10.33 s printed inside the captured CLI differs from the 10.396 s external process measurement: the latter includes process startup and output completion. Neither includes installing Ollama or downloading weights.

The model was already available locally. This is an ordered batch, not a controlled cold-start benchmark. Model residency, prompt caching, thermal state, and other work affect results. Three repetitions per synthetic scenario are insufficient for broad performance claims.

## Inputs and checks

`make_demo.py` creates nine synthetic commits: five selected by today's window and the fictional author “Teng Demo,” an additional author's commit, and older activity. It also executes a tiny worker to capture a real Python `KeyError: 'result'`, then adds a deliberately fake credential-shaped value. The fixture contains no customer or employer data.

`benchmark.py` runs the actual CLI in subprocesses against local Gemma. It checks exit code, the three exact headings, expected scope, known source IDs, absence of the fake credential, and saved Markdown. The CLI separately validates complete source coverage and error-linked follow-ups. These checks establish structural and workflow behavior; they do **not** score semantic truth, usefulness, or root-cause accuracy.

The first final run produced the committed [digest](demo-assets/digest.md), [JSON report](demo-assets/run.json), [terminal transcript](demo-assets/transcript.txt), and [timestamped terminal cast](demo-assets/session.cast).

## Failures during development

These final results follow earlier failed experiments; they do not mean the first implementation worked reliably. Free-text output over-attributed an unspecified error. A later array-shaped JSON plan omitted required source coverage and failed even after its retry. Changing to an object with required source keys made omissions detectable at the generation contract. We also attached each error's summary and follow-up to the same key after observing an error investigation attached to an unrelated commit. See [BUILD_LOG.md](BUILD_LOG.md).

## Reproduce

```bash
OLLAMA_NO_CLOUD=1 ollama serve
# In another terminal, after downloading Gemma:
python3 -m unittest -v
python3 benchmark.py --runs 3
```

The benchmark replaces the generated assets in `demo-assets/`; keep a copy if you want to preserve an earlier result. A different date changes fixture hashes. A model tag can change upstream, so record your own model ID and runtime version. The MP4 and poster are presentation artifacts and are not rebuilt by the benchmark.

## Compatibility

The local unit suite has 23 tests and does not need Ollama. Python sources are parsed against Python 3.8 syntax locally; GitHub Actions additionally exercises real Python 3.8 and 3.14 interpreters. Local inference timings were measured only with Python 3.14.5 and the Gemma version above.

There is no measured human baseline. We make no claim that the tool saves 15 minutes, eliminates review, or achieves 100% factual accuracy.
