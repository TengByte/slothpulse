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

Install [Ollama](https://ollama.com/download) first. On macOS you can use `brew install ollama`. If the Ollama desktop app is not running, start the local server in a terminal and leave it open:

```bash
ollama serve
```

In another terminal, download and start the default Gemma model (about 5 GB):

```bash
ollama run gemma
```

Once the model is ready, type `/bye` to leave its interactive chat. Clone SlothPulse:

```bash
git clone https://github.com/TengByte/slothpulse.git
cd slothpulse
```

Generate a digest from the repository's recent activity and an optional error:

```bash
python3 slothpulse.py -e "AttributeError: 'NoneType' object has no attribute 'get'"
```

On systems where Python 3 is named `python`, the equivalent is `python slothpulse.py -e "error text"`.

To choose another Ollama model or a repository explicitly:

```bash
python3 slothpulse.py --model gemma:latest --repo /path/to/repository
```

Each response is appended to `~/.slothpulse/digest.md` with a local timestamp. The script sends the prompt only to `http://localhost:11434`, bypassing HTTP proxies. It has no cloud service or third-party Python dependencies. The initial Ollama/model installation needs internet access; inference uses the downloaded local model.

## Troubleshooting

- **Connection refused:** Start Ollama with `ollama serve` or open the desktop app.
- **Model not found:** Run `ollama pull gemma:latest` (or pull the model you passed to `--model`).
- **Git history unavailable:** Pass a Git repository to `--repo`. SlothPulse can still summarize the supplied error without Git history.
- **Slow first run:** Model loading and inference depend on your hardware; SlothPulse waits up to 120 seconds for a response.

## Checks

Run the standard-library tests without downloading a model:

```bash
python3 -m unittest -v
```

## Demo

See [captured Gemma output and local verification results](DEMO.md). On an Apple M5 with 16 GB RAM, the measured invocation with the example error completed in 5.87 seconds after unloading the model; two further scenarios completed in 3.08 and 4.24 seconds. Each generated exactly three sections and appended the digest successfully. Your timings will depend on hardware, model loading, and input length.
