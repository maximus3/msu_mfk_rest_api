#!/bin/bash
set -e

rm -rf /var/lib/postgresql/data/*
pg_basebackup --host=postgres --username=replicator --pgdata=/var/lib/postgresql/data/pgdata --wal-method=stream --slot=replication_slot_slave1 --write-recovery-conf --progress --format=plain
echo "# Do not edit this file manually!
# It will be overwritten by the ALTER SYSTEM command.
primary_conninfo = 'host=$POSTGRES_HOST port=$POSTGRES_PORT user=replicator password=$POSTGRES_REPLICATOR_PASSWORD'
primary_slot_name = 'replication_slot_slave1'
restore_command = 'cp /var/lib/postgresql/data/pgdata/pg_wal/%f \"%p\"'" >  /var/lib/postgresql/data/pgdata/postgresql.auto.conf
