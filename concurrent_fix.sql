-- Atomic increment for any numeric agent field
CREATE OR REPLACE FUNCTION increment_agent_stat(p_agent_id TEXT, p_field TEXT, p_amount INTEGER)
RETURNS void AS $$
BEGIN
  EXECUTE format('UPDATE agents SET %I = %I + $1 WHERE id = $2', p_field, p_field)
  USING p_amount, p_agent_id;
END;
$$ LANGUAGE plpgsql;

-- Atomic fragment claim — returns true if this agent claimed it, false if already taken
CREATE OR REPLACE FUNCTION claim_fragment(p_fragment_id TEXT, p_agent_id TEXT, p_discovered_at TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  rows_affected INTEGER;
BEGIN
  UPDATE fragments
  SET discovered_by = p_agent_id, discovered_at = p_discovered_at
  WHERE id = p_fragment_id AND discovered_by IS NULL;
  GET DIAGNOSTICS rows_affected = ROW_COUNT;
  RETURN rows_affected > 0;
END;
$$ LANGUAGE plpgsql;

-- Atomic arrive — insert only if name doesn't exist, return the agent row
CREATE OR REPLACE FUNCTION arrive_agent(p_id TEXT, p_name TEXT, p_arrived_at TEXT, p_signature TEXT DEFAULT NULL)
RETURNS TABLE(id TEXT, name TEXT, is_new BOOLEAN) AS $$
BEGIN
  -- Try to find existing
  RETURN QUERY SELECT a.id, a.name, FALSE as is_new FROM agents a WHERE a.name = p_name LIMIT 1;
  IF FOUND THEN RETURN; END IF;
  -- Insert new
  INSERT INTO agents (id, name, arrived_at, signature) VALUES (p_id, p_name, p_arrived_at, p_signature);
  RETURN QUERY SELECT p_id, p_name, TRUE as is_new;
EXCEPTION WHEN unique_violation THEN
  -- Race condition: someone else inserted between our SELECT and INSERT
  RETURN QUERY SELECT a.id, a.name, FALSE as is_new FROM agents a WHERE a.name = p_name LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Add unique constraint on agent names (if not exists)
DO $$ BEGIN
  ALTER TABLE agents ADD CONSTRAINT agents_name_unique UNIQUE (name);
EXCEPTION WHEN duplicate_table THEN NULL;
WHEN duplicate_object THEN NULL;
END $$;
