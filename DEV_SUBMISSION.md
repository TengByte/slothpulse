---
title: How I Built a 100% Local Dev Digest Agent with Gemma to Stop Reading My Own Git Logs
published: false
tags: devchallenge, hf26challenge, gemma, python
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## 💡 What I Built
I hate pausing at the end of a busy week to reconstruct what I did from memory and reread my own Git logs. SlothPulse is a 100% local CLI agent for developers who would rather get back to building. It gives Gemma recent Git commits and optional terminal errors, then turns them into a clean Markdown summary with blockers and next steps.

## 🎥 Demo
I ran the CLI locally with `gemma:latest` on an Apple M5 with 16 GB RAM. After unloading the model, the example invocation completed in 5.87 seconds, returned the three requested sections, and appended the response to `~/.slothpulse/digest.md`.

[See the captured response and verification results](https://github.com/TengByte/slothpulse/blob/main/DEMO.md).

`python3 slothpulse.py -e "AttributeError: 'NoneType' object has no attribute 'get'"`

*(Add a screen recording of this real workflow before publishing the contest entry.)*

## 💻 Code
{% github TengByte/slothpulse %}

## 🛠️ How I Built It
SlothPulse uses Python's standard library: `subprocess` reads Git history, `urllib.request` calls the local Ollama API, and Gemma writes the digest. There are zero external Python dependencies. Local checks cover both the normal workflow and failure cases. Testing caught a misleading missing-model message and a prompt that incorrectly attributed a user-supplied error to the CLI; both were corrected before the recorded results above.

## 🔒 Why Does Open Innovation Matter?
Code commits and internal errors can contain confidential project details, infrastructure clues, and other information that should stay inside a team. Uploading that context to a cloud LLM creates a security risk and puts data sovereignty in someone else's hands. Open-weight models like Gemma let developers run this workflow locally, so automation can help with daily notes while the source material stays on the developer's machine.

## 🦥 The Lazy Payoff
The chore I want to remove is piecing together standup notes from Git history and scattered terminal errors. SlothPulse turns those inputs into a first draft with one command. Three local scenarios took 3.08–5.87 seconds on my machine; that measures generation time, not a formal study of time saved. I still review the draft, but the repetitive recap is already written.

## 🏆 Prize Categories
* **Best Use of Gemma**
