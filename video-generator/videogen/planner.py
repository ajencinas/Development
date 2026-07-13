"""Turn a topic into a scene plan via the Claude API (or load one from disk)."""

import json
import logging
from dataclasses import asdict, dataclass

log = logging.getLogger("videogen.planner")

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
visual prompts (what the camera sees), not abstract narration."""


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


def generate_plan(topic: str | None, num_scenes: int, clip_seconds: int) -> Plan:
    """Ask Claude for a scene plan. topic=None lets Claude invent one."""
    import anthropic

    client = anthropic.Anthropic()
    if topic:
        ask = f"Plan a short video about: {topic}"
    else:
        ask = "Invent a visually striking topic for a short video, then plan it."
    user = (
        f"{ask}\n\nProduce exactly {num_scenes} scenes. Each scene's duration "
        f"should be {clip_seconds} seconds unless a scene clearly needs slightly "
        "more or less (stay within 4-10 seconds)."
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": PLAN_SCHEMA}},
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to plan this topic; try a different one")
    text = next(b.text for b in response.content if b.type == "text")
    plan = plan_from_dict(json.loads(text))
    plan.scenes = plan.scenes[:num_scenes]
    log.info("planned '%s' with %d scenes", plan.title, len(plan.scenes))
    return plan
