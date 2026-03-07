from __future__ import annotations

import tarfile
from pathlib import Path

from atitd_tile_cache.tooling.release_tiles import BuildReleaseConfig, run_build_release


def test_build_release_creates_archive_and_checksum(tmp_path: Path) -> None:
    png = tmp_path / "tile_cache" / "tale10" / "0" / "0" / "0.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    png.write_bytes(b"fake-png")

    output_dir = tmp_path / "releases"
    exit_code = run_build_release(
        BuildReleaseConfig(
            tale="tale10",
            tile_cache_root=str(tmp_path / "tile_cache"),
            output_dir=str(output_dir),
        ),
        progress=None,
    )
    assert exit_code == 0

    archive = output_dir / "tile_cache_tale10.tar.gz"
    checksum = output_dir / "tile_cache_tale10.tar.gz.sha256"
    assert archive.exists()
    assert checksum.exists()

    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert "tale10/0/0/0.png" in names
