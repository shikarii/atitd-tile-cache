from __future__ import annotations

import argparse
from pathlib import Path

from atitd_tile_cache.tooling.compress_tiles import CompressTilesConfig, run_compress_tiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert cached map PNG tiles to WebP.")
    parser.add_argument(
        "--tile-cache-dir",
        default=str((Path.cwd() / "tile_cache").resolve()),
        help="Path to tile cache root.",
    )
    parser.add_argument("--quality", type=int, default=85, help="WebP quality 1-100.")
    parser.add_argument("--workers", type=int, default=8, help="Parallel worker count.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-convert .webp files even when present.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report candidates without writing output files.",
    )
    return parser.parse_args()


def namespace_to_config(args: argparse.Namespace) -> CompressTilesConfig:
    return CompressTilesConfig(
        tile_cache_dir=str(args.tile_cache_dir),
        quality=int(args.quality),
        workers=int(args.workers),
        dry_run=bool(args.dry_run),
        overwrite=bool(args.overwrite),
    )


def main() -> int:
    args = parse_args()
    return int(run_compress_tiles(namespace_to_config(args)))


if __name__ == "__main__":
    raise SystemExit(main())
