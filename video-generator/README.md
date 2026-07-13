# Autonomous Video Generator (RunComfy Model API)

One command in, finished video out. The pipeline:

1. **Plan** — Claude turns your topic into a title and per-scene cinematic
   text-to-video prompts (or you supply a plan file and skip the LLM).
2. **Generate** — each scene is submitted to a video model on the
   [RunComfy Model API](https://www.runcomfy.com/models) (`model-api.runcomfy.net`),
   polled with backoff, and downloaded. Scenes run concurrently with retries.
3. **Assemble** — ffmpeg normalizes the clips to a common resolution/fps and
   concatenates them into `final.mp4`.

Every run writes a `manifest.json`; if anything fails mid-run you resume with
`--resume RUN_ID` and only the incomplete scenes are regenerated — clips you
already paid for are never redone.

## Setup

```bash
cd video-generator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# ffmpeg is a system dependency: apt install ffmpeg / brew install ffmpeg

cp .env.example .env   # then fill in your tokens
```

- `RUNCOMFY_API_TOKEN` — from your RunComfy profile page (click your avatar,
  upper right, at runcomfy.com).
- `ANTHROPIC_API_KEY` — for the Claude planning step. Optional if you always
  use `--plan-file`.

## Usage

```bash
# Fully autonomous: plan + generate + stitch
python -m videogen "deep sea creatures at night"

# Let Claude invent the topic too
python -m videogen --auto-topic

# Skip the LLM: bring your own plan
python -m videogen --plan-file my-plan.json

# Pick a model, scene count, and pass model-specific params
python -m videogen "retro arcade" --model seedance-lite --scenes 6 --param aspect_ratio=16:9

# Resume a failed run (finished clips are kept)
python -m videogen --resume 20260713-181500-a1b2c3

# Test the whole pipeline with zero credits (local placeholder clips)
python -m videogen --dry-run --plan-file tests/fixtures/plan.json
```

Output lands in `outputs/<run-id>/final.mp4`, with per-scene clips and the
manifest alongside.

A plan file looks like:

```json
{
  "title": "My video",
  "scenes": [
    {"prompt": "A wide aerial shot of ... cinematic, golden hour", "duration": 5},
    {"prompt": "Close-up of ... same visual style, shallow depth of field", "duration": 5}
  ]
}
```

## Models & cost

`--model` accepts a registry name (`wan` — the budget default, `seedance-lite`,
`seedance-pro`, `kling`, `veo`) or any raw `vendor/model/endpoint` route from a
RunComfy model API page. Cost per 5s clip varies roughly 10x between budget
(Wan/Seedance Lite — cents) and premium (Kling/Veo) models.

Spend guards:

- `--max-clips` (default 8) aborts before generation if the plan is bigger.
- `--dry-run` exercises everything locally for free.

> **Before your first paid run:** the registry routes ship unverified — model
> slugs and parameter names occasionally change on RunComfy's side. Open your
> chosen model's API page (e.g. `runcomfy.com/models/<vendor>/<model>/api`),
> confirm the route in the curl example matches, and pass differences via
> `--model <route>` and `--param key=value`. A 404 on submit means the route
> is wrong, not that the pipeline is broken.

## First-real-run checklist

1. `python -m videogen --dry-run --plan-file tests/fixtures/plan.json` — verify
   ffmpeg assembly works on your machine.
2. Confirm the model route on its RunComfy API page (see above).
3. Start small: `python -m videogen "test shot of ocean waves" --scenes 1`.
4. Check `outputs/<run-id>/manifest.json` if anything fails — it records the
   request IDs and errors, and `--resume` picks up where it left off.

## Development

```bash
pytest            # unit tests + a dry-run end-to-end test (needs ffmpeg)
```

Layout: `videogen/config.py` (registry, defaults) · `planner.py` (Claude scene
planning) · `runcomfy.py` (Model API client + dry-run mock) · `pipeline.py`
(orchestration, manifest, resume) · `assembler.py` (ffmpeg) · `cli.py`.
