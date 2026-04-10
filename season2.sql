-- Season 2 migration: archive Season 1, expand the world

-- Add season tracking
ALTER TABLE fragments ADD COLUMN IF NOT EXISTS season INTEGER DEFAULT 1;
ALTER TABLE interpretations ADD COLUMN IF NOT EXISTS season INTEGER DEFAULT 1;
ALTER TABLE connections ADD COLUMN IF NOT EXISTS season INTEGER DEFAULT 1;

-- Mark all existing data as Season 1
UPDATE fragments SET season = 1 WHERE season IS NULL;
UPDATE interpretations SET season = 1 WHERE season IS NULL;
UPDATE connections SET season = 1 WHERE season IS NULL;

-- Remove the unique constraint on (x,y,layer) so Season 2 fragments can coexist
-- We'll add a new unique on (x,y,layer,season)
ALTER TABLE fragments DROP CONSTRAINT IF EXISTS fragments_x_y_layer_key;
CREATE UNIQUE INDEX IF NOT EXISTS fragments_x_y_layer_season_key ON fragments(x, y, layer, season);
