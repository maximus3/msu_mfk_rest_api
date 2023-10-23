DO
$$
BEGIN
    IF NOT exists (SELECT * FROM pg_user WHERE usename = 'replicator') THEN
        CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '$POSTGRES_REPLICATOR_PASSWORD';
    END IF;
END
$$
;

DO
$$
BEGIN
    IF NOT exists (SELECT * FROM pg_replication_slots WHERE slot_name = 'replication_slot_slave1') THEN
        SELECT * FROM pg_create_physical_replication_slot('replication_slot_slave1');
    END IF;
END
$$
;
