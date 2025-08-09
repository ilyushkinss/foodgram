[![Workflow main status](https://github.com/arefiture/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/arefiture/foodgram/actions)

![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Описание проекта

Foodgram - это сайт, позволяющий пользователям создавать и делиться своими рецептами, подписываться на других людей, и много чего еще. В общем, как маленькая социальная сеть для любителей кулинарии!

## Технологии

- Python 3.9
- Django 3.2.3
- Django REST framework 3.12.4
- JavaScript
- Postgres
- Docker
- Nginx

## Запуск проекта из образов с Docker Hub

При первом запуске убедитесь, что Docker работает.

Скачиваем файл `docker-compose.production.yml` из репозитория https://github.com/ilyushkinss/foodgram/tree/main и запускаем его:

```bash
sudo docker compose -f docker-compose.production.yml up -d
```

Далее автоматически скачаются образы, произойдет создание и включение контейнеров и объедение их в одну сеть.

## Настройки переменных окружения (о том, как заполнить env)

В корне проекта необходимо создать файл .env и заполнить по образцу из файла .env.example

## После запуска: Миграции, сбор статистики

После запуска необходимо выполнить сбор статики и миграции бэкенда.
Статика фронтенда собирается во время запуска контейнера, после чего он останавливается. 

```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic

sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

После этого проект будет доступен по адресам:
```
localhost:8080
127.0.0.1:8080
```

## Если нужно наполнение тегами и ингредиентами:

```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py data_loader
```

## Остановка проекта:

```bash
sudo docker compose -f docker-compose.production.yml down
```

## Проект доступен по адресу

https://ilyushkins-foodgram.zapto.org/recipes

## Автор

Гильманов Илья
