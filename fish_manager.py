"""Fish spawning, pooling, and spatial lookup.

中文：集中管理魚群生成、回收和簡易格子索引，讓主遊戲只需要查詢附近的魚做命中判定。
English: Centralizes fish spawning, recycling, and a lightweight grid index so the main game can query nearby fish for hit detection.
"""

from __future__ import annotations

import random
from typing import Dict, Iterable, List, Tuple

import pygame

from assets import Assets, RotationCache
from config import FISH_CELL, FISH_SPECS, FPS, HEIGHT, MAX_FISH, WIDTH
from entities import Fish


class FishManager:
    """Owns all fish currently on screen.

    中文：使用 object pool 避免遊戲過程頻繁建立/銷毀魚物件，降低卡頓機率。
    English: Uses an object pool to avoid frequent fish allocation/destruction during gameplay, reducing stutter risk.
    """

    def __init__(self) -> None:
        self.pool = [Fish() for _ in range(MAX_FISH)]
        self.fishes: List[Fish] = []
        self.spawn_timer = FPS * 2

    def spawn_group(self) -> None:
        """Spawn one group of fish from either side of the screen.

        中文：魚種選擇偏向列表前段的小魚，偶爾才生成高價魚，讓畫面和賠率比較穩定。
        English: Fish selection is biased toward earlier low-value fish, with occasional high-value fish for steadier pacing and payouts.
        """
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
        """Update all fish and return total coins from finished captures.

        中文：離開畫面且已經出現過的魚會被回收；捕獲動畫完成的魚會回傳獎金。
        English: Fish that have left after appearing are recycled; fish with completed capture animations return their award.
        """
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
        """Build a coarse spatial grid for active uncaptured fish.

        中文：命中判定只檢查附近 3x3 格，避免每顆子彈都掃描全部魚。
        English: Hit checks only inspect nearby 3x3 cells instead of scanning every fish for every bullet.
        """
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
