# SlothPulse 🦥

SlothPulse is a 100% local, privacy-first CLI agent that turns recent Git activity and optional terminal errors into a daily developer digest with a local Gemma model. Your commits and error traces stay on your machine.

## Features

- **Zero Cloud:** Sends prompts only to your local Ollama instance.
- **Auto Git-Context:** Reads up to eight recent commits from your repository.
- **Markdown Output:** Saves a timestamped digest to `~/.slothpulse/digest.md`.

## Prerequisites

- Python 3.8+
- Git
- [Ollama](https://ollama.com/) with Gemma available locally

## Quick Start

Download and start Gemma with Ollama:

```bash
ollama run gemma
```

In another terminal, run SlothPulse from your Git repository:

```bash
python slothpulse.py -e "error text"
```

In a second terminal, run SlothPulse from a Git repository:

```bash
python slothpulse.py -e "AttributeError: 'NoneType' object has no attribute 'get'"
```

To choose another Ollama model or a repository explicitly:

```bash
python slothpulse.py --model gemma:latest --repo /path/to/repository
```

Each response is appended to `~/.slothpulse/digest.md` with a local timestamp. The script sends the prompt only to `http://localhost:11434`; it has no cloud service or third-party Python dependencies.

## Demo

The command above is the demo flow. Run it with Ollama and Gemma installed to generate a real digest; no generated sample is presented as model output.
