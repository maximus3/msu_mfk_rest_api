#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f init_master.sql

cp /etc/postgresql/pg_hba.conf /var/lib/postgresql/data/pgdata/pg_hba.conf
