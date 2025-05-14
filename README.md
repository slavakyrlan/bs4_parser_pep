# Проект парсинга pep

## Оглавление

- [Описание](#Описание)
- [Технологии](#Технологии)
- [Запуск проекта](#Запуск-проекта)
- [Примеры команд](#Примеры-команд)
- [Автор](#Автор)



## Описание:

Модуль для парсинга HTML-страниц с использованием библиотеки BeautifulSoup.

Этот модуль содержит функции для выполнения HTTP-запросов, обработки ответов,
поиска HTML-тегов и создания объектов BeautifulSoup.

#### В проекте реализованы четыре парсера:

- whats-new - Парser, который обрабатывает статьи о новшествах в Python.
- latest_versions - Парсер, отслеживающий актуальный статус версии Python.
- download - Парсер, предназначенный для загрузки документации по Python.
- pep - Парсер, который работает с документацией [PEP](https://peps.python.org/).

## Технологии:

- Python 3.9.10
- BeautifulSoup4
- PrettyTable
- Logging

## Запуск проекта:

Клонируйте репозиторий и перейдите в директорию bs4_parser_pep:
```
git clone https://github.com/slavakyrlan/bs4_parser_pep

cd bs4_parser_pep
```
Создайте виртуальное окружение и активируйте его:
```
python -m venv vevn

source venv/Scripts/activate
```
Установите необходимые библиотеки для работы проекта:
```
pip install -r requirements.txt
```
Готово!

## Примеры команд
Команды вводим в директории ./src

Вывод справки (help):
```
python main.py -h
```
Список ссылок c обновлениями Python:
```
python main.py whats-new
```
Cкачивание архива с документацией актуальной версии Python:
```
python main.py download
```
Cписок ссылок на версии Python со статусами:
```
python main.py latest-versions
```
Информация по статусам и количеству PEP:
```
python main.py pep
```
Информация по статусам и количеству PEP c очитской кеша, вывод в виде таблицы:
```
python main.py pep -c -o pretty
```
Создает в папке results .csv файл с таблицей со статусами PEP:

```
python main.py pep -o file
```


## Автор

[Кырлан Вячеслав](https://github.com/slavakyrlan)
