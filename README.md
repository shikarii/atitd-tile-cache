# atitd-tile-cache

Public tile cache repository for ATITD map caches.

This repository tracks compressed `.webp` tile snapshots directly under
`tile_cache/<tale>/...`, then produces release archives from that tracked state.

## Layout

- `src/atitd_tile_cache/` - python tooling package
- `tile_cache/` - tracked compressed cache snapshots (`.webp`)
- `releases/` - generated `.tar.gz` and `.sha256` artifacts (ignored by git)

## Runtime requirements

- Python 3.12+
- `uv`

## Branch and approval policy

- `develop` is the primary/default branch.
- Changes should land through pull requests targeting `develop`.
- `develop` is protected and requires CODEOWNERS review approval.
- PRs must include full issue URLs and a closing statement (`Closes <issue-url>`).
- CI workflows are configured for self-hosted runners to avoid GitHub-hosted billing.

## Setup

```bash
uv sync
```

## Package entrypoints (no top-level scripts required)

This repo is intended to run as an installed package via `uv run` entrypoints:

- `atitd-tile-mirror`
- `atitd-tile-compress`
- `atitd-tile-release`

## CLI commands

Mirror tiles from wiki:

```bash
uv run atitd-tile-mirror --tale tale10 --min-zoom 0 --max-zoom 6
```

Convert PNG tiles to WebP:

```bash
uv run atitd-tile-compress --tile-cache-dir tile_cache --quality 85 --workers 8
```

Package release archive:

```bash
uv run atitd-tile-release --tale tale10 --tile-cache-root tile_cache --output-dir releases
```

## Release asset contract

- Asset name: `tile_cache_<tale>.tar.gz` (default)
- Archive layout: `<tale>/<z>/<x>/<y>.webp`
- Checksum: `<asset>.sha256`

## Tile snapshot policy

- Tracked in git: `tile_cache/**/*.webp`
- Never tracked: raw `.png` source tiles
- Never tracked: generated release artifacts in `releases/`

## Publish release assets

Example with GitHub CLI:

```bash
gh release create v2026.03.07 \
  releases/tile_cache_tale10.tar.gz \
  releases/tile_cache_tale10.tar.gz.sha256 \
  --title "Tile cache tale10" \
  --notes "Refreshed tile cache from wiki."
```

## Optional local Docker runner setup

```bash
cp docker/.env.example docker/.env
# set RUNNER_TOKEN in docker/.env
bash docker/scripts/setup_runner.sh
```

## Quality checks

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pytest
# pytype runs in Linux CI/self-hosted runner
uv run pytype src/atitd_tile_cache
```
