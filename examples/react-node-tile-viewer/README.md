# React + Node Tile Viewer Example

Minimal example that:

1. Downloads the latest `atitd-tile-cache` release asset when local cache is missing
2. Extracts tiles into a user-local directory (`~/.atitd/tile_cache` by default)
3. Serves tiles with a basic Node.js/Express server
4. Renders the tile layer in a small React + Leaflet client

## Run

```bash
cd examples/react-node-tile-viewer
npm install
npm run dev
```

Open: `http://localhost:8788`

## Runtime behavior

- On startup, the server checks for `<tile-cache-root>/<tale>/0`.
- If missing, it fetches release metadata from GitHub and downloads:
  - `tile_cache_<tale>.tar.gz`
- The archive is extracted to the cache root, then served from disk.

## Environment variables

- `PORT` (default: `8788`)
- `ATITD_TILE_TALE` (default: `tale10`)
- `ATITD_TILE_CACHE_ROOT` (default: `~/.atitd/tile_cache`)
- `ATITD_TILE_RELEASE_REPO` (required, format: `<owner>/<repo>`)
- `ATITD_TILE_RELEASE_TAG` (default: `latest`)
  - Set this to a specific tag to pin the example to a known release.

Example pinned startup:

```bash
ATITD_TILE_RELEASE_REPO=owner/atitd-tile-cache ATITD_TILE_RELEASE_TAG=v2026.03.08-tale10 npm run dev
```

## Notes

- This example is intentionally minimal and not production-hardened.
- It demonstrates the "latest release + user-dir cache bootstrap" pattern.
- Tile rights remain with their original owners.
