import shutil
import logging
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)


def get_file_category(file_ext: str, rules: Dict[str, List[str]]) -> str:
    """Определяет категорию файла по расширению."""
    file_ext = file_ext.lower()
    for category, extensions in rules.items():
        if file_ext in extensions:
            return category
    return "Other"


def generate_unique_path(dest_path: Path) -> Path:
    """Если файл существует, добавляет таймштамп к имени."""
    if not dest_path.exists():
        return dest_path

    stem = dest_path.stem
    suffix = dest_path.suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{stem}_{timestamp}{suffix}"
    return dest_path.with_name(new_name)


def organize_files(source_dir: Path, rules: Dict[str, List[str]], dry_run: bool = False):
    """Сортирует файлы по папкам."""
    moved_count = 0

    for file_path in source_dir.iterdir():
        if file_path.is_file() and not file_path.name.startswith('.'):
            # Игнорируем сам скрипт и логи, если они в папке загрузок
            if file_path.name in ['organizer.log', 'config.yaml']:
                continue

            category = get_file_category(file_path.suffix, rules)
            target_dir = source_dir / category
            dest_path = target_dir / file_path.name
            dest_path = generate_unique_path(dest_path)

            action = f"Move {file_path.name} -> {dest_path}"

            if dry_run:
                logger.info(f"[DRY-RUN] {action}")
            else:
                target_dir.mkdir(exist_ok=True)
                try:
                    shutil.move(str(file_path), str(dest_path))
                    logger.info(f"{action}")
                    moved_count += 1
                except Exception as e:
                    logger.error(f"Failed to move {file_path.name}: {e}")

    return moved_count


def archive_old_files(source_dir: Path, days: int, dry_run: bool = False):
    """Сжимает файлы, старше указанного количества дней, в один архив."""
    cutoff_time = datetime.now() - timedelta(days=days)
    files_to_archive = []

    for file_path in source_dir.iterdir():
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time.timestamp():
            files_to_archive.append(file_path)

    if not files_to_archive:
        return 0

    archive_name = source_dir / f"old_files_{datetime.now().strftime('%Y%m%d')}"

    if dry_run:
        logger.info(f"[DRY-RUN] Would archive {len(files_to_archive)} files to {archive_name}.zip")
        return len(files_to_archive)

    try:
        with zipfile.ZipFile(f"{archive_name}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_archive:
                zipf.write(file_path, arcname=file_path.name)
                file_path.unlink()  # Удаляем оригинал после архивации

        logger.info(f"Archived {len(files_to_archive)} files to {archive_name}.zip")
        return len(files_to_archive)
    except Exception as e:
        logger.error(f"Failed to archive files: {e}")
        return 0