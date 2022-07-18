import sys
import os


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir_content = os.listdir(BASE_DIR)
PROJECT_DIR_NAME = 'yatube_api'
# проверяем, что в корне репозитория лежит папка с проектом
if (
        PROJECT_DIR_NAME not in root_dir_content
        or not os.path.isdir(os.path.join(BASE_DIR, PROJECT_DIR_NAME))
):
    assert False, (
        f'В директории `{BASE_DIR}` не найдена папка c проектом `{PROJECT_DIR_NAME}`. '
        f'Убедитесь, что у вас верная структура проекта.'
    )

MANAGE_PATH = os.path.join(BASE_DIR, PROJECT_DIR_NAME)
project_dir_content = os.listdir(MANAGE_PATH)
FILENAME = 'manage.py'
# проверяем, что структура проекта верная, и manage.py на месте
if FILENAME not in project_dir_content:
    assert False, (
        f'В директории `{MANAGE_PATH}` не найден файл `{FILENAME}`. '
        f'Убедитесь, что у вас верная структура проекта.'
    )

pytest_plugins = [
    'tests.fixtures.fixture_user',
    'tests.fixtures.fixture_data',
]

# test .md
default_md = '# api_final\napi final\n'
filename = 'README.md'
assert filename in root_dir_content, (
    f'В корне проекта не найден файл `{filename}`'
)

with open(filename, 'r') as f:
    file = f.read()
    assert file != default_md, (
        f'Не забудьте оформить `{filename}`'
    )
