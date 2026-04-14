import yaml
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "target_folder": "~/Downloads",
    "rules": {
        "Images": [".jpg", ".jpeg", ".png", ".gif"],
        "Documents": [".pdf", ".docx", ".txt"],
        "Installers": [".exe", ".msi", ".dmg"],
        "Archives": [".zip", ".rar", ".7z"]
    },
    "archive_old_days": 30,  # Архивировать файлы старше 30 дней
    "log_file": "organizer.log"
}


def load_config(config_path: str) -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        # Если конфига нет, создаем дефолтный
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(DEFAULT_CONFIG, f)
        return DEFAULT_CONFIG

    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)