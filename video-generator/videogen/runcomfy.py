"""RunComfy Model API client.

Flow: POST /v1/models/{vendor}/{model}/{endpoint} -> {request_id, ...},
poll GET /v1/requests/{id}/status until completed, then
GET /v1/requests/{id}/result for output URLs.
"""

import logging
import shutil
import subprocess
import time

import requests

from . import config

log = logging.getLogger("videogen.runcomfy")

RETRYABLE_STATUSES = {408, 429, 500, 502, 503, 504}


class RunComfyError(RuntimeError):
    pass


class GenerationFailed(RunComfyError):
    pass


class RunComfyClient:
    def __init__(self, token: str, base_url: str = config.MODEL_API_BASE, session: requests.Session | None = None):
        if not token:
            raise RunComfyError("RUNCOMFY_API_TOKEN is not set")
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )

    def _request(self, method: str, url: str, retries: int = config.SUBMIT_RETRIES, **kwargs) -> requests.Response:
        delay = 2.0
        for attempt in range(retries + 1):
            try:
                resp = self.session.request(method, url, timeout=60, **kwargs)
            except requests.RequestException as exc:
                if attempt == retries:
                    raise RunComfyError(f"{method} {url} failed: {exc}") from exc
            else:
                if resp.status_code < 400:
                    return resp
                if resp.status_code not in RETRYABLE_STATUSES or attempt == retries:
                    raise RunComfyError(
                        f"{method} {url} returned {resp.status_code}: {resp.text[:500]}"
                    )
            log.warning("retrying %s %s (attempt %d)", method, url, attempt + 2)
            time.sleep(delay)
            delay = min(delay * 2, 30)
        raise RunComfyError("unreachable")

    def submit(self, model_path: str, payload: dict) -> dict:
        """Submit a generation job; returns the API response incl. request_id."""
        url = f"{self.base_url}/v1/models/{model_path}"
        data = self._request("POST", url, json=payload).json()
        if "request_id" not in data:
            raise RunComfyError(f"no request_id in response: {data}")
        log.info("submitted %s -> request %s", model_path, data["request_id"])
        return data

    def wait(self, request_id: str, timeout: float = config.POLL_TIMEOUT_SECONDS) -> dict:
        """Poll status until completed; returns the final status payload."""
        url = f"{self.base_url}/v1/requests/{request_id}/status"
        deadline = time.monotonic() + timeout
        interval = config.POLL_INITIAL_SECONDS
        while True:
            data = self._request("GET", url).json()
            status = str(data.get("status", "")).lower()
            if status in {"completed", "succeeded", "success"}:
                return data
            if status in {"failed", "error", "cancelled", "canceled"}:
                raise GenerationFailed(f"request {request_id} ended with status '{status}': {data}")
            if time.monotonic() > deadline:
                raise GenerationFailed(f"request {request_id} timed out after {timeout:.0f}s (last status: {status})")
            log.debug("request %s status=%s; sleeping %ds", request_id, status, interval)
            time.sleep(interval)
            interval = min(interval * 1.5, config.POLL_MAX_SECONDS)

    def result(self, request_id: str) -> dict:
        url = f"{self.base_url}/v1/requests/{request_id}/result"
        return self._request("GET", url).json()

    def download(self, url: str, dest: str) -> str:
        with self.session.get(url, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    fh.write(chunk)
        return dest

    def generate_clip(self, model_path: str, payload: dict, dest: str) -> str:
        """Submit -> wait -> fetch result -> download the video to dest."""
        submission = self.submit(model_path, payload)
        request_id = submission["request_id"]
        self.wait(request_id)
        result = self.result(request_id)
        video_url = extract_video_url(result)
        if not video_url:
            raise GenerationFailed(f"no video URL found in result for {request_id}: {result}")
        return self.download(video_url, dest)


def extract_video_url(result: dict) -> str | None:
    """Find a video URL anywhere in the result payload.

    Model result schemas vary across vendors, so walk the structure and take
    the first URL that looks like a video (or, failing that, any URL under a
    video-ish key).
    """
    video_exts = (".mp4", ".webm", ".mov")
    fallback: str | None = None

    def walk(node, key: str = ""):
        nonlocal fallback
        if isinstance(node, dict):
            for k, v in node.items():
                found = walk(v, k)
                if found:
                    return found
        elif isinstance(node, list):
            for item in node:
                found = walk(item, key)
                if found:
                    return found
        elif isinstance(node, str) and node.startswith(("http://", "https://")):
            path = node.split("?", 1)[0].lower()
            if path.endswith(video_exts):
                return node
            if fallback is None and key.lower() in {"url", "video_url", "video", "output_url"}:
                fallback = node
        return None

    return walk(result) or fallback


class MockRunComfyClient:
    """Dry-run client: renders placeholder clips locally with ffmpeg.

    Exercises the full pipeline (submission bookkeeping, manifest, assembly)
    without network access or credits.
    """

    def __init__(self, clip_seconds_cap: float = 2.0):
        self.clip_seconds_cap = clip_seconds_cap
        self._counter = 0
        if not shutil.which("ffmpeg"):
            raise RunComfyError("ffmpeg is required for --dry-run")

    def generate_clip(self, model_path: str, payload: dict, dest: str) -> str:
        self._counter += 1
        seconds = min(float(payload.get("duration", 2) or 2), self.clip_seconds_cap)
        label = str(payload.get("prompt", "scene"))[:40].replace("'", "").replace('"', "").replace(":", "").replace("\\", "").replace("%", "")
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi",
            "-i", f"testsrc2=size=640x360:rate=24:duration={seconds}",
            "-vf", f"drawtext=text='{label}':fontcolor=white:fontsize=20:x=10:y=10",
            "-pix_fmt", "yuv420p", dest,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            # drawtext may be unavailable in minimal ffmpeg builds; retry plain
            cmd = [c for c in cmd if not c.startswith("drawtext")]
            cmd = [c for c in cmd if c != "-vf"]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RunComfyError(f"mock clip render failed: {proc.stderr[:500]}")
        log.info("dry-run: rendered placeholder clip %s", dest)
        return dest
