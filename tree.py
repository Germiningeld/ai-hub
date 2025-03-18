import os


def print_tree(directory='.', exclude_dirs=[
    '.venv',
    '.idea',
    '__pycache__',
    '.git',
    '.pytest_cache',
    'node_modules',
    'alembic',
]):
    for root, dirs, files in os.walk(directory):
        # Исключаем нежелательные директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # Вычисляем уровень вложенности
        level = root.replace(directory, '').count(os.sep)

        # Корневую директорию выводим без отступов
        if level == 0:
            print(f"📁 {os.path.basename(root) or os.path.abspath(root)}")
        else:
            # Создаем префикс с отступами для текущего уровня
            prefix = '│   ' * (level - 1) + '├── '
            print(f"{prefix}📁 {os.path.basename(root)}")

        # Для файлов нужен дополнительный уровень отступа
        prefix = '│   ' * level

        # Выводим файлы
        for i, file in enumerate(sorted(files)):
            # Для последнего файла используем '└── ' вместо '├── '
            connector = '└── ' if i == len(files) - 1 else '├── '
            print(f"{prefix}{connector}📄 {file}")


# Запускаем функцию с текущей директорией
print_tree()