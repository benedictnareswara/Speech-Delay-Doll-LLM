# Contributing

Thanks for your interest in SpeechLLM! This guide covers how to set up the project for development and how to contribute changes.

## Development setup

### Prerequisites

- Python 3.10 or newer
- An Orange Pi Zero 3 is **not** required — the core routing logic runs on any machine

### Clone and install

```bash
git clone https://github.com/benedictnareswara/Speech-Delay-Doll-LLM.git
cd Speech-Delay-Doll-LLM
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e packages/speechllm-core
pip install pytest ruff
```

Install the device package only if you're working on Orange Pi–specific code:

```bash
pip install -e packages/speechllm-device
```

### Run the tests

```bash
pytest tests/ -q
```

Hardware-dependent tests are marked and skipped by default:

```bash
pytest tests/ -q -m "not hardware"   # skip hardware tests (default)
pytest tests/ -q -m hardware         # run only hardware tests (on the device)
```

### Lint

```bash
ruff check .
ruff format --check .
```

## Project structure

```
packages/speechllm-core/     Pure logic: detection, routing, phrase bank (zero dependencies)
packages/speechllm-device/   Orange Pi application: capture, VAD, STT, pipeline, hardware
tools/                       Build-time utilities: render_bank, verify_bank, bench_device
deploy/orangepi/             Installer, diagnostics, systemd unit, wiring reference
assets/bank/manifest.json    Index of what's on the DFPlayer SD card
tests/                       All tests (unit + integration)
```

`speechllm-core` has **no third-party dependencies** — keep it that way. This is a deliberate constraint: the device may not have a compiler, and this package must build everywhere.

## Making changes

### Adding a new phoneme

Three files must be updated together, or the new phoneme silently falls through to the generic noise pool:

1. `PHONEME_MAP` in `packages/speechllm-core/src/speechllm_core/detection/phonemes.py`
2. `INTENT_REGISTRY` in `packages/speechllm-core/src/speechllm_core/routing/intents.py`
3. `TEMPLATES` in `packages/speechllm-core/src/speechllm_core/routing/templates.py`

After changing these, re-render and re-burn the DFPlayer SD card:

```bash
python tools/render_bank.py
python tools/verify_bank.py
```

`tests/test_bank.py` enforces that all three tables stay in sync.

### Editing a therapy phrase

Modify the template text in `routing/templates.py`, then re-render only the changed phrase:

```bash
python tools/render_bank.py          # only changed phrases are re-synthesized
python tools/verify_bank.py
```

Every response must be **≤10 words**. The test suite enforces this across the entire template table.

### Code conventions

- Line length: 100 characters (configured in `pyproject.toml`)
- Use type hints for function signatures
- Keep `speechllm-core` dependency-free
- All therapy phrases are in Indonesian
- Run `ruff check .` and `pytest tests/ -q` before committing

## Submitting changes

1. Fork the repository
2. Create a branch from `main`
3. Make your changes and add tests if applicable
4. Run `pytest tests/ -q` and `ruff check .`
5. Open a pull request with a clear description of what changed and why

## Reporting issues

Open a GitHub issue. For hardware problems, include:

- Output of `sudo ./deploy/orangepi/doctor.sh`
- Board model and kernel version (`uname -a`)
- Serial port configuration (`ls /dev/ttyS* /dev/ttyUSB*`)
