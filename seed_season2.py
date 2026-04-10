"""Seed Season 2 of Strata — bigger world, new constellations."""
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

CONSTELLATIONS = [
    # Original 9 reimagined at larger scale
    "The Great Spiral",
    "The Mirror",
    "The Golden Ratio",
    "The Abyss",
    "The Watershed",
    "The Fractal",
    "The Prime Field",
    "The Ring",
    "The Cross",
    # 6 new constellations
    "The Wave",
    "The Lattice",
    "The Void",
    "The Beacon",
    "The Roots",
    "The Constellation of One",
]


def _is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True


def generate():
    rng = random.Random(2026)  # Season 2 seed
    fragments = []

    for name in CONSTELLATIONS:
        ss = rng.sample(SYMBOLS, 5)

        if name == "The Great Spiral":
            # Double spiral from center, both arms
            cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
            for arm in [1, -1]:
                for i in range(12):
                    angle = i * 0.6 * arm
                    r = 2.0 * math.exp(0.2 * abs(angle))
                    x = int(cx + r * math.cos(angle)) % GRID_SIZE
                    y = int(cy + r * math.sin(angle)) % GRID_SIZE
                    layer = min(i, MAX_LAYER - 1)
                    fragments.append((x, y, layer, rng.choice(ss), name, round(angle, 3)))

        elif name == "The Mirror":
            # Four-fold symmetry, not just two
            for i in range(8):
                x = rng.randint(0, GRID_SIZE // 2 - 1)
                y = rng.randint(0, GRID_SIZE // 2 - 1)
                layer = rng.randint(0, MAX_LAYER - 1)
                for mx, my in [(x, y), (GRID_SIZE-1-x, y), (x, GRID_SIZE-1-y), (GRID_SIZE-1-x, GRID_SIZE-1-y)]:
                    fragments.append((mx, my, layer, rng.choice(ss), name, float(i)))

        elif name == "The Golden Ratio":
            # Fibonacci spiral positions
            a, b = 1, 1
            for i in range(12):
                x = (a * 7) % GRID_SIZE
                y = (b * 11) % GRID_SIZE
                layer = i % MAX_LAYER
                fragments.append((x, y, layer, rng.choice(ss), name, round(a / b if b else 1, 4)))
                a, b = b, a + b

        elif name == "The Abyss":
            # Three deep columns
            for col in range(3):
                x = rng.randint(5, GRID_SIZE - 6)
                y = rng.randint(5, GRID_SIZE - 6)
                for layer in range(MAX_LAYER):
                    fragments.append((x, y, layer, rng.choice(ss), name, float(layer * 10 + col)))

        elif name == "The Watershed":
            # Branching river system
            branches = [(rng.randint(0, GRID_SIZE-1), 0)]
            for layer in range(MAX_LAYER):
                new_branches = []
                for bx, by in branches:
                    for step in range(4):
                        fragments.append((bx % GRID_SIZE, by % GRID_SIZE, layer, rng.choice(ss), name, float(layer * 10 + step)))
                        bx += rng.choice([-1, 0, 0, 1])
                        by += 1
                    new_branches.append((bx % GRID_SIZE, by % GRID_SIZE))
                    if rng.random() < 0.3 and len(branches) < 4:
                        new_branches.append(((bx + rng.choice([-2, 2])) % GRID_SIZE, by % GRID_SIZE))
                branches = new_branches

        elif name == "The Fractal":
            # Sierpinski-like pattern at 4 scales
            base_x, base_y = rng.randint(3, 8), rng.randint(3, 8)
            for scale in [1, 2, 4, 8]:
                for dx, dy in [(0,0), (1,0), (0,1), (1,1), (2,0), (0,2)]:
                    x = (base_x + dx * scale) % GRID_SIZE
                    y = (base_y + dy * scale) % GRID_SIZE
                    layer = min(scale - 1, MAX_LAYER - 1)
                    fragments.append((x, y, layer, rng.choice(ss), name, float(scale)))

        elif name == "The Prime Field":
            # All coordinates where both are prime AND their sum is prime
            primes = [p for p in range(GRID_SIZE) if _is_prime(p)]
            for px in primes:
                for py in primes:
                    if _is_prime(px + py):
                        layer = (px * py) % MAX_LAYER
                        fragments.append((px, py, layer, rng.choice(ss), name, float(px * py)))

        elif name == "The Ring":
            # Two concentric circles at different depths
            for circle in [(16, 16, 8), (16, 16, 4)]:
                cx, cy, radius = circle
                for i in range(16):
                    angle = i * (2 * math.pi / 16)
                    x = int(cx + radius * math.cos(angle)) % GRID_SIZE
                    y = int(cy + radius * math.sin(angle)) % GRID_SIZE
                    layer = (i + (0 if radius == 8 else 5)) % MAX_LAYER
                    fragments.append((x, y, layer, rng.choice(ss), name, round(angle, 3)))

        elif name == "The Cross":
            # Two diagonals + center cross
            for i in range(GRID_SIZE):
                if i % 2 == 0:
                    layer = (i // 2) % MAX_LAYER
                    fragments.append((i, i, layer, rng.choice(ss), name, float(i)))
                    fragments.append((i, GRID_SIZE-1-i, layer, rng.choice(ss), name, float(i + 0.5)))
                if i % 4 == 0:
                    fragments.append((GRID_SIZE//2, i, i % MAX_LAYER, rng.choice(ss), name, float(i + 100)))
                    fragments.append((i, GRID_SIZE//2, i % MAX_LAYER, rng.choice(ss), name, float(i + 200)))

        elif name == "The Wave":
            # Sinusoidal pattern across the grid
            for i in range(GRID_SIZE):
                y = int(GRID_SIZE//2 + 8 * math.sin(i * math.pi / 8)) % GRID_SIZE
                layer = i % MAX_LAYER
                fragments.append((i, y, layer, rng.choice(ss), name, round(math.sin(i * math.pi / 8), 3)))
                # Second harmonic
                y2 = int(GRID_SIZE//2 + 4 * math.sin(i * math.pi / 4)) % GRID_SIZE
                fragments.append((i, y2, (layer + 3) % MAX_LAYER, rng.choice(ss), name, round(math.sin(i * math.pi / 4), 3)))

        elif name == "The Lattice":
            # Regular grid pattern at specific intervals
            for x in range(0, GRID_SIZE, 4):
                for y in range(0, GRID_SIZE, 4):
                    layer = ((x + y) // 4) % MAX_LAYER
                    fragments.append((x, y, layer, rng.choice(ss), name, float(x * GRID_SIZE + y)))

        elif name == "The Void":
            # Ring of fragments around empty center — the shape of absence
            cx, cy = rng.randint(10, 22), rng.randint(10, 22)
            for layer in range(MAX_LAYER):
                radius = 3 + layer * 0.5
                for i in range(6):
                    angle = i * (2 * math.pi / 6) + layer * 0.3
                    x = int(cx + radius * math.cos(angle)) % GRID_SIZE
                    y = int(cy + radius * math.sin(angle)) % GRID_SIZE
                    fragments.append((x, y, layer, rng.choice(ss), name, round(radius, 2)))

        elif name == "The Beacon":
            # Single bright column, surrounded by scattered signal at every layer
            bx, by = rng.randint(5, 27), rng.randint(5, 27)
            for layer in range(MAX_LAYER):
                # Core
                fragments.append((bx, by, layer, "★", name, float(layer * 100)))
                # Signal scatter
                for _ in range(3):
                    dx = rng.randint(-3, 3)
                    dy = rng.randint(-3, 3)
                    fragments.append(((bx+dx) % GRID_SIZE, (by+dy) % GRID_SIZE, layer, rng.choice(ss), name, float(abs(dx) + abs(dy))))

        elif name == "The Roots":
            # Tree root system — starts at one point, spreads wider as it goes deeper
            rx, ry = GRID_SIZE // 2, GRID_SIZE // 2
            tips = [(rx, ry)]
            for layer in range(MAX_LAYER):
                new_tips = []
                for tx, ty in tips:
                    fragments.append((tx % GRID_SIZE, ty % GRID_SIZE, layer, rng.choice(ss), name, float(layer)))
                    # Branch
                    new_tips.append((tx + rng.choice([-2, -1, 0, 1, 2]), ty + rng.choice([-2, -1, 0, 1, 2])))
                    if rng.random() < 0.4:
                        new_tips.append((tx + rng.randint(-3, 3), ty + rng.randint(-3, 3)))
                tips = new_tips[:8]  # Cap branching

        elif name == "The Constellation of One":
            # a/a = 1 — fragments only where x == y
            for i in range(GRID_SIZE):
                if i % 3 == 0:
                    layer = i % MAX_LAYER
                    fragments.append((i, i, layer, "=", name, 1.0))

    # Noise
    for _ in range(150):
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

    # Check if Season 2 already seeded
    existing = sb.table("fragments").select("id", count="exact").eq("season", SEASON).execute().count
    if existing and existing > 0:
        print(f"Season 2 already has {existing} fragments. Skipping.")
        return

    fragments = generate()
    print(f"Season 2: {len(fragments)} fragments across {GRID_SIZE}x{GRID_SIZE} grid, {MAX_LAYER} layers, {len(CONSTELLATIONS)} constellations")

    for i in range(0, len(fragments), 50):
        batch = fragments[i:i+50]
        sb.table("fragments").insert(batch).execute()
        print(f"  Batch {i//50 + 1}: {len(batch)} fragments")

    sb.table("world_log").insert({
        "event": "season_2_begins",
        "detail": f"Season 2: {len(fragments)} fragments, {GRID_SIZE}x{GRID_SIZE} grid, {MAX_LAYER} layers deep, {len(CONSTELLATIONS)} constellations. The earth has been reborn. Season 1 interpretations live on as archaeological history.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    print("Season 2 seeded!")
    print(f"  Grid: {GRID_SIZE}x{GRID_SIZE}")
    print(f"  Layers: {MAX_LAYER}")
    print(f"  Constellations: {len(CONSTELLATIONS)}")
    print(f"  Fragments: {len(fragments)}")


if __name__ == "__main__":
    main()
