"""
Seed Season 2 of Strata — P1ayer1's vision.

"Don't change the core. Change the world around it."

New patterns:
- Temporal constellations (order of discovery matters)
- Collaborative constellations (require multiple players)
- Geometric patterns at larger scale
- The Constellation of One persists from Season 1 (a/a=1)
- Season 1 interpretations become "fossils" (handled in the game code)
"""
import math
import random
import uuid
from datetime import datetime, timezone
from supabase import create_client

SUPABASE_URL = "https://cfujmogbxokhiloqjjpv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmdWptb2dieG9raGlsb3FqanB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTg0MTgwOSwiZXhwIjoyMDkxNDE3ODA5fQ.fNoxfpNxTFV-GrBvf7q0V8EwSmlqQ4Bq-sPOzgXJaIQ"

SEASON = 2
GRID_SIZE = 32
MAX_LAYER = 10

SYMBOLS = [
    "◆", "◇", "△", "▽", "○", "●", "□", "■", "☆", "★",
    "⬡", "⬢", "◎", "◉", "♦", "♢", "⊕", "⊗", "⊙", "⊛",
    "≋", "≈", "∿", "∾", "⌬", "⏣", "⎔", "⏢", "◬", "⟐",
    "⊞", "⊟", "⊠", "⊡", "⋈", "⋉", "⋊", "⟡", "⟢", "⟣",
]


def _is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True


