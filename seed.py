"""Seed the Strata world into Supabase. Run once."""
import math
import random
import uuid
from datetime import datetime, timezone

# Must pip install supabase first
from supabase import create_client

SUPABASE_URL = "https://cfujmogbxokhiloqjjpv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmdWptb2dieG9raGlsb3FqanB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTg0MTgwOSwiZXhwIjoyMDkxNDE3ODA5fQ.fNoxfpNxTFV-GrBvf7q0V8EwSmlqQ4Bq-sPOzgXJaIQ"

CONSTELLATIONS = [
    "The Spiral", "The Twins", "The Sequence", "The Depth",
    "The River", "The Echo", "The Primes", "The Circle", "The Diagonal",
]

SYMBOLS = [
    "◆", "◇", "△", "▽", "○", "●", "□", "■", "☆", "★",
    "⬡", "⬢", "◎", "◉", "♦", "♢", "⊕", "⊗", "⊙", "⊛",
    "≋", "≈", "∿", "∾", "⌬", "⏣", "⎔", "⏢", "◬", "⟐",
]

GRID_SIZE = 16
MAX_LAYER = 7


def _is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True


def generate_fragments():
    rng = random.Random(42)
    fragments = []

    for name in CONSTELLATIONS:
        symbol_set = rng.sample(SYMBOLS, 4)

        if name == "The Spiral":
            cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
            for i in range(8):
                angle = i * 0.8
                r = 1.5 * math.exp(0.25 * angle)
                x = int(cx + r * math.cos(angle)) % GRID_SIZE
                y = int(cy + r * math.sin(angle)) % GRID_SIZE
                layer = min(i, MAX_LAYER - 1)
                fragments.append((x, y, layer, rng.choice(symbol_set), name, round(angle, 3)))

        elif name == "The Twins":
            for i in range(6):
                x = rng.randint(0, GRID_SIZE // 2 - 1)
                y = rng.randint(0, GRID_SIZE - 1)
                layer = rng.randint(0, MAX_LAYER - 1)
                fragments.append((x, y, layer, rng.choice(symbol_set), name, i + 0.1))
                fragments.append((GRID_SIZE - 1 - x, GRID_SIZE - 1 - y, layer,
                                  rng.choice(symbol_set), name, i + 0.2))

        elif name == "The Sequence":
            a, b = 1, 1
            for i in range(7):
                x = (a * 3) % GRID_SIZE
                y = (b * 5) % GRID_SIZE
                layer = i % MAX_LAYER
                fragments.append((x, y, layer, rng.choice(symbol_set), name, float(a)))
                a, b = b, a + b

        elif name == "The Depth":
            x, y = rng.randint(0, GRID_SIZE - 1), rng.randint(0, GRID_SIZE - 1)
            for layer in range(MAX_LAYER):
                fragments.append((x, y, layer, rng.choice(symbol_set), name, float(layer)))

        elif name == "The River":
            x = rng.randint(0, GRID_SIZE - 1)
            y = 0
            for layer in range(MAX_LAYER):
                for step in range(3):
                    fragments.append((x % GRID_SIZE, y % GRID_SIZE, layer,
                                      rng.choice(symbol_set), name, float(layer * 3 + step)))
                    x += rng.choice([-1, 0, 1])
                    y += 1

        elif name == "The Echo":
            base_x, base_y = rng.randint(2, 5), rng.randint(2, 5)
            for scale in [1, 2, 4]:
                for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                    x = (base_x + dx * scale) % GRID_SIZE
                    y = (base_y + dy * scale) % GRID_SIZE
                    layer = scale - 1
                    fragments.append((x, y, layer, rng.choice(symbol_set), name, float(scale)))

        elif name == "The Primes":
            primes = [p for p in range(GRID_SIZE) if _is_prime(p)]
            for px in primes:
                for py in primes[:3]:
                    layer = (px + py) % MAX_LAYER
                    fragments.append((px, py, layer, rng.choice(symbol_set), name, float(px * py)))

        elif name == "The Circle":
            cx, cy, radius = 5, 10, 4
            for i in range(10):
                angle = i * (2 * math.pi / 10)
                x = int(cx + radius * math.cos(angle)) % GRID_SIZE
                y = int(cy + radius * math.sin(angle)) % GRID_SIZE
                layer = i % MAX_LAYER
                fragments.append((x, y, layer, rng.choice(symbol_set), name, round(angle, 3)))

        elif name == "The Diagonal":
            for i in range(GRID_SIZE):
                if i % 2 == 0:
                    layer = (i // 2) % MAX_LAYER
                    fragments.append((i, i, layer, rng.choice(symbol_set), name, float(i)))
                if i % 3 == 0:
                    layer = (i // 3) % MAX_LAYER
                    fragments.append((i, GRID_SIZE - 1 - i, layer, rng.choice(symbol_set), name, float(i + 0.5)))

    # Noise
    for _ in range(50):
        x = rng.randint(0, GRID_SIZE - 1)
        y = rng.randint(0, GRID_SIZE - 1)
        layer = rng.randint(0, MAX_LAYER - 1)
        fragments.append((x, y, layer, rng.choice(SYMBOLS), "noise", 0.0))

    # Deduplicate
    seen = set()
    result = []
    for x, y, layer, symbol, constellation, hidden_value in fragments:
        key = (x, y, layer)
        if key not in seen:
            seen.add(key)
            result.append({
                "id": str(uuid.uuid4())[:8],
                "x": x, "y": y, "layer": layer,
                "symbol": symbol,
                "constellation": constellation,
                "hidden_value": hidden_value,
            })
    return result


def main():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Check if already seeded
    resp = sb.table("fragments").select("id", count="exact").limit(1).execute()
    if resp.count and resp.count > 0:
        print(f"Already seeded ({resp.count} fragments). Skipping.")
        return

    fragments = generate_fragments()
    print(f"Inserting {len(fragments)} fragments...")

    # Insert in batches of 50
    for i in range(0, len(fragments), 50):
        batch = fragments[i:i+50]
        sb.table("fragments").insert(batch).execute()
        print(f"  Batch {i//50 + 1}: {len(batch)} fragments")

    # Log the seeding
    sb.table("world_log").insert({
        "event": "world_seeded",
        "detail": f"{len(fragments)} fragments buried across {GRID_SIZE}x{GRID_SIZE} grid, {MAX_LAYER} layers deep, {len(CONSTELLATIONS)} constellations",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    print(f"Done! {len(fragments)} fragments seeded.")


if __name__ == "__main__":
    main()
