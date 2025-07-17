import os
import platform
from pathlib import Path
import zstandard as zstd

ZSTD_DICT_URL = "https://raw.githubusercontent.com/bluesky-social/jetstream/main/pkg/models/zstd_dictionary"


def get_cache_directory(app_name: str) -> Path:
    if platform.system() == "Windows":
        base_cache_dir = os.getenv(
            "LOCALAPPDATA", Path.home() / "AppData" / "Local")
    else:
        base_cache_dir = os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")
    cache_dir = Path(base_cache_dir) / app_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def download_zstd_dict(zstd_dict_path: Path):
    import httpx
    with httpx.stream("GET", ZSTD_DICT_URL) as response:
        with zstd_dict_path.open("wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)


def get_zstd_decompressor() -> zstd.ZstdDecompressor:
    cache_dir = get_cache_directory("jetstream")
    cache_dir.mkdir(parents=True, exist_ok=True)
    zstd_dict_path = cache_dir / "zstd_dict.bin"
    if not zstd_dict_path.exists():
        download_zstd_dict(zstd_dict_path)
    with zstd_dict_path.open("rb") as f:
        zstd_dict = f.read()
    dict_data = zstd.ZstdCompressionDict(zstd_dict)
    return zstd.ZstdDecompressor(dict_data=dict_data)
