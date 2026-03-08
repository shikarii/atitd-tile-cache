import { createWriteStream } from "node:fs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { pipeline } from "node:stream/promises";

import express from "express";
import tar from "tar";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.PORT ?? "8788");
const TALE = process.env.ATITD_TILE_TALE ?? "tale10";
const RELEASE_REPO = process.env.ATITD_TILE_RELEASE_REPO;
const RELEASE_TAG = process.env.ATITD_TILE_RELEASE_TAG ?? "latest";
const TILE_CACHE_ROOT =
  process.env.ATITD_TILE_CACHE_ROOT ?? path.join(os.homedir(), ".atitd", "tile_cache");
const TILE_ARCHIVE_NAME = `tile_cache_${TALE}.tar.gz`;

function log(message) {
  process.stdout.write(`[tile-example] ${message}\n`);
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function hasTaleTiles(taleDir) {
  if (!(await pathExists(taleDir))) {
    return false;
  }
  const zoom0 = path.join(taleDir, "0");
  return pathExists(zoom0);
}

function releaseApiUrl() {
  if (!RELEASE_REPO) {
    throw new Error("ATITD_TILE_RELEASE_REPO must be set (example: owner/atitd-tile-cache)");
  }
  if (RELEASE_TAG === "latest") {
    return `https://api.github.com/repos/${RELEASE_REPO}/releases/latest`;
  }
  return `https://api.github.com/repos/${RELEASE_REPO}/releases/tags/${encodeURIComponent(RELEASE_TAG)}`;
}

async function fetchReleaseMetadata() {
  const response = await fetch(releaseApiUrl(), {
    headers: {
      Accept: "application/vnd.github+json",
      "User-Agent": "atitd-tile-viewer-example"
    }
  });

  if (!response.ok) {
    throw new Error(`GitHub release metadata fetch failed (${response.status})`);
  }

  return response.json();
}

async function downloadAsset(assetUrl, outputPath) {
  const response = await fetch(assetUrl, {
    headers: {
      "User-Agent": "atitd-tile-viewer-example"
    }
  });

  if (!response.ok || !response.body) {
    throw new Error(`Asset download failed (${response.status})`);
  }

  await pipeline(response.body, createWriteStream(outputPath));
}

async function bootstrapTileCache() {
  const taleDir = path.join(TILE_CACHE_ROOT, TALE);
  if (await hasTaleTiles(taleDir)) {
    log(`Tile cache already present at ${taleDir}`);
    return;
  }

  await fs.mkdir(TILE_CACHE_ROOT, { recursive: true });
  const release = await fetchReleaseMetadata();
  const asset = Array.isArray(release.assets)
    ? release.assets.find((candidate) => candidate.name === TILE_ARCHIVE_NAME)
    : undefined;
  if (!asset || typeof asset.browser_download_url !== "string") {
    throw new Error(`Release asset not found: ${TILE_ARCHIVE_NAME}`);
  }

  const archivePath = path.join(os.tmpdir(), `${release.tag_name ?? "latest"}-${TILE_ARCHIVE_NAME}`);
  log(`Downloading ${asset.name} from ${release.tag_name ?? "latest"}...`);
  await downloadAsset(asset.browser_download_url, archivePath);

  log(`Extracting ${archivePath} -> ${TILE_CACHE_ROOT}`);
  await tar.x({
    file: archivePath,
    cwd: TILE_CACHE_ROOT
  });
  await fs.unlink(archivePath).catch(() => undefined);

  if (!(await hasTaleTiles(taleDir))) {
    throw new Error(`Extraction completed but tale directory is still missing: ${taleDir}`);
  }
}

function resolveTilePath(params) {
  const { tale, z, x, y } = params;
  if (!/^[a-zA-Z0-9_-]+$/.test(tale)) {
    return null;
  }
  if (!/^\d+$/.test(z) || !/^\d+$/.test(x) || !/^\d+$/.test(y)) {
    return null;
  }
  return path.join(TILE_CACHE_ROOT, tale, z, x, `${y}.webp`);
}

async function startServer() {
  await bootstrapTileCache();

  const app = express();
  app.use(express.static(path.join(__dirname, "public")));

  app.get("/api/config", (_req, res) => {
    res.json({
      ok: true,
      tale: TALE,
      tileUrlTemplate: `/tiles/${TALE}/{z}/{x}/{y}.webp`
    });
  });

  app.get("/tiles/:tale/:z/:x/:y.webp", async (req, res) => {
    const tilePath = resolveTilePath(req.params);
    if (!tilePath) {
      res.status(400).json({ ok: false, error: "Invalid tile path." });
      return;
    }
    if (!(await pathExists(tilePath))) {
      res.status(404).json({ ok: false, error: "Tile not found." });
      return;
    }
    res.sendFile(tilePath);
  });

  app.listen(PORT, () => {
    log(`Viewer ready: http://localhost:${PORT}`);
    log(`Serving tale ${TALE} from ${TILE_CACHE_ROOT}`);
  });
}

startServer().catch((error) => {
  process.stderr.write(`[tile-example] startup failed: ${String(error)}\n`);
  process.exitCode = 1;
});
