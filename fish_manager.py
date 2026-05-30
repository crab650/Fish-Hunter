from __future__ import annotations

import random
from typing import Dict, Iterable, List, Tuple

import pygame

from assets import Assets, RotationCache
from config import FISH_CELL, FISH_SPECS, FPS, HEIGHT, MAX_FISH, WIDTH
from entities import Fish


class FishManager:
    def __init__(self) -> None:
        self.pool = [Fish() for _ in range(MAX_FISH)]
        self.fishes: List[Fish] = []
        self.spawn_timer = FPS * 2

    def spawn_group(self) -> None:
        if len(self.fishes) >= MAX_FISH or not self.pool:
            return

        chance = random.randrange(len(FISH_SPECS))
        spec = FISH_SPECS[random.randint(0, chance)]
        count = min(random.randint(1, spec.max_group), len(self.pool))
        start_left = random.random() > 0.5
        start_x = -spec.frame_w * 2 if start_left else WIDTH + spec.frame_w * 2
        start_y = random.randint(HEIGHT // 2 - 100, HEIGHT // 2 + 100)
        speed = random.uniform(spec.min_speed, spec.max_speed)
        angle = random.randint(-10, 10) + (0 if start_left else 180)

        prev_x = start_x
        prev_y = start_y
        direction = -1 if start_x > 0 else 1
        for _ in range(count):
            fish = self.pool.pop()
            dx = random.randint(20, max(21, spec.frame_w + 20))
            dy = random.randint(20, max(21, spec.frame_h + 20))
            if random.random() > 0.5:
                dy *= -1
            x = prev_x - dx * direction
            y = prev_y + dy
            fish.reset(spec, x, y, speed, angle)
            self.fishes.append(fish)
            prev_x, prev_y = x, y

    def update(self) -> int:
        earned = 0
        for fish in self.fishes[:]:
            coin = fish.update()
            if coin:
                earned += coin
                self.recycle(fish)
            elif fish.active and fish.is_out() and fish.has_shown:
                self.recycle(fish)

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_timer = FPS * (2 if len(self.fishes) < MAX_FISH // 2 else 3)
            self.spawn_group()
        return earned

    def recycle(self, fish: Fish) -> None:
        if fish in self.fishes:
            self.fishes.remove(fish)
        fish.active = False
        self.pool.append(fish)

    def build_grid(self) -> Dict[Tuple[int, int], List[Fish]]:
        grid: Dict[Tuple[int, int], List[Fish]] = {}
        for fish in self.fishes:
            if not fish.active or fish.captured:
                continue
            key = (int(fish.x // FISH_CELL), int(fish.y // FISH_CELL))
            grid.setdefault(key, []).append(fish)
        return grid

    def nearby(self, x: float, y: float, grid: Dict[Tuple[int, int], List[Fish]]) -> Iterable[Fish]:
        cx = int(x // FISH_CELL)
        cy = int(y // FISH_CELL)
        for gx in range(cx - 1, cx + 2):
            for gy in range(cy - 1, cy + 2):
                yield from grid.get((gx, gy), ())

    def draw(self, screen: pygame.Surface, assets: Assets, rotations: RotationCache) -> None:
        for fish in self.fishes:
            fish.draw(screen, assets, rotations)
