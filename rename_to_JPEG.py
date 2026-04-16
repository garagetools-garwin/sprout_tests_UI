import os
import sys

def get_script_directory():
    """
    Определяет папку, в которой лежит .exe / .py файл.
    Работает корректно и для обычного .py, и для собранного .exe
    """
    if getattr(sys, 'frozen', False):
        # Запущен как .exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Запущен как .py
        return os.path.dirname(os.path.abspath(__file__))


def rename_to_jpeg(folder_path):
    files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Исключаем сам .exe из списка
    exe_name = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else None
    if exe_name:
        files = [f for f in files if f != exe_name]

    if not files:
        print("В папке нет файлов для переименования.")
        return

    renamed = 0
    skipped = 0

    for filename in files:
        old_path = os.path.join(folder_path, filename)
        name, ext = os.path.splitext(filename)

        if ext.lower() == ".jpeg":
            print(f"  [ПРОПУСК] {filename} (уже .jpeg)")
            skipped += 1
            continue

        if not name or name.startswith("."):
            print(f"  [ПРОПУСК] {filename} (скрытый/служебный)")
            skipped += 1
            continue

        new_filename = name + ".jpeg"
        new_path = os.path.join(folder_path, new_filename)

        if os.path.exists(new_path):
            print(f"  [ПРОПУСК] {filename} -> {new_filename} уже существует")
            skipped += 1
            continue

        os.rename(old_path, new_path)
        print(f"  [OK] {filename} -> {new_filename}")
        renamed += 1

    print(f"\nГотово! Переименовано: {renamed}, пропущено: {skipped}")


def main():
    folder = get_script_directory()

    print("=" * 50)
    print("  Переименование файлов в .jpeg")
    print("=" * 50)
    print(f"\nРабочая папка: {folder}")
    print(f"Файлов найдено: {len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])}")
    print()

    confirm = input("Переименовать все файлы в .jpeg? (да/нет): ").strip().lower()

    if confirm in ("да", "yes", "y", "д"):
        print()
        rename_to_jpeg(folder)
    else:
        print("Отменено.")

    print()
    input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
