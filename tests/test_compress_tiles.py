from __future__ import annotations

from pathlib import Path

from PIL import Image

from atitd_tile_cache.tooling.compress_tiles import CompressTilesConfig, run_compress_tiles


def _write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), color=(100, 180, 40)).save(path, format="PNG")


def test_compress_tiles_dry_run_does_not_write_webp(tmp_path: Path) -> None:
    tile = tmp_path / "tile_cache" / "tale10" / "0" / "0" / "0.png"
    _write_png(tile)

    exit_code = run_compress_tiles(
        CompressTilesConfig(
            tile_cache_dir=str(tmp_path / "tile_cache"),
            dry_run=True,
        ),
        progress=None,
    )
    assert exit_code == 0
    assert not tile.with_suffix(".webp").exists()


def test_compress_tiles_writes_webp(tmp_path: Path) -> None:
    tile = tmp_path / "tile_cache" / "tale10" / "0" / "0" / "0.png"
    _write_png(tile)

    exit_code = run_compress_tiles(
        CompressTilesConfig(
            tile_cache_dir=str(tmp_path / "tile_cache"),
            quality=80,
            workers=1,
        ),
        progress=None,
    )
    assert exit_code == 0
    assert tile.with_suffix(".webp").exists()
