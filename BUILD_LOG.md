# Build log: making a small local assistant easier to check

This is an edited engineering record, not a transcript export. Development and local measurement took place on October 21, 2026. Codex assisted with implementation, tests, demo preparation, and writing; Gemma performs the product's local inference.

## 1. A plausible paragraph was not enough

The first CLI sent recent Git history and an example `AttributeError` to Gemma, then appended the returned Markdown. An early run described the error as occurring while running the CLI even though its source was unspecified. The text looked plausible. The attribution was unsupported.

Decision: keep user-reported errors separate from commit evidence, preserve an explicit “cause unverified” label, and make every generated item reviewable against a source.

## 2. Schema syntax did not guarantee coverage

An intermediate structured response used arrays of `{text, evidence}` items. Local checks exposed missing blockers and incomplete commit coverage; one five-commit attempt still failed after its retry. A structurally valid JSON object could still leave out the work we supplied.

Decision: require one object property per known commit ID, and one per known error ID. Each required C key carries its summary. Each required E key carries both a summary and an investigation step. Python maps those keys into references rather than trusting model-written footnotes.

## 3. Error follow-ups needed the same source

A later valid-looking plan linked an error investigation to a commit. Both IDs existed, so a known-ID check alone was insufficient.

Decision: when errors are present, derive the next steps directly from each E object's `next_step`. Reject extra commit-based next steps in that case. When no error is supplied, allow at most two commit-linked suggestions.

## 4. “Local URL” needed a server-side boundary

Ollama can expose cloud-backed models through its local API. Calling localhost alone is not evidence that inference stayed local.

Decision: inspect model metadata before sending context, reject remote models or unverifiable metadata, bypass environment proxies, and run the tested server with `OLLAMA_NO_CLOUD=1`. This trusts the local server and does not claim to sandbox arbitrary processes.

## 5. Give the user a chance to see the input

Added `--preview`, optional time and author filters, trace files/stdin, common credential masking, and an optional JSON report. The preview makes no model request or file write. Masking is deliberately described as best effort; output files can still be confidential.

## 6. Make the demonstration reproducible

Added a synthetic repository with older activity, another author, a real generated traceback, and a fake key. The final batch contains nine real Gemma calls across three scenarios. All nine passed the documented structural/workflow checks. The committed cast preserves the captured timing; the MP4 adds explanatory cards around that replay.

## Remaining limits

Source coverage is not factual verification. One summary per commit can be repetitive; eight commits can miss part of a busy day. Commit subjects omit important context. A malicious or misleading source can still affect prose despite instructions to ignore embedded commands. The tool executes no model-proposed commands and requires human review before sharing.

Useful next work would be human evaluation on deliberately misleading commit subjects, clearer grouping without losing source coverage, and optional diff context with explicit preview. These are future work, not shipped features.
