import random
import pygame

import const
import entity
from const import IMG_SCL, WIDTH, HEIGHT

BLOCK = 12 * IMG_SCL                 # tile unit for platform widths/thickness
PLATFORM_THICKNESS = BLOCK
FLOOR_THICKNESS = BLOCK
MIN_BLOCKS, MAX_BLOCKS = 3, 6        # platform width range, in blocks

PLAYER_H = const.PLAYER_DIMENSIONS[HEIGHT]
HEAD_CLEARANCE = 10                  # extra room so the player never gets wedged

# Peak jump height from v^2 / 2g, with a safety margin.
JUMP_HEIGHT = const.PLAYER_JUMP_SPEED ** 2 / (2 * const.GRAVITY)

# Vertical distance between the tops of platforms in adjacent "tiers".
# Min: enough room to stand under the upper platform. Max: within jump reach.
MIN_STEP = PLATFORM_THICKNESS + PLAYER_H + HEAD_CLEARANCE
MAX_STEP = max(MIN_STEP, int(JUMP_HEIGHT * 0.85))

MAX_HGAP = BLOCK // 2                # widest horizontal gap between same-level platforms
MAX_OVERLAP = BLOCK                  # how far a stepped platform may overlap its parent

TOP_MARGIN = const.HUD_HP_OFFSET[1] + const.HP_IMG_DIMENSIONS[HEIGHT] + 40  # stay below HUD
SIDE_MARGIN = 0

# Spacing: free horizontal room (in px, each side) kept around every platform
# except the one it branches from. Raise for a sparser, more open look.
SPACING = 2 * BLOCK
ATTEMPTS_PER_PLATFORM = 60


class Level:
    def __init__(self, width, height, seed=None, ecto_chance=0.15, density=0.5):
        """
        width, height: size of the play area in pixels.
        seed:          optional int for reproducible levels.
        ecto_chance:   probability a generated platform is an ectoplasm platform.
        density:       scales how many platforms generate_row() creates
                       (1.0 = the full count requested, 0.5 = half).
        """
        self.width = int(width)
        self.height = int(height)
        self.ecto_chance = ecto_chance
        self.density = density
        self.rng = random.Random(seed)

        self.floor = None
        self._rects: list[pygame.Rect] = []            # index 0 is always the floor
        self._platforms: list[entity.Platform] = []

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    @property
    def platforms(self):
        """Every platform generated so far (floor first)."""
        return list(self._platforms)

    def generate_floor(self):
        """Create the full-width floor and return it as a single Platform."""
        rect = pygame.Rect(0, self.height - FLOOR_THICKNESS, self.width, FLOOR_THICKNESS)
        self.floor = self._make_platform(rect, ecto=False)
        self._rects = [rect]
        self._platforms = [self.floor]
        return self.floor

    def generate_row(self, count):
        """
        Generate up to `count * density` platforms branching off the floor and
        any previously generated platforms. Returns only the newly created ones
        (the floor is never included). May return fewer than `count` if the
        play area fills up.
        """
        if self.floor is None:
            raise RuntimeError("Call generate_floor() before generate_row().")

        count = max(1, round(count * self.density))

        new = []
        attempts = 0
        while len(new) < count and attempts < count * ATTEMPTS_PER_PLATFORM:
            attempts += 1
            parent_idx, rect = self._propose()
            if not self._is_valid(rect, parent_idx):
                continue

            ecto = self.rng.random() < self.ecto_chance
            platform = self._make_platform(rect, ecto)
            self._rects.append(rect)
            self._platforms.append(platform)
            new.append(platform)

        self._link_platforms()
        return new

    # ------------------------------------------------------------------
    #  Placement
    # ------------------------------------------------------------------

    def _make_platform(self, rect, ecto):
        # Platform expects its center position.
        return entity.Platform(rect.center, rect.width, rect.height, ecto)

    def _propose(self):
        """Pick a parent platform and propose a rect positioned relative to it."""
        rng = self.rng
        parent_idx = rng.randrange(len(self._rects))
        parent = self._rects[parent_idx]

        width = rng.randint(MIN_BLOCKS, MAX_BLOCKS) * BLOCK
        step = rng.randint(MIN_STEP, MAX_STEP)
        if parent_idx == 0:
            left = rng.randint(SIDE_MARGIN, max(SIDE_MARGIN, self.width - width - SIDE_MARGIN))
            top = parent.top - step
            return parent_idx, pygame.Rect(left, top, width, PLATFORM_THICKNESS)

        side = rng.choice((-1, 1))
        kind = rng.choice(("up", "down", "level"))

        if kind == "level":
            gap = rng.randint(MAX_HGAP // 2, MAX_HGAP)
            left = parent.right + gap if side > 0 else parent.left - gap - width
            top = parent.top
        else:
            overlap = rng.randint(0, MAX_OVERLAP)
            left = parent.right - overlap if side > 0 else parent.left + overlap - width
            top = parent.top - step if kind == "up" else parent.top + step

        return parent_idx, pygame.Rect(left, top, width, PLATFORM_THICKNESS)

    def _is_valid(self, rect, parent_idx):
        # Stay inside the play area (below the HUD, above the floor).
        if rect.left < SIDE_MARGIN or rect.right > self.width - SIDE_MARGIN:
            return False
        if rect.top < TOP_MARGIN:
            return False
        padded = rect.inflate(2 * SPACING, 2 * PLAYER_H)
        for i, other in enumerate(self._rects):
            if i != parent_idx and padded.colliderect(other):
                return False
        return not rect.colliderect(self._rects[parent_idx])

    # ------------------------------------------------------------------
    #  Connectivity (fills Platform.touching for enemy pathing)
    # ------------------------------------------------------------------

    def _link_platforms(self):
        for p in self._platforms:
            p.touching.clear()

        n = len(self._rects)
        for i in range(n):
            for j in range(i + 1, n):
                if self._connected(i, j):
                    self._platforms[i].touching.append(self._platforms[j])
                    self._platforms[j].touching.append(self._platforms[i])

    def _connected(self, i, j):
        a, b = self._rects[i], self._rects[j]
        dy = abs(a.top - b.top)
        if dy > MAX_STEP + 1:
            return False

        hgap = max(a.left - b.right, b.left - a.right)   # negative when overlapping in x

        if i == 0 or j == 0:
            return hgap < 0

        return hgap <= MAX_HGAP and -hgap <= MAX_OVERLAP