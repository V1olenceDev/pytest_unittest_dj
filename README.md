# Django Testing

> Проект представляет собой тестирование двух Django приложений: `ya_news` и `ya_note` с использованием двух различных подходов к тестированию — `pytest` и `unittest`.

## Технологии проекта

- Django — веб-фреймворк для разработки веб-приложений.
- Pytest — фреймворк для тестирования на языке Python.
- Unittest — стандартная библиотека для модульного тестирования в Python.
- Docker — платформа для автоматизации развёртывания приложений в контейнерах.

## Структура репозитория:

```
Dev
 └── django_testing
     ├── ya_news
     │   ├── news
     │   │   ├── fixtures/
     │   │   ├── migrations/
     │   │   ├── pytest_tests/   <- Директория с тестами pytest для проекта ya_news
     │   │   ├── __init__.py
     │   │   ├── admin.py
     │   │   ├── apps.py
     │   │   ├── forms.py
     │   │   ├── models.py
     │   │   ├── urls.py
     │   │   └── views.py
     │   ├── templates/
     │   ├── yanews/
     │   ├── manage.py
     │   └── pytest.ini
     ├── ya_note
     │   ├── notes
     │   │   ├── migrations/
     │   │   ├── tests/          <- Директория с тестами unittest для проекта ya_note
     │   │   ├── __init__.py
     │   │   ├── admin.py
     │   │   ├── apps.py
     │   │   ├── forms.py
     │   │   ├── models.py
     │   │   ├── urls.py
     │   │   └── views.py
     │   ├── templates/
     │   ├── yanote/
     │   ├── manage.py
     │   └── pytest.ini
     ├── .gitignore
     ├── README.md
     ├── requirements.txt
     └── structure_test.py
```

### Как запустить проект:

Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone git@github.com:V1olenceDev/bs4_parser_pep.git
```

```
cd bs4_parser_pep
```

Cоздайте и активируйте виртуальное окружение:

```
python -m venv venv
```

```
. venv/Scripts/activate
```

Установите зависимости из файла `requirements.txt`:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
    
Запустить скрипт `run_tests.sh` из корневой директории проекта:
   
```
bash run_tests.sh
```

## Автор
[Гаспарян Валерий Гургенович](https://github.com/V1olenceDev)
