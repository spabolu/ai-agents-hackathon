# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Purpose

This is a minimal starter repository for an AI task agent for the AI Agents Hackathon. It intentionally keeps only the essentials needed to install dependencies, configure the agent, and run it.

## Current Structure and Planned Architecture

- Python-based agent
- Key files (planned):
  - `requirements.txt` — Python dependencies
  - `config.yaml` — runtime configuration for the agent
  - `agent.py` — main entry point for the agent
  - `README.md` — the canonical source for setup and run instructions

## Initial Setup

Run commands from the repository root. Prefer `uv` if available; otherwise use `pip`.

**Using uv:**
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Using pip:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to set required values as described in README.md (for example, API keys or runtime parameters mentioned there).

## Run the Agent

After activating the virtual environment, from the repository root:
```bash
python agent.py
```

## Notes for WARP / Automation

- Keep changes minimal and aligned with the current structure; do not add new frameworks or restructure code
- When in doubt, defer to README.md as the source of truth for setup and run details
