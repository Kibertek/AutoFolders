from pathlib import Path
from datetime import datetime, timedelta
import json
import shutil


CONFIG_FILE = Path("config.json")
LOG_FILE = Path("log.txt")


def write_log(message):
    """Записывает сообщение в журнал."""

    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{current_time}] {message}\n")

    print(message)


def load_config():
    """Загружает настройки из config.json."""

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "Файл config.json не найден."
        )

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    return config


def is_folder_empty(folder):
    """Проверяет, пустая ли папка."""

    return not any(folder.iterdir())


def check_previous_folder(base_folder, today):
    """
    Проверяет папку предыдущего дня.

    Если папка пустая — удаляет её.
    Если в ней есть файлы или другие папки — оставляет.
    """

    previous_day = today - timedelta(days=1)

    year = previous_day.strftime("%Y")
    date = previous_day.strftime("%d.%m.%Y")

    previous_folder = base_folder / year / date

    # Если папки предыдущего дня нет
    if not previous_folder.exists():
        write_log(
            f"Папка предыдущего дня отсутствует: "
            f"{previous_folder}"
        )
        return

    # Проверяем пустая ли папка
    if is_folder_empty(previous_folder):

        try:
            previous_folder.rmdir()

            write_log(
                f"Удалена пустая папка: "
                f"{previous_folder}"
            )

        except Exception as error:

            write_log(
                f"Не удалось удалить папку "
                f"{previous_folder}: {error}"
            )

    else:

        write_log(
            f"Папка предыдущего дня содержит данные, "
            f"оставляем: {previous_folder}"
        )


def create_today_folder():
    """Проверяет предыдущую папку и создаёт папку сегодняшней даты."""

    config = load_config()

    base_folder = Path(config["base_folder"])
    date_format = config["date_format"]

    today = datetime.now()

    # Сначала проверяем вчерашнюю папку
    check_previous_folder(
        base_folder,
        today
    )

    # Определяем текущий год
    year = today.strftime("%Y")

    # Определяем сегодняшнюю дату
    date = today.strftime(date_format)

    # Папка текущего года
    year_folder = base_folder / year

    # Папка сегодняшней даты
    today_folder = year_folder / date

    # Создаём папку года
    year_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # Создаём папку сегодняшнего дня
    if today_folder.exists():

        write_log(
            f"Папка уже существует: "
            f"{today_folder}"
        )

    else:

        today_folder.mkdir()

        write_log(
            f"Создана новая папка: "
            f"{today_folder}"
        )


def main():

    write_log("========================================")
    write_log("Запуск программы.")

    try:

        create_today_folder()

    except Exception as error:

        write_log(
            f"ОШИБКА: {error}"
        )

    write_log("Работа программы завершена.")
    write_log("========================================")


if __name__ == "__main__":
    main()
