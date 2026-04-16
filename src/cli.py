import click
import logging
from pathlib import Path
import sys
import os

# Добавляем src в path, чтобы импорты работали при запуске
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import load_config
from src.core import organize_files, archive_old_files


def setup_logging(log_file: str):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


@click.command()
@click.option('--config', default='config.yaml', help='Путь к файлу конфигурации.')
@click.option('--dry-run', is_flag=True, help='Режим проверки (без реальных изменений).')
@click.option('--archive', is_flag=True, help='Включить архивацию старых файлов.')
def main(config, dry_run, archive):
    """Умный органайзер папки Загрузки."""
    conf = load_config(config)

    # Настройка логирования
    log_path = Path(conf.get('log_file', 'organizer.log'))
    # Если лог не в той же папке, делаем абсолютный путь
    if not log_path.is_absolute():
        log_path = Path.cwd() / log_path

    setup_logging(str(log_path))

    target_folder = Path(conf['target_folder']).expanduser()

    if not target_folder.exists():
        click.echo(f"Ошибка: Папка {target_folder} не найдена.")
        return

    click.echo(f"Сканирование папки: {target_folder}")
    if dry_run:
        click.echo("!!! РЕЖИМ DRY-RUN (Изменения не будут сохранены) !!!")

    # 1. Сортировка
    moved = organize_files(target_folder, conf['rules'], dry_run)
    click.echo(f"Файлов отсортировано: {moved}")

    # 2. Архивация (опционально)
    if archive:
        days = conf.get('archive_old_days', 30)
        archived = archive_old_files(target_folder, days, dry_run)
        click.echo(f"Файлов заархивировано: {archived}")


if __name__ == '__main__':
    main()