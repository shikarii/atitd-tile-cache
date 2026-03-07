# AGENTS.md

Repository operating rules for coding agents.

## 0. Prime Directive

- Move fast on reproducible tile distribution.
- Keep this repository focused on compressed, auditable cache snapshots.
- Do not introduce architecture changes without maintainer approval.

## 1. Purpose and Scope

This repository exists to host ATITD tile cache release artifacts.

- Source tiles are mirrored from the ATITD wiki.
- Tiles are optionally converted to WebP for smaller payloads.
- Release archives are uploaded as GitHub Release assets.
- Other code repositories must not be used for large tile binary history.

## 2. Storage Contract

- Commit only compressed tile snapshots as `.webp` under `tile_cache/<tale>/...`.
- Never commit source `.png` tiles.
- Never commit generated release archives (`.tar.gz`, `.sha256`).
- Keep deterministic layout:
  - `<tale>/<z>/<x>/<y>.webp`
- Release assets are built from the tracked WebP snapshot.

## 3. Python Tooling Contract

- Use `uv` for environment and dependency execution.
- Keep code under `src/`.
- CLI entrypoints belong under `src/atitd_tile_cache/cli/`.
- Core logic belongs under `src/atitd_tile_cache/tooling/`.
- Keep tooling pure and side-effect boundaries explicit.

## 4. Quality Gates

Before push:

1. `uv sync`
2. `uv run ruff check .`
3. `uv run ruff format --check .`
4. `uv run pytest`
5. `uv run pytype src/atitd_tile_cache` (Linux runner/CI)

## 5. Release Workflow Contract

Every tile release should be reproducible and auditable:

- Before publishing a release, create a release branch from current `main`.
  - Naming: `release/<tag-or-purpose>` (example: `release/v2026.03.07-tale10`).
  - Do not cut release branches from `develop`.
- Record the source tale and zoom range.
- Record compression settings (quality/workers).
- Include SHA256 for uploaded archives.
- Prefer manual workflow dispatch for controlled releases.
- After every published release, `main` must be updated from `develop` immediately.
  - Preferred path: fast-forward `main` to `develop`.
  - If fast-forward is not possible, open a sync PR from `develop` to `main` and merge it before the next release.

## 6. Branch Discipline

- `develop` is the default integration branch.
- Use feature branches and pull requests into `develop`.
- CODEOWNERS approval is required before merge.
- Every PR must include a full issue URL and a closing statement with full issue URL.

## 7. Issue Close-Out

- Use `.github/ISSUE_CLOSE_SUMMARY_TEMPLATE.md` before closing an issue.
- Include PR URL, commit SHA, and validation evidence.
