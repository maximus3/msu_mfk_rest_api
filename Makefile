ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

VENV = .venv
ifeq ($(OS),Windows_NT)
    PYTHON_EXECUTABLE = python
    VENV_BIN = $(VENV)/Scripts
else
    PYTHON_EXECUTABLE = python3
    VENV_BIN = $(VENV)/bin
endif

POETRY_VERSION=1.2
POETRY_RUN = $(VENV_BIN)/poetry run

# Manually define main variables

APPLICATION_NAME = app

ifndef APP_PORT
override APP_PORT = 8090
endif

ifndef APP_HOST
override APP_HOST = 127.0.0.1
endif

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

TEST = $(POETRY_RUN) pytest --verbosity=2 --showlocals --log-level=DEBUG
CODE = $(APPLICATION_NAME) tests

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands

.PHONY: help
help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)


.PHONY: env
env:  ##@Environment Create .env file with variables
	@$(eval SHELL:=/bin/bash)
	@cp .env.example .env
	@echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env


.PHONY: venv
venv: ##@Environment Create virtual environment, no need in docker
	$(PYTHON_EXECUTABLE) -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade pip
	$(VENV_BIN)/python -m pip install poetry==$(POETRY_VERSION)
	$(VENV_BIN)/poetry config virtualenvs.create true
	$(VENV_BIN)/poetry config virtualenvs.in-project true


.PHONY: install
install: ##@Code Install dependencies
	$(VENV_BIN)/poetry install --no-interaction --no-ansi


.PHONY: install-prod
install-prod: ##@Code Install dependencies for production
	$(VENV_BIN)/poetry install --without dev --no-interaction --no-ansi


.PHONY: poetry-add
poetry-add: ##@Code Add new dependency
	$(VENV_BIN)/poetry add $(args)


.PHONY: up
up: ##@Application Up App
	$(POETRY_RUN) python -m app


.PHONY: up-scheduler
up-scheduler: ##@Application Up Scheduler
	$(POETRY_RUN) python -m app.scheduler

.PHONY: migrate
migrate:  ##@Database Do all migrations in database
	$(POETRY_RUN) alembic upgrade $(args)

.PHONY: revision
revision:  ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_14cs34f_message.py)
	$(POETRY_RUN) alembic revision --autogenerate

.PHONY: downgrade
downgrade:  ##@Database Downgrade migration on one revision
	alembic downgrade -1

.PHONY: db
db: ##@Database Docker up db
	docker-compose up -d postgres

.PHONY: test
test: ##@Testing Runs pytest with coverage
	$(POETRY_RUN) pytest tests/app/endpoints/v1/test_ping.py::TestHealthCheckHandler::test_ping_database
	$(TEST) --cov

.PHONY: test-fast
test-fast: ##@Testing Runs pytest with exitfirst
	$(TEST) --exitfirst

.PHONY: test-failed
test-failed: ##@Testing Runs pytest from last-failed
	$(TEST) --last-failed

.PHONY: test-cov
test-cov: ##@Testing Runs pytest with coverage report
	$(TEST) --cov --cov-report html

.PHONY: test-mp
test-mp: ##@Testing Runs pytest with multiprocessing
	$(POETRY_RUN) pytest tests/app/endpoints/v1/test_ping.py::TestHealthCheckHandler::test_ping_database
	$(TEST) --cov -n auto

.PHONY: test-fast-mp
test-fast-mp: ##@Testing Runs pytest with exitfirst with multiprocessing
	$(TEST) --exitfirst -n auto

.PHONY: test-failed-mp
test-failed-mp: ##@Testing Runs pytest from last-failed with multiprocessing
	$(TEST) --last-failed -n auto

.PHONY: test-cov-mp
test-cov-mp: ##@Testing Runs pytest with coverage report with multiprocessing
	$(TEST) --cov --cov-report html -n auto

.PHONY: format
format: ###@Code Formats all files
	$(POETRY_RUN) autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(POETRY_RUN) isort $(CODE)
	$(POETRY_RUN) black --line-length 79 --target-version py310 --skip-string-normalization $(CODE)
	$(POETRY_RUN) unify --in-place --recursive $(CODE)

