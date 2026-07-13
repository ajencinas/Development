"""Command-line entry point: one command in, finished video out."""

import argparse
import logging
import os
import sys

from . import config, pipeline, planner, runcomfy


def parse_kv(pairs: list[str]) -> dict:
    out = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"--param expects key=value, got '{pair}'")
        key, value = pair.split("=", 1)
        for cast in (int, float):
            try:
                value = cast(value)
                break
            except ValueError:
                continue
        out[key] = value
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="videogen",
        description="Autonomous video generator on the RunComfy Model API: "
        "plans scenes with Claude, generates a clip per scene, stitches with ffmpeg.",
    )
    p.add_argument("topic", nargs="?", help="Topic for the video (omit with --auto-topic or --plan-file)")
    p.add_argument("--auto-topic", action="store_true", help="Let Claude invent the topic")
    p.add_argument("--plan-file", help="JSON plan file; skips the Claude planning step")
    p.add_argument("--scenes", type=int, default=config.DEFAULT_SCENES, help="Number of scenes (default %(default)s)")
    p.add_argument("--duration", type=int, default=config.DEFAULT_CLIP_SECONDS, help="Target seconds per clip (default %(default)s)")
    p.add_argument("--model", default=config.DEFAULT_MODEL,
                   help=f"Registry name ({', '.join(sorted(config.MODEL_REGISTRY))}) or raw vendor/model/endpoint route")
    p.add_argument("--param", action="append", default=[], metavar="KEY=VALUE",
                   help="Extra model parameter, repeatable (e.g. --param aspect_ratio=16:9)")
    p.add_argument("--resolution", default=config.DEFAULT_RESOLUTION, help="Output resolution (default %(default)s)")
    p.add_argument("--fps", type=int, default=config.DEFAULT_FPS, help="Output fps (default %(default)s)")
    p.add_argument("--concurrency", type=int, default=config.DEFAULT_CONCURRENCY, help="Parallel scene generations (default %(default)s)")
    p.add_argument("--max-clips", type=int, default=config.DEFAULT_MAX_CLIPS, help="Spend guard: abort if the plan exceeds this many clips (default %(default)s)")
    p.add_argument("--output-dir", default="outputs", help="Where runs are stored (default %(default)s)")
    p.add_argument("--resume", metavar="RUN_ID", help="Resume a previous run; only incomplete scenes are regenerated")
    p.add_argument("--dry-run", action="store_true", help="No API calls: render placeholder clips locally with ffmpeg")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("videogen")

    try:
        options = pipeline.PipelineOptions(
            model_name=args.model,
            output_dir=args.output_dir,
            concurrency=args.concurrency,
            max_clips=args.max_clips,
            resolution=args.resolution,
            fps=args.fps,
            extra_params=parse_kv(args.param),
        )
        config.resolve_model(args.model)  # fail fast on bad model names

        manifest = None
        if args.resume:
            manifest = pipeline.Manifest.load(args.output_dir, args.resume)
            plan = manifest.plan
            log.info("resuming run %s ('%s')", args.resume, plan.title)
        elif args.plan_file:
            plan = planner.load_plan_file(args.plan_file)
        else:
            if not args.topic and not args.auto_topic:
                raise SystemExit("Provide a topic, or use --auto-topic / --plan-file. See --help.")
            if not os.environ.get("ANTHROPIC_API_KEY"):
                log.warning("ANTHROPIC_API_KEY not set; relying on other Anthropic credentials")
            plan = planner.generate_plan(args.topic, args.scenes, args.duration)

        if args.dry_run:
            client = runcomfy.MockRunComfyClient()
            log.info("dry run: placeholder clips, no credits spent")
        else:
            client = runcomfy.RunComfyClient(token=config.runcomfy_token())
            log.info(
                "generating %d clip(s) on '%s' — this consumes RunComfy credits",
                len(plan.scenes), options.model_name,
            )

        manifest = pipeline.run(client, plan, options, manifest=manifest)
        final = os.path.join(manifest.run_dir, manifest.data["final"])
        print(f"\nDone: {final}")
        print(f"Run ID: {manifest.data['run_id']} (manifest: {manifest.run_dir}/manifest.json)")
        return 0
    except KeyboardInterrupt:
        log.error("interrupted")
        return 130
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        log.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
