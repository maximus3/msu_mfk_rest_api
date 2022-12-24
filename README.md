# REST API Service for Yandex Contest

## Description:
Service for manage courses using Yandex.Contest

## Описание

Данный проект представляет собой REST-API сервис для автоматического управления курсами, использующими систему автоматической проверки задач Yandex.Contest.

Спецификация API доступна в файле [openapi.json](openapi.json).

### Основные возможности

* Регистрация студентов на курс (ручка /api/v1/register)
* Добавление нового контеста в курс (ручка /api/v1/contest)
* Получение информации о доступных курсах (ручка /api/v1/course)
* Получение результатов студентов по логину (ручка api/v1/results/all/{student_login})
* Автоматическое добавление студентов в контесты
* Автоматический парсинг результатов студентов

### Структура проекта

Проект состоит из четырех контейнеров:
    
* Контейнер с базой данных PostgreSQL
* Контейнер с nginx
* Контейнер с REST-API сервисом
* Контейнер с автоматическими скриптами

### Запуск проекта

Для запуска проекта необходимо выполнить следующие команды:

    make docker

Данная команда запускает все контейнеры, необходимые для работы проекта.

Если необходимо обновить код на сервере из git, то на сервере необходимо выполнить команду:

    make update

Ниже представлены все команды, которые также можно получить через `make help`.

## Команды

`Usage: make [target] ...`

### Help

* `help` - Show this help.

### Database

* `migrate` - Do all migrations in database
* `revision` - Create new revision file automatically with prefix (ex. 2022_01_01_14cs34f_message.py)
* `downgrade` - Downgrade migration on one revision
* `db` - Docker up db
* `dump` - Dump database from server
* `dump-local` - Dump database local
* `restore-local` - Restore database local
* `restore-server` - Restore database on server

### Git

* `commit` - Commit with message all files
* `push` - Push to origin
* `pull` - Pull from origin
* `git` - Check and commit

### Testing

* `test` - Runs pytest with coverage
* `test-fast` - Runs pytest with exitfirst
* `test-failed` - Runs pytest from last-failed
* `test-cov` - Runs pytest with coverage report
* `test-mp` - Runs pytest with multiprocessing
* `test-fast-mp` - Runs pytest with exitfirst with multiprocessing
* `test-failed-mp` - Runs pytest from last-failed with multiprocessing
* `test-cov-mp` - Runs pytest with coverage report with multiprocessing

### Code

* `install` - Install dependencies
* `install-prod` - Install dependencies for production only
* `poetry-add` - Add new dependency
* `format` - Formats all files
* `lint` - Lint code
* `check` - Format and lint code then run tests

### Application

* `up` - Up App
* `up-scheduler` - Up Scheduler
* `docker-up` - Docker up
* `docker-up-d` - Docker up detach
* `docker-build` - Docker build
* `docker-up-build` - Docker up detach with build
* `docker-down` - Docker down
* `docker-stop` - Docker stop some app
* `docker-clean` - Docker prune -f
* `docker` - Docker prune, up, run and prune
* `open` - Open container in docker
* `docker-migrate` - Migrate db in docker
* `update` - Update docker app
* `update-server` - Update docker app on server 
* `docker-clear-logs` - Clear logs
* `get-scheduler-logs` - Get scheduler logs

### Server

* `connect` - Connect to server

### Environment

* `env` - Create .env file with variables
* `venv` - Create virtual environment, no need in docker

### File

* `file-copy` - Copy file from server