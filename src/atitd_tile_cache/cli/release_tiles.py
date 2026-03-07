from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from atitd_tile_cache.tooling.release_tiles import BuildReleaseConfig, run_build_release


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build tile cache release archive from local cache."
    )
    parser.add_argument("--tale", default="tale10", help="Tale directory name (e.g. tale10).")
    parser.add_argument(
        "--tile-cache-root",
        default=str((Path.cwd() / "tile_cache").resolve()),
        help="Root directory containing tale directories.",
    )
    parser.add_argument(
        "--output-dir",
        default=str((Path(tempfile.gettempdir()) / "atitd-tile-cache" / "releases").resolve()),
        help="Directory where release archives/checksums are written.",
    )
    parser.add_argument(
        "--asset-name-template",
        default="tile_cache_{tale}.tar.gz",
        help="Release asset filename template. Supports {tale}.",
    )
    return parser.parse_args()


def namespace_to_config(args: argparse.Namespace) -> BuildReleaseConfig:
    return BuildReleaseConfig(
        tale=str(args.tale),
        tile_cache_root=str(args.tile_cache_root),
        output_dir=str(args.output_dir),
        asset_name_template=str(args.asset_name_template),
    )


def main() -> int:
    args = parse_args()
    return int(run_build_release(namespace_to_config(args)))


if __name__ == "__main__":
    raise SystemExit(main())
