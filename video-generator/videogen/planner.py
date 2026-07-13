"""Turn a topic into a scene plan with an LLM (or load one from disk).

Story/scene planning uses an OpenAI-compatible chat-completions provider —
DeepSeek (default) or MiniMax. Claude remains available via --planner claude.
"""

import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field

import requests

log = logging.getLogger("videogen.planner")


@dataclass
class PlannerProvider:
    """An OpenAI-compatible chat-completions endpoint."""

    url: str
    default_model: str
    key_env: str
    # DeepSeek supports response_format json_object; MiniMax's M-series models
    # emit clean JSON when asked but reject the parameter, so it's opt-in.
    json_mode: bool = False
    extra_body: dict = field(default_factory=dict)


PLANNER_PROVIDERS: dict[str, PlannerProvider] = {
    "deepseek": PlannerProvider(
        url="https://api.deepseek.com/chat/completions",
        default_model="deepseek-chat",
        key_env="DEEPSEEK_API_KEY",
        json_mode=True,
    ),
    "minimax": PlannerProvider(
        url="https://api.minimax.io/v1/chat/completions",
        default_model="MiniMax-M2",
        key_env="MINIMAX_API_KEY",
    ),
}

DEFAULT_PLANNER = "deepseek"
CLAUDE_MODEL = "claude-opus-4-8"

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Self-contained cinematic text-to-video prompt for this scene",
                    },
                    "duration": {"type": "integer", "description": "Clip length in seconds (4-10)"},
                },
                "required": ["prompt", "duration"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "scenes"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """\
You are a video director planning a short-form video that will be generated \
scene by scene with a text-to-video AI model. Each scene becomes an \
independent clip, so every scene prompt must stand fully on its own: restate \
the subject, setting, lighting, camera movement, and visual style in every \
prompt — never refer to a previous scene. Keep a consistent visual style \
across all scenes so the stitched video feels coherent. Write concrete, \
visual prompts (what the camera sees), not abstract narration.

Respond with a single JSON object and nothing else, in this exact shape:
{"title": "...", "scenes": [{"prompt": "...", "duration": 5}, ...]}"""


@dataclass
class Scene:
    prompt: str
    duration: int


@dataclass
class Plan:
    title: str
    scenes: list[Scene]

    def to_dict(self) -> dict:
        return asdict(self)


def plan_from_dict(data: dict) -> Plan:
    try:
        scenes = [Scene(prompt=s["prompt"], duration=int(s.get("duration", 5))) for s in data["scenes"]]
        title = str(data["title"])
    except (KeyError, TypeError) as exc:
        raise ValueError(f"invalid plan: expected {{title, scenes:[{{prompt, duration}}]}} — {exc}") from exc
    if not scenes:
        raise ValueError("invalid plan: scenes list is empty")
    for scene in scenes:
        if not scene.prompt.strip():
            raise ValueError("invalid plan: a scene has an empty prompt")
    return Plan(title=title, scenes=scenes)


def load_plan_file(path: str) -> Plan:
    with open(path, encoding="utf-8") as fh:
        return plan_from_dict(json.load(fh))


def extract_json_object(text: str) -> dict:
    """Parse a JSON object out of an LLM reply, tolerating code fences/prose."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ValueError(f"no JSON object in planner reply: {text[:200]!r}")
        text = text[start : end + 1]
    return json.loads(text)


def _build_user_prompt(topic: str | None, num_scenes: int, clip_seconds: int) -> str:
    if topic:
        ask = f"Plan a short video about: {topic}"
    else:
        ask = "Invent a visually striking topic for a short video, then plan it."
    return (
        f"{ask}\n\nProduce exactly {num_scenes} scenes. Each scene's duration "
        f"should be {clip_seconds} seconds unless a scene clearly needs slightly "
        "more or less (stay within 4-10 seconds). Reply with the JSON object only."
    )


def _generate_openai_compatible(
    provider: PlannerProvider, model: str, topic: str | None, num_scenes: int, clip_seconds: int
) -> Plan:
    api_key = os.environ.get(provider.key_env)
    if not api_key:
        raise RuntimeError(f"{provider.key_env} is not set (required for this planner)")

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(topic, num_scenes, clip_seconds)},
        ],
        "max_tokens": 4096,
        **provider.extra_body,
    }
    if provider.json_mode:
        body["response_format"] = {"type": "json_object"}

    resp = requests.post(
        provider.url,
        json=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=180,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"planner request failed ({resp.status_code}): {resp.text[:500]}")
    data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"unexpected planner response shape: {json.dumps(data)[:500]}") from exc
    return plan_from_dict(extract_json_object(text))


def _generate_claude(model: str, topic: str | None, num_scenes: int, clip_seconds: int) -> Plan:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(topic, num_scenes, clip_seconds)}],
        output_config={"format": {"type": "json_schema", "schema": PLAN_SCHEMA}},
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to plan this topic; try a different one")
    text = next(b.text for b in response.content if b.type == "text")
    return plan_from_dict(json.loads(text))


def generate_plan(
    topic: str | None,
    num_scenes: int,
    clip_seconds: int,
    provider_name: str = DEFAULT_PLANNER,
    model: str | None = None,
) -> Plan:
    """Ask the configured LLM for a scene plan. topic=None invents one."""
    if provider_name == "claude":
        plan = _generate_claude(model or CLAUDE_MODEL, topic, num_scenes, clip_seconds)
    elif provider_name in PLANNER_PROVIDERS:
        provider = PLANNER_PROVIDERS[provider_name]
        plan = _generate_openai_compatible(
            provider, model or provider.default_model, topic, num_scenes, clip_seconds
        )
    else:
        raise ValueError(
            f"unknown planner '{provider_name}'; use one of {sorted(PLANNER_PROVIDERS) + ['claude']}"
        )
    plan.scenes = plan.scenes[:num_scenes]
    log.info("planned '%s' with %d scenes via %s", plan.title, len(plan.scenes), provider_name)
    return plan
