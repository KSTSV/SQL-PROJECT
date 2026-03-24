from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / 'data'
STATIC_DIR = BASE_DIR / 'app' / 'static'


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def ensure_static_dir() -> Path:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    return STATIC_DIR