.PHONY: lint
lint: ###@Code Lint code
	$(POETRY_RUN) flake8 --jobs 4 --statistics --show-source $(CODE)
	$(POETRY_RUN) pylint $(CODE)
	$(POETRY_RUN) mypy $(CODE)
	$(POETRY_RUN) black --line-length 79 --target-version py310 --skip-string-normalization --check $(CODE)
	$(POETRY_RUN) pytest --dead-fixtures --dup-fixtures
	$(POETRY_RUN) safety check --full-report || echo "Safety check failed"

.PHONY: check
check: format lint test-mp ###@Code Format and lint code then run tests

.PHONY: docker-up
docker-up: ##@Application Docker up
	docker-compose up --remove-orphans

.PHONY: docker-up-d
docker-up-d: ##@Application Docker up detach
	docker-compose up -d --remove-orphans

.PHONY: docker-build
docker-build: ##@Application Docker build
	docker-compose build

.PHONY: docker-up-build
docker-up-build: ##@Application Docker up detach with build
	docker-compose up -d --build --remove-orphans

.PHONY: docker-down
docker-down: ##@Application Docker down
	docker-compose down

.PHONY: docker-stop
docker-stop: ##@Application Docker stop some app
	docker-compose stop $(args)

.PHONY: docker-clean
docker-clean: ##@Application Docker prune -f
	docker image prune -f

.PHONY: docker
docker: docker-clean docker-build docker-up-d docker-clean ##@Application Docker prune, up, run and prune

.PHONY: open
open: ##@Application Open container in docker
	docker exec -it $(args) /bin/bash

.PHONY: docker-migrate
docker-migrate: ##@Application Migrate db in docker
	docker exec app make migrate $(args)

.PHONY: commit
commit: format ##@Git Commit with message all files
	@git add .
	@git status
	$(eval MESSAGE := $(shell read -p "Commit message: " MESSAGE; echo $$MESSAGE))
	@git commit -m "$(MESSAGE)"

.PHONY: push
push: ##@Git Push to origin
	@git push

.PHONY: pull
pull: ##@Git Pull from origin
	@git pull

.PHONY: check-git
git: check commit ##@Git Check and commit

.PHONY: update
update: pull dump-local ##@Application Update docker app
	@make docker-stop nginx
	@make docker
	@make docker-migrate head

.PHONY: dump
dump: ##@Database Dump database from server
	$(eval FILENAME=backup_$(shell date +%Y%m%d_%H%M%S).sql)
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	$(eval DB_NAME=$(shell cat deploy/db_name.txt))
	$(eval DB_USERNAME=$(shell cat deploy/db_username.txt))

	echo "Dumping database to $(FILENAME)"
	ssh -p $(PORT) $(USERNAME)@$(HOST) "docker exec postgres_container pg_dump -f $(FILENAME) -d $(DB_NAME) -U $(DB_USERNAME);docker cp postgres_container:$(FILENAME) $(FILENAME);docker exec postgres_container rm $(FILENAME);exit;"
	scp -P $(PORT) $(USERNAME)@$(HOST):$(FILENAME) db/$(FILENAME)
	ssh -p $(PORT) $(USERNAME)@$(HOST) "rm $(FILENAME); exit;"
	echo "Done"

.PHONY: dump-local
dump-local: ##@Database Dump database local
	$(eval FILENAME=backup_$(shell date +%Y%m%d_%H%M%S).sql)

	echo "Dumping database to $(FILENAME)"
	docker exec postgres_container pg_dump -f $(FILENAME) -d $(POSTGRES_DB) -U $(POSTGRES_USER)
	docker cp postgres_container:$(FILENAME) db/$(FILENAME)
	docker exec postgres_container rm $(FILENAME)
	echo "Done"

.PHONY: connect
connect: ##@Server Connect to server
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	ssh -p $(PORT) $(USERNAME)@$(HOST)

%::
	echo $(MESSAGE)
