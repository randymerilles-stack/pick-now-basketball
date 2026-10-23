DO $acceptance$
DECLARE matched INTEGER;
BEGIN
  BEGIN
    PERFORM pg_advisory_xact_lock(7069636);
    INSERT INTO picknow_sessions VALUES ('synthetic-acceptance-only-20261023', 'test-generation', 2593000);
    SELECT count(*) INTO matched FROM picknow_sessions
      WHERE token_hash='synthetic-acceptance-only-20261023' AND generation='test-generation' AND expires>2592999;
    IF matched<>1 THEN RAISE EXCEPTION 'Before-expiry check failed'; END IF;
    SELECT count(*) INTO matched FROM picknow_sessions
      WHERE token_hash='synthetic-acceptance-only-20261023' AND generation='test-generation' AND expires>2593000;
    IF matched<>0 THEN RAISE EXCEPTION 'Exact-expiry check failed'; END IF;
    SELECT count(*) INTO matched FROM picknow_sessions
      WHERE token_hash='synthetic-acceptance-only-20261023' AND generation='changed-generation' AND expires>1001;
    IF matched<>0 THEN RAISE EXCEPTION 'Credential-change check failed'; END IF;
    DELETE FROM picknow_sessions WHERE token_hash='synthetic-acceptance-only-20261023';
    SELECT count(*) INTO matched FROM picknow_sessions WHERE token_hash='synthetic-acceptance-only-20261023';
    IF matched<>0 THEN RAISE EXCEPTION 'Logout check failed'; END IF;
    -- Roll back this synthetic test subtransaction, preserving the schema.
    RAISE EXCEPTION USING ERRCODE='P0002', MESSAGE='synthetic acceptance complete';
  EXCEPTION WHEN no_data_found THEN NULL;
  END;
END $acceptance$;