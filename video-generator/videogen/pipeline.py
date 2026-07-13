"""End-to-end orchestration: plan -> generate clips -> assemble, resumable."""

import json
import logging
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from . import assembler, config, planner

log = logging.getLogger("videogen.pipeline")


@dataclass
class PipelineOptions:
    model_name: str = config.DEFAULT_MODEL
    output_dir: str = "outputs"
    concurrency: int = config.DEFAULT_CONCURRENCY
    max_clips: int = config.DEFAULT_MAX_CLIPS
    resolution: str = config.DEFAULT_RESOLUTION
    fps: int = config.DEFAULT_FPS
    extra_params: dict = field(default_factory=dict)


class Manifest:
    """Persistent record of a run; the unit of resumability."""

    def __init__(self, run_dir: str, data: dict):
        self.run_dir = run_dir
        self.data = data

    @classmethod
    def create(cls, output_dir: str, plan: planner.Plan, options: PipelineOptions) -> "Manifest":
        run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        run_dir = os.path.join(output_dir, run_id)
        os.makedirs(os.path.join(run_dir, "clips"), exist_ok=True)
        data = {
            "run_id": run_id,
            "model": options.model_name,
            "plan": plan.to_dict(),
            "scenes": [
                {"index": i, "status": "pending", "clip": None, "request_id": None, "error": None}
                for i in range(len(plan.scenes))
            ],
            "final": None,
        }
        manifest = cls(run_dir, data)
        manifest.save()
        return manifest

    @classmethod
    def load(cls, output_dir: str, run_id: str) -> "Manifest":
        run_dir = os.path.join(output_dir, run_id)
        with open(os.path.join(run_dir, "manifest.json"), encoding="utf-8") as fh:
            return cls(run_dir, json.load(fh))

    def save(self) -> None:
        path = os.path.join(self.run_dir, "manifest.json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2)
        os.replace(tmp, path)

    @property
    def plan(self) -> planner.Plan:
        return planner.plan_from_dict(self.data["plan"])


def build_payload(scene: planner.Scene, spec: config.ModelSpec, options: PipelineOptions) -> dict:
    payload = {"prompt": scene.prompt, **spec.default_params, **options.extra_params}
    if spec.duration_key:
        payload.setdefault(spec.duration_key, scene.duration)
    return payload


def run(client, plan: planner.Plan, options: PipelineOptions, manifest: Manifest | None = None) -> Manifest:
    """Generate every pending scene, then assemble the final video.

    client is anything with generate_clip(model_path, payload, dest) — the
    real RunComfyClient or the dry-run mock. Pass an existing manifest to
    resume: completed scenes are skipped, so paid clips are never redone.
    """
    spec = config.resolve_model(options.model_name)
    if len(plan.scenes) > options.max_clips:
        raise RuntimeError(
            f"plan has {len(plan.scenes)} scenes, above --max-clips {options.max_clips}; "
            "raise the cap explicitly if intended"
        )

    if manifest is None:
        manifest = Manifest.create(options.output_dir, plan, options)
    log.info("run %s: %d scenes on %s", manifest.data["run_id"], len(plan.scenes), spec.path)

    def generate(index: int) -> str:
        scene = plan.scenes[index]
        dest = os.path.join(manifest.run_dir, "clips", f"scene_{index:02d}.mp4")
        payload = build_payload(scene, spec, options)
        return client.generate_clip(spec.path, payload, dest)

    pending = [
        s["index"] for s in manifest.data["scenes"]
        if not (s["status"] == "done" and s["clip"] and os.path.exists(os.path.join(manifest.run_dir, s["clip"])))
    ]
    failures: list[tuple[int, Exception]] = []
    if pending:
        with ThreadPoolExecutor(max_workers=max(1, options.concurrency)) as pool:
            futures = {pool.submit(generate, i): i for i in pending}
            for future in as_completed(futures):
                index = futures[future]
                record = manifest.data["scenes"][index]
                try:
                    clip_path = future.result()
                except Exception as exc:  # noqa: BLE001 - recorded and re-raised below
                    record.update(status="failed", error=str(exc))
                    failures.append((index, exc))
                    log.error("scene %d failed: %s", index, exc)
                else:
                    record.update(status="done", clip=os.path.relpath(clip_path, manifest.run_dir), error=None)
                    log.info("scene %d done: %s", index, clip_path)
                manifest.save()

    if failures:
        raise RuntimeError(
            f"{len(failures)} scene(s) failed (run {manifest.data['run_id']}). "
            f"Fix and rerun with --resume {manifest.data['run_id']} — completed clips are kept. "
            f"First error: scene {failures[0][0]}: {failures[0][1]}"
        )

    clips = [os.path.join(manifest.run_dir, s["clip"]) for s in manifest.data["scenes"]]
    final = os.path.join(manifest.run_dir, "final.mp4")
    assembler.assemble(clips, manifest.run_dir, final, options.resolution, options.fps)
    manifest.data["final"] = os.path.relpath(final, manifest.run_dir)
    manifest.save()
    return manifest
