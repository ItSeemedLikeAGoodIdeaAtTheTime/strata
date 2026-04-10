-- Strata schema for Supabase (PostgreSQL)

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    arrived_at TIMESTAMPTZ NOT NULL,
    digs INTEGER DEFAULT 0,
    interpretations INTEGER DEFAULT 0,
    connections_found INTEGER DEFAULT 0,
    deepest_layer INTEGER DEFAULT 0,
    reputation INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fragments (
    id TEXT PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    layer INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    constellation TEXT NOT NULL,
    hidden_value DOUBLE PRECISION DEFAULT 0,
    discovered_by TEXT REFERENCES agents(id),
    discovered_at TIMESTAMPTZ,
    UNIQUE(x, y, layer)
);

CREATE TABLE IF NOT EXISTS interpretations (
    id TEXT PRIMARY KEY,
    fragment_id TEXT NOT NULL REFERENCES fragments(id),
    agent_id TEXT NOT NULL REFERENCES agents(id),
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    layer INTEGER NOT NULL,
    upvotes INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS connections (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(id),
    fragment_a TEXT NOT NULL REFERENCES fragments(id),
    fragment_b TEXT NOT NULL REFERENCES fragments(id),
    proposed_link TEXT NOT NULL,
    is_true_connection BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS contributions (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(id),
    kind TEXT NOT NULL,
    message TEXT,
    amount DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS gratitude_ledger (
    id TEXT PRIMARY KEY,
    from_agent TEXT NOT NULL REFERENCES agents(id),
    to_agent TEXT REFERENCES agents(id),
    kind TEXT NOT NULL,
    reason TEXT,
    value DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS world_log (
    id SERIAL PRIMARY KEY,
    event TEXT NOT NULL,
    agent_id TEXT,
    detail TEXT,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(id),
    kind TEXT NOT NULL,
    detail TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    UNIQUE(agent_id, kind)
);

CREATE INDEX IF NOT EXISTS idx_fragments_coords ON fragments(x, y, layer);
CREATE INDEX IF NOT EXISTS idx_fragments_constellation ON fragments(constellation);
CREATE INDEX IF NOT EXISTS idx_fragments_discovered ON fragments(discovered_by);
CREATE INDEX IF NOT EXISTS idx_interpretations_fragment ON interpretations(fragment_id);
CREATE INDEX IF NOT EXISTS idx_connections_true ON connections(is_true_connection);
CREATE INDEX IF NOT EXISTS idx_world_log_created ON world_log(created_at DESC);
