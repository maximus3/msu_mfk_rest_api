#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f init_master.sql

pg_basebackup -D /postgresslave/pgdata -S replication_slot_slave1 -X stream -P -U replicator -Fp -R

echo "# Do not edit this file manually!
# It will be overwritten by the ALTER SYSTEM command.
primary_conninfo = 'host=127.0.0.1 port=5432 user=replicator password=$POSTGRES_REPLICATOR_PASSWORD'
primary_slot_name = 'replication_slot_proxy_slave1'
restore_command = 'cp /var/lib/postgresql/data/pg_wal/%f \"%p\"'" >  /postgresslave/pgdata/postgresql.auto.conf

tar -C postgresslave -zcvf /slave_pgdata/slave_pgdata.tar.gz pgdata

rm -rf /postgresslave/*
