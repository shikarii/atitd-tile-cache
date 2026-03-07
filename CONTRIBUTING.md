# Contributing

This guide defines the exact contribution process for this repository.

## Repository purpose

This repository stores:

- governance and project docs
- compressed tile snapshots (`tile_cache/<tale>/**/*.webp`)
- release automation and release metadata

This repository does not store:

- source `.png` tiles
- generated release archives (`.tar.gz`, `.sha256`) in git history

## Required contribution flow

Follow this sequence every time:

1. Start with an issue.
   - Either create a new issue or use an existing one.
   - The issue must clearly describe the change and expected outcome.
2. Create a feature branch from `develop`.
   - Naming examples: `feat/...`, `fix/...`, `docs/...`, `chore/...`
3. Implement and validate locally.
   - Run:
     - `uv sync`
     - `uv run ruff check .`
     - `uv run ruff format --check .`
     - `uv run pytest`
   - `pytype` runs on Linux CI and must pass there before merge.
4. Commit and push your branch.
5. Open a pull request to `develop`.
   - PR body must include:
     - a full issue URL in `Linked Issue`
     - a closing statement with full issue URL, for example:
       - `Closes https://github.com/shikarii/atitd-tile-cache/issues/123`
6. Get approval from a CODEOWNER.
   - Approval is required before merge.
7. Merge only after all required checks are green.

## Pull request checklist

Before requesting merge, confirm:

- [ ] Issue exists and is linked by full URL.
- [ ] Branch targets `develop`.
- [ ] Local validation commands passed.
- [ ] CI checks passed.
- [ ] CODEOWNER approval is present.
- [ ] PR includes a full-URL close statement.

## Release rule

After every published release:

- `main` must be synced from `develop` immediately.
- Prefer fast-forwarding `main` to `develop`.
- If fast-forward is blocked, open a sync PR from `develop` to `main` and merge it before the next release.
