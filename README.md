![foodgram_workflow](https://github.com/deorz/foodgram_project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

# Yandex Foodgram

---

## Описание:

Проект агрегатора рецептов / дипломный проект Яндекс.Практикум

На этом сайте можно хранить все свои рецепты и просматривать рецепты других
пользователей. Также реализован сервис подписки на пользователей и добавление
рецептов в избранное, чтобы любимые рецепты были всегда под рукой

Его можно найти тут: [Yandex Foodgram](http://84.201.161.35/)

---

### Стэк используемых технологий:

#### Backend:
- Python 3.8.9
- Django Framework 4.1 
- Django Rest Framework 3.13.1

#### Infrastructure:
- Docker
- Nginx for docker
- PostgreSQL DB in Docker

#### Frontend:
- React

---
### Установка на удалённом сервере:

#### Необходимые зависимости на сервере:

- docker.io
```shell
sudo apt install docker.io
```
- docker-compose
```shell
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

1. Склонируйте репозиторий на сервер:

   ```shell
   git clone https://github.com/deorz/foodgram-project-react.git
   ```
   
1. Перейдите в папку infra:
```bash
├── backend
├── docs
├── frontend
├── infra
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── README.md
└── .gitignore
```

1. Создайте .env файл, куда поместите все переменные окружения:
   ```shell
   ├── infra
       ├── .env
       ├── docker-compose.yml
       └── nginx.conf
   ```

   ```
   SECRET_KEY=<DJANGO_APP_SECRET_KEY>
   HOST=<YOUR_DB_SERVER_HOST>
   ...
   DB_NAME=<YOUR_DB_NAME>
   ```

1. Внесите изменения в файл nginx.conf:
   ```shell
   server_name <имя вашего сервера/ip вашего сервера>;
   ```

1. Запустите сборку контейнеров командой:

   ```shell
   docker-compose up -d --build
   ```

   - Примените миграции внутри контейнера:

      ```shell
      docker-compose exec <Имя контейнера с бэкендом> python manage.py migrate
      ```

   - Примените команду для сборки статики в одну директорию, из которой 
   она будет раздаваться веб-сервером Nginx:

      ```shell
      docker-compose exec <Имя контейнера с бэкендом> collectstatic --no-input
      ```
   - Примените команду для загрузки ReadOnly данных в БД:

     ```shell
        docker-compose exec <Имя контейнера с бэкендом> python manage.py load_default_data
     ```

---

#### Для того, чтобы посмотреть исходники API перейдите по URL:
   ```
   http://<server_url>/api/docs/   
   ```

---

### Если вы хотите отключить контейнер и отменить все изменения:

   ```shell
   docker-compose down -v
   ```

### Приятного пользования!

------

Author: [deorz](https://github.com/deorz/)