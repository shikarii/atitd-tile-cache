"""One-time tile mirroring logic for ATITD map tiles."""

from __future__ import annotations

import concurrent.futures
import dataclasses
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

DEFAULT_BASE_URL = "https://static.atitd.wiki/maps"
DEFAULT_OUTPUT_DIR = str(Path("tile_cache").resolve())


@dataclasses.dataclass(frozen=True)
class TileCoord:
    z: int
    x: int
    y: int


@dataclasses.dataclass
class MirrorStats:
    downloaded: int = 0
    existing: int = 0
    missing: int = 0
    failed: int = 0


@dataclasses.dataclass(frozen=True)
class MirrorTilesConfig:
    tale: str = "tale10"
    base_url: str = DEFAULT_BASE_URL
    output_dir: str = DEFAULT_OUTPUT_DIR
    min_zoom: int = 0
    max_zoom: int = 6
    workers: int = 24
    timeout: float = 10.0
    retries: int = 2
    overwrite: bool = False


def iter_tile_coords(min_zoom: int, max_zoom: int) -> list[TileCoord]:
    coords: list[TileCoord] = []
    for z in range(min_zoom, max_zoom + 1):
        span = 1 << z
        for x in range(span):
            for y in range(span):
                coords.append(TileCoord(z=z, x=x, y=y))
    return coords


def tile_url(base_url: str, tale: str, coord: TileCoord) -> str:
    return f"{base_url.rstrip('/')}/{tale}/{coord.z}/{coord.x}/{coord.y}.png"


def tile_path(output_root: Path, tale: str, coord: TileCoord) -> Path:
    return output_root / tale / str(coord.z) / str(coord.x) / f"{coord.y}.png"


def download_one(
    base_url: str,
    tale: str,
    output_root: Path,
    coord: TileCoord,
    timeout: float,
    retries: int,
    overwrite: bool,
) -> str:
    path = tile_path(output_root, tale, coord)
    if path.exists() and not overwrite:
        return "existing"

    path.parent.mkdir(parents=True, exist_ok=True)
    url = tile_url(base_url, tale, coord)
    request = urllib.request.Request(url, headers={"User-Agent": "atitd-tile-mirror/1.0"})

    attempt = 0
    while True:
        attempt += 1
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    return "failed"
                content = response.read()
                tmp_path = path.with_suffix(".tmp")
                tmp_path.write_bytes(content)
                os.replace(tmp_path, path)
                return "downloaded"
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return "missing"
            if attempt > retries + 1:
                return "failed"
        except (urllib.error.URLError, TimeoutError):
            if attempt > retries + 1:
                return "failed"


def emit_progress(progress: Callable[[str], None] | None, message: str) -> None:
    if progress is None:
        return
    progress(message)


def run_mirror_tiles(
    config: MirrorTilesConfig, progress: Callable[[str], None] | None = print
) -> int:
    if config.min_zoom < 0 or config.max_zoom < config.min_zoom:
        raise ValueError("Invalid zoom range.")

    output_root = Path(config.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    coords = iter_tile_coords(config.min_zoom, config.max_zoom)
    total = len(coords)
    stats = MirrorStats()
    started = time.time()

    emit_progress(
        progress,
        f"[tile-mirror] tale={config.tale} zoom={config.min_zoom}..{config.max_zoom} "
        f"total={total} workers={config.workers} out={output_root}",
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.workers) as executor:
        futures = [
            executor.submit(
                download_one,
                config.base_url,
                config.tale,
                output_root,
                coord,
                config.timeout,
                config.retries,
                config.overwrite,
            )
            for coord in coords
        ]
        for idx, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            result = future.result()
            if result == "downloaded":
                stats.downloaded += 1
            elif result == "existing":
                stats.existing += 1
            elif result == "missing":
                stats.missing += 1
            else:
                stats.failed += 1
            if idx % 250 == 0 or idx == total:
                elapsed = time.time() - started
                rate = idx / elapsed if elapsed > 0 else 0.0
                emit_progress(
                    progress,
                    f"[tile-mirror] {idx}/{total} downloaded={stats.downloaded} "
                    f"existing={stats.existing} missing={stats.missing} "
                    f"failed={stats.failed} rate={rate:.1f}/s",
                )

    elapsed = time.time() - started
    emit_progress(
        progress,
        f"[tile-mirror] done in {elapsed:.1f}s | downloaded={stats.downloaded} "
        f"existing={stats.existing} missing={stats.missing} failed={stats.failed}",
    )
    return 0 if stats.failed == 0 else 1
