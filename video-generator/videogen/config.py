"""Configuration: environment, defaults, and the video-model registry."""

import os
from dataclasses import dataclass, field

MODEL_API_BASE = "https://model-api.runcomfy.net"

DEFAULT_SCENES = 4
DEFAULT_MAX_CLIPS = 8
DEFAULT_CONCURRENCY = 2
DEFAULT_CLIP_SECONDS = 5
DEFAULT_RESOLUTION = "1280x720"
DEFAULT_FPS = 24

# Polling
POLL_INITIAL_SECONDS = 5
POLL_MAX_SECONDS = 30
POLL_TIMEOUT_SECONDS = 20 * 60
SUBMIT_RETRIES = 3


@dataclass
class ModelSpec:
    """One entry in the model registry.

    path is the RunComfy Model API route: {vendor}/{model}/{endpoint},
    POSTed to https://model-api.runcomfy.net/v1/models/{path}.
    """

    path: str
    duration_key: str | None = "duration"
    default_params: dict = field(default_factory=dict)
    verified: bool = False


# Slugs below follow the vendor/model/endpoint pattern used across
# runcomfy.com model pages. Confirm the exact slug and parameter schema on the
# model's API page (https://www.runcomfy.com/models/<vendor>/<model>/api)
# before the first paid run, or pass an explicit route with --model.
MODEL_REGISTRY: dict[str, ModelSpec] = {
    "wan": ModelSpec(path="wan-ai/wan-2-6/text-to-video"),
    "seedance-lite": ModelSpec(path="bytedance/seedance-v1-lite/text-to-video"),
    "seedance-pro": ModelSpec(path="bytedance/seedance-v1.5-pro/text-to-video"),
    "kling": ModelSpec(path="kwai/kling-v2-5/text-to-video"),
    "veo": ModelSpec(path="google/veo-3/text-to-video"),
}

DEFAULT_MODEL = "wan"


def resolve_model(name: str) -> ModelSpec:
    """Resolve a friendly registry name or a raw vendor/model/endpoint route."""
    if name in MODEL_REGISTRY:
        return MODEL_REGISTRY[name]
    if name.count("/") >= 2:
        return ModelSpec(path=name.strip("/"))
    raise ValueError(
        f"Unknown model '{name}'. Use one of {sorted(MODEL_REGISTRY)} "
        "or a full route like 'wan-ai/wan-2-6/text-to-video'."
    )


def runcomfy_token() -> str | None:
    return os.environ.get("RUNCOMFY_API_TOKEN")
