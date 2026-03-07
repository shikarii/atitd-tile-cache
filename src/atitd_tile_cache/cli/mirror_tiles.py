from __future__ import annotations

import argparse
from pathlib import Path

from atitd_tile_cache.tooling.mirror_tiles import MirrorTilesConfig, run_mirror_tiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror ATITD map tiles locally.")
    parser.add_argument("--tale", default="tale10", help="Tale directory name (e.g. tale10).")
    parser.add_argument(
        "--base-url",
        default="https://static.atitd.wiki/maps",
        help="Base URL containing tale tile directories.",
    )
    parser.add_argument(
        "--output-dir",
        default=str((Path.cwd() / "tile_cache").resolve()),
        help="Local output root directory.",
    )
    parser.add_argument("--min-zoom", type=int, default=0, help="Minimum zoom level.")
    parser.add_argument("--max-zoom", type=int, default=6, help="Maximum zoom level.")
    parser.add_argument("--workers", type=int, default=24, help="Concurrent download workers.")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds.")
    parser.add_argument("--retries", type=int, default=2, help="Retries for transient failures.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-download even when tile already exists.",
    )
    return parser.parse_args()


def namespace_to_config(args: argparse.Namespace) -> MirrorTilesConfig:
    return MirrorTilesConfig(
        tale=str(args.tale),
        base_url=str(args.base_url),
        output_dir=str(args.output_dir),
        min_zoom=int(args.min_zoom),
        max_zoom=int(args.max_zoom),
        workers=int(args.workers),
        timeout=float(args.timeout),
        retries=int(args.retries),
        overwrite=bool(args.overwrite),
    )


def main() -> int:
    args = parse_args()
    return int(run_mirror_tiles(namespace_to_config(args)))


if __name__ == "__main__":
    raise SystemExit(main())
