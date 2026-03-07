"""Build release artifacts from local tile cache content."""

from __future__ import annotations

import dataclasses
import hashlib
import tarfile
import tempfile
from collections.abc import Callable
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class BuildReleaseConfig:
    tale: str = "tale10"
    tile_cache_root: str = str((Path.cwd() / "tile_cache").resolve())
    output_dir: str = str((Path(tempfile.gettempdir()) / "atitd-tile-cache" / "releases").resolve())
    asset_name_template: str = "tile_cache_{tale}.tar.gz"


def _emit(progress: Callable[[str], None] | None, message: str) -> None:
    if progress is not None:
        progress(message)


def _sha256_for(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_build_release(
    config: BuildReleaseConfig,
    progress: Callable[[str], None] | None = print,
) -> int:
    cache_root = Path(config.tile_cache_root).resolve()
    tale_dir = cache_root / config.tale
    if not tale_dir.exists():
        _emit(progress, f"[tile-release] ERROR: missing tale directory: {tale_dir}")
        return 1

    output_dir = Path(config.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    asset_name = config.asset_name_template.format(tale=config.tale)
    archive_path = output_dir / asset_name
    checksum_path = output_dir / f"{asset_name}.sha256"

    _emit(progress, f"[tile-release] packaging {tale_dir} -> {archive_path}")
    with tarfile.open(archive_path, mode="w:gz") as tar:
        tar.add(tale_dir, arcname=config.tale)

    checksum = _sha256_for(archive_path)
    checksum_path.write_text(f"{checksum}  {archive_path.name}\n", encoding="utf-8")
    _emit(progress, f"[tile-release] wrote {checksum_path}")
    _emit(progress, f"[tile-release] SHA256={checksum}")
    return 0
