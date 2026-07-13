"""Stitch generated clips into one MP4 with ffmpeg."""

import logging
import os
import subprocess

from . import config

log = logging.getLogger("videogen.assembler")


class AssemblyError(RuntimeError):
    pass


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssemblyError(f"ffmpeg failed ({' '.join(cmd[:6])}...): {proc.stderr[-800:]}")


def normalize_clip(src: str, dest: str, resolution: str = config.DEFAULT_RESOLUTION, fps: int = config.DEFAULT_FPS) -> str:
    """Re-encode a clip to a common resolution/fps/codec so concat is seamless."""
    width, height = resolution.split("x")
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p"
    )
    _run([
        "ffmpeg", "-y", "-v", "error", "-i", src,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-an",  # source clips are video-only; drop any stray audio for clean concat
        dest,
    ])
    return dest


def concat_clips(clips: list[str], dest: str) -> str:
    """Concatenate normalized clips (same codec/params) via the concat demuxer."""
    if not clips:
        raise AssemblyError("no clips to assemble")
    list_path = dest + ".txt"
    with open(list_path, "w", encoding="utf-8") as fh:
        for clip in clips:
            escaped = os.path.abspath(clip).replace("'", "'\\''")
            fh.write(f"file '{escaped}'\n")
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", dest])
    os.unlink(list_path)
    return dest


def assemble(clips: list[str], workdir: str, dest: str, resolution: str = config.DEFAULT_RESOLUTION, fps: int = config.DEFAULT_FPS) -> str:
    normalized_dir = os.path.join(workdir, "normalized")
    os.makedirs(normalized_dir, exist_ok=True)
    normalized = []
    for i, clip in enumerate(clips):
        out = os.path.join(normalized_dir, f"scene_{i:02d}.mp4")
        normalized.append(normalize_clip(clip, out, resolution, fps))
    concat_clips(normalized, dest)
    log.info("assembled %d clips -> %s", len(clips), dest)
    return dest