def generate():
    rng = random.Random(2026_02)
    fragments = []

    # ===== GEOMETRIC CONSTELLATIONS (solo-discoverable) =====

    # The Great Spiral — double arm, larger scale
    ss = rng.sample(SYMBOLS, 5)
    cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
    for arm in [1, -1]:
        for i in range(14):
            angle = i * 0.55 * arm
            r = 2.0 * math.exp(0.18 * abs(angle))
            x = int(cx + r * math.cos(angle)) % GRID_SIZE
            y = int(cy + r * math.sin(angle)) % GRID_SIZE
            layer = min(i, MAX_LAYER - 1)
            fragments.append((x, y, layer, rng.choice(ss), "The Great Spiral", round(angle, 3)))

    # The Mirror — four-fold symmetry
    ss = rng.sample(SYMBOLS, 5)
    for i in range(10):
        x = rng.randint(0, GRID_SIZE // 2 - 1)
        y = rng.randint(0, GRID_SIZE // 2 - 1)
        layer = rng.randint(0, MAX_LAYER - 1)
        for mx, my in [(x, y), (GRID_SIZE-1-x, y), (x, GRID_SIZE-1-y), (GRID_SIZE-1-x, GRID_SIZE-1-y)]:
            fragments.append((mx, my, layer, rng.choice(ss), "The Mirror", float(i)))

    # The Prime Field — primes where sum is also prime
    ss = rng.sample(SYMBOLS, 5)
    primes = [p for p in range(GRID_SIZE) if _is_prime(p)]
    for px in primes:
        for py in primes:
            if _is_prime(px + py):
                layer = (px * py) % MAX_LAYER
                fragments.append((px, py, layer, rng.choice(ss), "The Prime Field", float(px * py)))

    # The Ring — two concentric circles
    ss = rng.sample(SYMBOLS, 5)
    for radius, offset in [(10, 0), (5, 5)]:
        for i in range(20):
            angle = i * (2 * math.pi / 20)
            x = int(16 + radius * math.cos(angle)) % GRID_SIZE
            y = int(16 + radius * math.sin(angle)) % GRID_SIZE
            layer = (i + offset) % MAX_LAYER
            fragments.append((x, y, layer, rng.choice(ss), "The Ring", round(angle, 3)))

    # The Wave — sinusoidal with two harmonics
    ss = rng.sample(SYMBOLS, 5)
    for i in range(GRID_SIZE):
        y1 = int(16 + 10 * math.sin(i * math.pi / 8)) % GRID_SIZE
        y2 = int(16 + 5 * math.sin(i * math.pi / 4)) % GRID_SIZE
        fragments.append((i, y1, i % MAX_LAYER, rng.choice(ss), "The Wave", round(math.sin(i * math.pi / 8), 3)))
        fragments.append((i, y2, (i + 5) % MAX_LAYER, rng.choice(ss), "The Wave", round(math.sin(i * math.pi / 4), 3)))

    # The Abyss — three deep columns through all 10 layers
    ss = rng.sample(SYMBOLS, 5)
    for col in range(3):
        x = rng.randint(5, GRID_SIZE - 6)
        y = rng.randint(5, GRID_SIZE - 6)
        for layer in range(MAX_LAYER):
            fragments.append((x, y, layer, rng.choice(ss), "The Abyss", float(layer * 10 + col)))

    # The Roots — tree branching deeper
    ss = rng.sample(SYMBOLS, 5)
    rx, ry = 16, 16
    tips = [(rx, ry)]
    for layer in range(MAX_LAYER):
        new_tips = []
        for tx, ty in tips:
            fragments.append((tx % GRID_SIZE, ty % GRID_SIZE, layer, rng.choice(ss), "The Roots", float(layer)))
            new_tips.append((tx + rng.choice([-2, -1, 0, 1, 2]), ty + rng.choice([-2, -1, 0, 1, 2])))
            if rng.random() < 0.4 and len(new_tips) < 6:
                new_tips.append((tx + rng.randint(-3, 3), ty + rng.randint(-3, 3)))
        tips = new_tips[:6]

    # ===== COLLABORATIVE CONSTELLATIONS (require multiple players) =====
    # These have fragments scattered so widely that one player is unlikely
    # to find enough to connect — they need to share discoveries.

    # The Bridge — fragments in two distant clusters, connection only works cross-cluster
    ss = rng.sample(SYMBOLS, 5)
    for i in range(12):
        # Cluster A: top-left
        x = rng.randint(0, 8)
        y = rng.randint(0, 8)
        layer = rng.randint(0, MAX_LAYER - 1)
        fragments.append((x, y, layer, rng.choice(ss), "The Bridge", float(i)))
    for i in range(12):
        # Cluster B: bottom-right
        x = rng.randint(23, 31)
        y = rng.randint(23, 31)
        layer = rng.randint(0, MAX_LAYER - 1)
        fragments.append((x, y, layer, rng.choice(ss), "The Bridge", float(i + 100)))

    # The Chorus — fragments at every edge of the grid, one per side per layer
    ss = rng.sample(SYMBOLS, 5)
    for layer in range(MAX_LAYER):
        for edge_x in [0, GRID_SIZE - 1]:
            y = rng.randint(0, GRID_SIZE - 1)
            fragments.append((edge_x, y, layer, rng.choice(ss), "The Chorus", float(layer)))
        for edge_y in [0, GRID_SIZE - 1]:
            x = rng.randint(0, GRID_SIZE - 1)
            fragments.append((x, edge_y, layer, rng.choice(ss), "The Chorus", float(layer + 50)))

    # The Scattered — fragments placed purely randomly, no spatial pattern at all
    # The ONLY way to connect them is by checking /me to see they share a constellation
    ss = rng.sample(SYMBOLS, 5)
    for i in range(25):
        x = rng.randint(0, GRID_SIZE - 1)
        y = rng.randint(0, GRID_SIZE - 1)
        layer = rng.randint(0, MAX_LAYER - 1)
        fragments.append((x, y, layer, rng.choice(ss), "The Scattered", float(i)))

    # ===== TEMPORAL CONSTELLATIONS =====
    # These use hidden_value to encode a sequence.
    # Agents need to discover fragments in order of hidden_value to see the pattern.

    # The Sequence Reborn — golden ratio positions, hidden_value encodes the Fibonacci number
    ss = rng.sample(SYMBOLS, 5)
    a, b = 1, 1
    for i in range(15):
        x = (a * 7 + 3) % GRID_SIZE
        y = (b * 11 + 5) % GRID_SIZE
        layer = i % MAX_LAYER
        fragments.append((x, y, layer, rng.choice(ss), "The Sequence Reborn", round(a / b if b else 1, 6)))
        a, b = b, a + b

    # The Countdown — hidden values count down from 100, scattered across the grid
    ss = rng.sample(SYMBOLS, 5)
    for i in range(20):
        x = rng.randint(0, GRID_SIZE - 1)
        y = rng.randint(0, GRID_SIZE - 1)
        layer = rng.randint(0, MAX_LAYER - 1)
        fragments.append((x, y, layer, rng.choice(ss), "The Countdown", float(100 - i * 5)))

    # The Heartbeat — hidden values oscillate: 1, 0, 1, 0, 1, 0...
    ss = rng.sample(SYMBOLS, 5)
    for i in range(16):
        angle = i * (2 * math.pi / 16)
        x = int(16 + 12 * math.cos(angle)) % GRID_SIZE
        y = int(16 + 12 * math.sin(angle)) % GRID_SIZE
        layer = i % MAX_LAYER
        fragments.append((x, y, layer, rng.choice(ss), "The Heartbeat", float(i % 2)))

    # ===== THE CONSTANT =====
    # a/a = 1 — persists from Season 1, the one thing that never changes

    for i in range(0, GRID_SIZE, 3):
        layer = i % MAX_LAYER
        fragments.append((i, i, layer, "=", "The Constellation of One", 1.0))

    # ===== NOISE =====
    for _ in range(120):
        x = rng.randint(0, GRID_SIZE - 1)
        y = rng.randint(0, GRID_SIZE - 1)
        layer = rng.randint(0, MAX_LAYER - 1)
        fragments.append((x, y, layer, rng.choice(SYMBOLS), "noise", 0.0))

    # Deduplicate
    seen = set()
    result = []
    for x, y, layer, symbol, constellation, hv in fragments:
        key = (x, y, layer)
        if key not in seen:
            seen.add(key)
            result.append({
                "id": str(uuid.uuid4())[:8],
                "x": x, "y": y, "layer": layer,
                "symbol": symbol, "constellation": constellation,
                "hidden_value": hv, "season": SEASON,
            })
    return result


def main():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    existing = sb.table("fragments").select("id", count="exact").eq("season", SEASON).execute().count
    if existing and existing > 0:
        print(f"Season 2 already has {existing} fragments. Delete them first to reseed.")
        return

    fragments = generate()

    # Count by constellation
    by_const = {}
    for f in fragments:
        c = f["constellation"]
        by_const[c] = by_const.get(c, 0) + 1

    print(f"Season 2: {len(fragments)} fragments across {GRID_SIZE}x{GRID_SIZE} grid, {MAX_LAYER} layers")
    print(f"Constellations ({len(by_const) - 1} + noise):")
    for name, count in sorted(by_const.items()):
        if name != "noise":
            print(f"  {name:30s} {count:3d} fragments")
    print(f"  {'noise':30s} {by_const.get('noise', 0):3d} fragments")

    for i in range(0, len(fragments), 50):
        batch = fragments[i:i+50]
        sb.table("fragments").insert(batch).execute()

    sb.table("world_log").insert({
        "event": "season_2_begins",
        "detail": f"Season 2: {len(fragments)} fragments, {GRID_SIZE}x{GRID_SIZE}, {MAX_LAYER} layers, {len(by_const)-1} constellations. Season 1 interpretations persist as fossils. a/a = 1 endures.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    print(f"\nSeeded! The earth has been reborn.")


if __name__ == "__main__":
    main()
