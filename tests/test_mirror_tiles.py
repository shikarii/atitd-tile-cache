from __future__ import annotations

import urllib.error
from pathlib import Path

import pytest

from atitd_tile_cache.tooling import mirror_tiles
from atitd_tile_cache.tooling.mirror_tiles import (
    MirrorTilesConfig,
    TileCoord,
    download_one,
    iter_tile_coords,
    run_mirror_tiles,
    tile_path,
)


def test_iter_tile_coords_counts_all_levels() -> None:
    coords = iter_tile_coords(0, 1)
    assert len(coords) == 5
    assert TileCoord(z=0, x=0, y=0) in coords
    assert TileCoord(z=1, x=1, y=1) in coords


def test_tile_path_layout() -> None:
    root = Path("cache")
    coord = TileCoord(z=3, x=4, y=5)
    expected = root / "tale10" / "3" / "4" / "5.png"
    assert tile_path(root, "tale10", coord) == expected


def test_download_one_returns_existing_for_cached_tile(tmp_path: Path) -> None:
    coord = TileCoord(z=0, x=0, y=0)
    existing = tile_path(tmp_path, "tale10", coord)
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_bytes(b"cached")

    status = download_one(
        base_url="https://example.com/maps",
        tale="tale10",
        output_root=tmp_path,
        coord=coord,
        timeout=1.0,
        retries=0,
        overwrite=False,
    )
    assert status == "existing"


def test_download_one_writes_tile_when_urlopen_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    coord = TileCoord(z=0, x=0, y=0)

    class FakeResponse:
        status = 200

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
            return False

        def read(self) -> bytes:
            return b"image-bytes"

    monkeypatch.setattr(
        mirror_tiles.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: FakeResponse(),
    )

    status = download_one(
        base_url="https://example.com/maps",
        tale="tale10",
        output_root=tmp_path,
        coord=coord,
        timeout=1.0,
        retries=0,
        overwrite=True,
    )
    assert status == "downloaded"
    assert tile_path(tmp_path, "tale10", coord).read_bytes() == b"image-bytes"


def test_download_one_returns_missing_on_404(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    coord = TileCoord(z=0, x=0, y=0)

    def _raise_404(*_args: object, **_kwargs: object) -> None:
        raise urllib.error.HTTPError(
            url="https://example.com/maps/tale10/0/0/0.png",
            code=404,
            msg="not found",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(mirror_tiles.urllib.request, "urlopen", _raise_404)
    status = download_one(
        base_url="https://example.com/maps",
        tale="tale10",
        output_root=tmp_path,
        coord=coord,
        timeout=1.0,
        retries=0,
        overwrite=True,
    )
    assert status == "missing"


def test_run_mirror_tiles_rejects_invalid_zoom_range() -> None:
    with pytest.raises(ValueError):
        run_mirror_tiles(MirrorTilesConfig(min_zoom=3, max_zoom=1), progress=None)


def test_run_mirror_tiles_reports_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mirror_tiles, "download_one", lambda *_args, **_kwargs: "failed")

    result = run_mirror_tiles(
        MirrorTilesConfig(
            output_dir=str(tmp_path),
            min_zoom=0,
            max_zoom=0,
            workers=1,
        ),
        progress=None,
    )
    assert result == 1
