import re


def safe_filename(value: str) -> str:
    value = (value or '').strip().lower().replace(' ', '_')
    value = re.sub(r'[^0-9a-zA-Zа-яА-Я_-]+', '_', value)
    value = re.sub(r'_+', '_', value).strip('_')
    return value or 'database'
