DO
$$
BEGIN
    IF NOT exists (SELECT * FROM pg_user WHERE usename = 'replicator') THEN
        CREATE ROLE "replicator" REPLICATION LOGIN ENCRYPTED PASSWORD '$POSTGRES_REPLICATOR_PASSWORD';
    END IF;
END
$$
;

-- DO
-- $$
-- BEGIN
--     IF NOT exists (SELECT * FROM pg_replication_slots WHERE slot_name = 'replication_slot_slave1') THEN
--         SELECT pg_create_physical_replication_slot('replication_slot_slave1');
--     END IF;
-- END
-- $$
-- ;
