
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging


# ==========================================
# ПУТИ К ФАЙЛАМ ПРОГРАММЫ
# ==========================================

# Папка, в которой находится сам скрипт
APP_FOLDER = Path(__file__).resolve().parent

CONFIG_FILE = APP_FOLDER / "config.json"
LOG_FILE = APP_FOLDER / "log.txt"


# ==========================================
# НАСТРОЙКА ЖУРНАЛА
# ==========================================

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    encoding="utf-8"
)


def write_log(message):
    """Записывает сообщение в журнал и выводит его в консоль."""

    logging.info(message)
    print(message)


# ==========================================
# ЗАГРУЗКА НАСТРОЕК
# ==========================================

def load_config():
    """Читает настройки из config.json."""

    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(
            f"Не найден файл настроек: {CONFIG_FILE}"
        )

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    if not config.get("base_folder"):
        raise ValueError(
            "В config.json не указан base_folder."
        )

    if not config.get("date_format"):
        raise ValueError(
            "В config.json не указан date_format."
        )

    return config


# ==========================================
# ПРОВЕРКА ПУСТОТЫ ПАПКИ
# ==========================================

def is_folder_empty(folder):
    """Возвращает True, если папка не содержит файлов и подпапок."""

    try:
        with os_scandir(folder) as entries:
            return next(entries, None) is None

    except OSError as error:
        write_log(
            f"Не удалось проверить содержимое {folder}: {error}"
        )
        return False


def os_scandir(folder):
    """Возвращает итератор содержимого папки."""

    import os
    return os.scandir(folder)


# ==========================================
# ПРОВЕРКА ПРЕДЫДУЩЕЙ ПАПКИ
# ==========================================

def check_previous_folder(base_folder, today, date_format):
    """
    Проверяет папку предыдущего календарного дня.

    Пустая папка удаляется.
    Папка с файлами или подпапками сохраняется.
    """

    previous_day = today - timedelta(days=1)

    year_folder = base_folder / previous_day.strftime("%Y")
    date_folder = year_folder / previous_day.strftime(date_format)

    if not date_folder.exists():
        write_log(
            f"Папка предыдущего дня отсутствует: {date_folder}"
        )
        return

    if not date_folder.is_dir():
        write_log(
            f"Путь предыдущего дня не является папкой: {date_folder}"
        )
        return

    if is_folder_empty(date_folder):
        try:
            # Удаляет только пустую папку
            date_folder.rmdir()

            write_log(
                f"Удалена пустая папка: {date_folder}"
            )

        except OSError as error:
            write_log(
                f"Не удалось удалить пустую папку "
                f"{date_folder}: {error}"
            )

    else:
        write_log(
            f"Папка содержит данные, оставляем: {date_folder}"
        )


# ==========================================
# СОЗДАНИЕ ПАПКИ СЕГОДНЯШНЕГО ДНЯ
# ==========================================

def create_today_folder():
    """Проверяет сетевой ресурс и создаёт папку текущей даты."""

    config = load_config()

    base_folder = Path(config["base_folder"])
    date_format = config["date_format"]

    # Проверяем, доступен ли сетевой ресурс
    if not base_folder.is_dir():
        write_log(
            f"ОШИБКА: сетевой путь недоступен: {base_folder}"
        )
        return

    today = datetime.now()

    # Сначала проверяем папку предыдущего дня
    check_previous_folder(
        base_folder,
        today,
        date_format
    )

    year_folder = base_folder / today.strftime("%Y")
    today_folder = year_folder / today.strftime(date_format)

    # Создаём папку года при необходимости
    year_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # Создаём папку даты, если её ещё нет
    if today_folder.exists():
        if today_folder.is_dir():
            write_log(
                f"Папка уже существует: {today_folder}"
            )
        else:
            write_log(
                f"ОШИБКА: путь занят файлом: {today_folder}"
            )
    else:
        today_folder.mkdir()

        write_log(
            f"Создана новая папка: {today_folder}"
        )


# ==========================================
# ЗАПУСК ПРОГРАММЫ
# ==========================================

def main():
    write_log("=" * 50)
    write_log("Запуск программы автоматических папок.")

    try:
        create_today_folder()

    except Exception:
        logging.exception("Критическая ошибка программы.")
        print(
            "Произошла ошибка. Подробности находятся в log.txt."
        )

    write_log("Работа программы завершена.")
    write_log("=" * 50)


if __name__ == "__main__":
    main()