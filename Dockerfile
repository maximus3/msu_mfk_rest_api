FROM python:3.10-slim

# Don't periodically check PyPI to determine whether a new version of pip is available for download.
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
# Disable package cache.
ENV PIP_NO_CACHE_DIR=off
# Python won't try to write .pyc files on the import of source modules.
ENV PYTHONDONTWRITEBYTECODE=on
# install a handler for SIGSEGV, SIGFPE, SIGABRT, SIGBUS and SIGILL signals to dump the Python traceback
ENV PYTHONFAULTHANDLER=on
# Force the stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED=on
# set workdir as PYTHONPATH
ENV PYTHONPATH=/opt/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget gnupg

# for pg_dump
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get install -y postgresql-client-14

RUN apt-get autoclean && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt/app

COPY pyproject.toml poetry.loc[k] /opt/app/

COPY Makefile Makefile

RUN make venv
RUN make install-prod

COPY setup.cfg setup.cfg
COPY alembic.ini alembic.ini
COPY log.ini log.ini
COPY config.yaml config.yaml

COPY app app
COPY static static
COPY tools tools

ENTRYPOINT []
CMD ["make", "up"]