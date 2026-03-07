# atitd-tile-cache

[![CI](https://github.com/shikarii/atitd-tile-cache/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/shikarii/atitd-tile-cache/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/shikarii/atitd-tile-cache?display_name=tag)](https://github.com/shikarii/atitd-tile-cache/releases)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)

Compressed ATITD tile-cache snapshots and release assets.

## What this repo is for

- Track compressed tile snapshots in git: `tile_cache/<tale>/**/*.webp`
- Publish downloadable release archives for consumers
- Keep release artifacts reproducible with checksum files

## What consumers usually need

1. Download latest release asset:
   - `tile_cache_<tale>.tar.gz`
   - `tile_cache_<tale>.tar.gz.sha256`
2. Verify checksum.
3. Extract archive into your local tile-cache root.

Archive layout:

- `<tale>/<z>/<x>/<y>.webp`

## Use the tooling locally

Requirements:

- Python 3.12+
- `uv`

Install:

```bash
uv sync
```

Available commands:

- `uv run atitd-tile-mirror`
- `uv run atitd-tile-compress`
- `uv run atitd-tile-release`

Examples:

```bash
uv run atitd-tile-mirror --tale tale10 --min-zoom 0 --max-zoom 6
uv run atitd-tile-compress --tile-cache-dir tile_cache --quality 85 --workers 8
uv run atitd-tile-release --tale tale10 --tile-cache-root tile_cache --output-dir work/releases
```

## Contribution and policy

- `develop` is the default integration branch.
- Use feature branches and PRs targeting `develop`.
- CODEOWNERS approval is required before merge.
- For release operations, follow `AGENTS.md` and `CONTRIBUTING.md`.

## License and attribution

- See `LICENSE` for repository licensing and third-party image notice.
- Tile images are mirrored from `https://atitd.wiki/`.
- Image rights are retained by their original owners, including Desert Nomad Studios.
