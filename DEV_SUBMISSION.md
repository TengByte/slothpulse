---
title: How I Built a 100% Local Dev Digest Agent with Gemma to Stop Reading My Own Git Logs
published: false
tags: devchallenge, hf26challenge, gemma, python
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## 💡 What I Built
I hate pausing at the end of a busy week to reconstruct what I did from memory and reread my own Git logs. SlothPulse is a 100% local CLI agent for developers who would rather get back to building. It gives Gemma recent Git commits and optional terminal errors, then turns them into a clean Markdown summary with blockers and next steps.

## 🎥 Demo
*(Add a screen recording or GIF of a real run here before publishing.)*
`python slothpulse.py -e "AttributeError: 'NoneType' object has no attribute 'get'"`

## 💻 Code
{% github TengByte/slothpulse %}

## 🛠️ How I Built It
SlothPulse uses Python's standard library: `subprocess` reads Git history, `urllib.request` calls the local Ollama API, and Gemma writes the digest. There are zero external Python dependencies.

## 🔒 Why Does Open Innovation Matter?
Code commits and internal errors can contain confidential project details, infrastructure clues, and other information that should stay inside a team. Uploading that context to a cloud LLM creates a security risk and puts data sovereignty in someone else's hands. Open-weight models like Gemma let developers run this workflow locally, so automation can help with daily notes while the source material stays on the developer's machine.

## 🦥 The Lazy Payoff
Instead of spending 15 minutes piecing together standup notes, I can run one script and get a useful first draft in seconds. SlothPulse does the repetitive recap, leaving me with more time to focus on the work.

## 🏆 Prize Categories
* **Best Use of Gemma**
