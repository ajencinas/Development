import json
import os
import shutil
import subprocess

import pytest

from videogen import pipeline, planner, runcomfy

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def load_plan():
    return planner.load_plan_file(os.path.join(FIXTURES, "plan.json"))


def options(tmp_path, **kw):
    return pipeline.PipelineOptions(output_dir=str(tmp_path / "outputs"), concurrency=2, **kw)


class FailOnceClient(runcomfy.MockRunComfyClient):
    """Mock that fails a chosen scene on the first attempt only."""

    def __init__(self, fail_index):
        super().__init__()
        self.fail_index = fail_index
        self.failed = False

    def generate_clip(self, model_path, payload, dest):
        if f"scene_{self.fail_index:02d}" in dest and not self.failed:
            self.failed = True
            raise runcomfy.GenerationFailed("simulated failure")
        return super().generate_clip(model_path, payload, dest)


@needs_ffmpeg
def test_dry_run_end_to_end(tmp_path):
    manifest = pipeline.run(runcomfy.MockRunComfyClient(), load_plan(), options(tmp_path))
    final = os.path.join(manifest.run_dir, manifest.data["final"])
    assert os.path.exists(final)
    # final video should be roughly the sum of the clip durations (2 x 2s)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", final],
        capture_output=True, text=True, check=True,
    )
    duration = float(json.loads(probe.stdout)["format"]["duration"])
    assert 3.0 < duration < 5.5
    assert all(s["status"] == "done" for s in manifest.data["scenes"])


@needs_ffmpeg
def test_failure_then_resume_skips_done_scenes(tmp_path):
    opts = options(tmp_path)
    client = FailOnceClient(fail_index=1)
    with pytest.raises(RuntimeError, match="--resume"):
        pipeline.run(client, load_plan(), opts)

    run_id = os.listdir(opts.output_dir)[0]
    manifest = pipeline.Manifest.load(opts.output_dir, run_id)
    statuses = {s["index"]: s["status"] for s in manifest.data["scenes"]}
    assert statuses[0] == "done"
    assert statuses[1] == "failed"

    # resume: scene 0 must not be regenerated
    clip0 = os.path.join(manifest.run_dir, "clips", "scene_00.mp4")
    mtime_before = os.path.getmtime(clip0)
    manifest = pipeline.run(client, manifest.plan, opts, manifest=manifest)
    assert os.path.getmtime(clip0) == mtime_before
    assert os.path.exists(os.path.join(manifest.run_dir, manifest.data["final"]))


def test_max_clips_guard(tmp_path):
    plan = planner.plan_from_dict(
        {"title": "big", "scenes": [{"prompt": f"s{i}"} for i in range(5)]}
    )
    with pytest.raises(RuntimeError, match="max-clips"):
        pipeline.run(object(), plan, options(tmp_path, max_clips=3))


def test_build_payload_merges_params():
    from videogen import config

    spec = config.ModelSpec(path="a/b/c", duration_key="duration", default_params={"aspect_ratio": "16:9"})
    scene = planner.Scene(prompt="p", duration=6)
    payload = pipeline.build_payload(scene, spec, pipeline.PipelineOptions(extra_params={"seed": 7}))
    assert payload == {"prompt": "p", "aspect_ratio": "16:9", "seed": 7, "duration": 6}


def test_build_payload_user_duration_wins():
    from videogen import config

    spec = config.ModelSpec(path="a/b/c", duration_key="duration")
    payload = pipeline.build_payload(
        planner.Scene(prompt="p", duration=6), spec,
        pipeline.PipelineOptions(extra_params={"duration": 10}),
    )
    assert payload["duration"] == 10
