"""Tile cache compression: converts PNG map tiles to WebP for smaller footprint."""

from __future__ import annotations

import concurrent.futures
import dataclasses
import time
from collections.abc import Callable
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class CompressTilesConfig:
    tile_cache_dir: str = str(Path("tile_cache").resolve())
    quality: int = 85
    workers: int = 8
    dry_run: bool = False
    overwrite: bool = False


@dataclasses.dataclass
class CompressStats:
    converted: int = 0
    skipped: int = 0
    failed: int = 0
    bytes_before: int = 0
    bytes_after: int = 0


def _convert_one(
    png_path: Path,
    quality: int,
    overwrite: bool,
    dry_run: bool,
) -> tuple[str, int, int]:
    """Returns (status, bytes_before, bytes_after)."""
    webp_path = png_path.with_suffix(".webp")
    bytes_before = png_path.stat().st_size

    if webp_path.exists() and not overwrite:
        return ("skipped", bytes_before, webp_path.stat().st_size)

    if dry_run:
        return ("dry_run", bytes_before, 0)

    try:
        from PIL import Image  # noqa: PLC0415

        img = Image.open(png_path)
        img.save(webp_path, format="WEBP", quality=quality, method=6)
        bytes_after = webp_path.stat().st_size
        return ("converted", bytes_before, bytes_after)
    except Exception:  # noqa: BLE001
        return ("failed", bytes_before, 0)


def _emit(progress: Callable[[str], None] | None, msg: str) -> None:
    if progress is not None:
        progress(msg)


def run_compress_tiles(
    config: CompressTilesConfig,
    progress: Callable[[str], None] | None = print,
) -> int:
    cache_root = Path(config.tile_cache_dir).resolve()
    if not cache_root.exists():
        _emit(progress, f"[compress-tiles] ERROR: tile cache not found at {cache_root}")
        return 1

    png_files = sorted(cache_root.rglob("*.png"))
    total = len(png_files)
    if total == 0:
        _emit(progress, "[compress-tiles] No PNG tiles found.")
        return 0

    _emit(
        progress,
        f"[compress-tiles] Found {total} PNG tiles in {cache_root}"
        + (" (dry run)" if config.dry_run else f" | quality={config.quality}"),
    )

    stats = CompressStats()
    started = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.workers) as executor:
        futures = {
            executor.submit(_convert_one, p, config.quality, config.overwrite, config.dry_run): p
            for p in png_files
        }
        for idx, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            status, before, after = future.result()
            if status == "converted":
                stats.converted += 1
                stats.bytes_before += before
                stats.bytes_after += after
            elif status == "skipped":
                stats.skipped += 1
                stats.bytes_before += before
                stats.bytes_after += after
            elif status == "dry_run":
                stats.skipped += 1
                stats.bytes_before += before
            else:
                stats.failed += 1

            if idx % 500 == 0 or idx == total:
                elapsed = time.time() - started
                rate = idx / elapsed if elapsed > 0 else 0.0
                _emit(
                    progress,
                    f"[compress-tiles] {idx}/{total} "
                    f"converted={stats.converted} skipped={stats.skipped} "
                    f"failed={stats.failed} rate={rate:.0f}/s",
                )

    elapsed = time.time() - started
    before_mb = stats.bytes_before / 1024 / 1024
    after_mb = stats.bytes_after / 1024 / 1024
    saved_mb = before_mb - after_mb
    pct = (saved_mb / before_mb * 100) if before_mb > 0 else 0.0

    _emit(
        progress,
        f"[compress-tiles] done in {elapsed:.1f}s | "
        f"before={before_mb:.1f} MB after={after_mb:.1f} MB "
        f"saved={saved_mb:.1f} MB ({pct:.0f}%)",
    )
    return 0 if stats.failed == 0 else 1
