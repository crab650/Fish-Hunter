from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import pygame

from config import (
    ASSET_DIR,
    BULLET_RECTS,
    CANNON_SPECS,
    FISH_SPECS,
    HEIGHT,
    WEB_RECTS,
    WIDTH,
)


def load_image(name: str, alpha: bool = True) -> pygame.Surface:
    path = ASSET_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    image = pygame.image.load(str(path))
    return image.convert_alpha() if alpha else image.convert()


def load_ui_font(size: int, bold: bool = True) -> pygame.font.Font:
    for name in ("microsoftjhenghei", "msjh", "mingliu", "pmingliu", "simhei", "arialunicode"):
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont("arial", size, bold=bold)


def slice_vertical(sheet: pygame.Surface, w: int, h: int, count: int) -> List[pygame.Surface]:
    return [sheet.subsurface((0, i * h, w, h)).copy() for i in range(count)]


def slice_rects(sheet: pygame.Surface, rects: Iterable[Tuple[int, int, int, int]]) -> List[pygame.Surface]:
    return [sheet.subsurface(rect).copy() for rect in rects]


class RotationCache:
    def __init__(self, step: int = 4) -> None:
        self.step = step
        self.cache: Dict[Tuple[int, int], pygame.Surface] = {}

    def get(self, surface: pygame.Surface, degrees: float) -> pygame.Surface:
        bucket = int(round(degrees / self.step) * self.step) % 360
        key = (id(surface), bucket)
        rotated = self.cache.get(key)
        if rotated is None:
            rotated = pygame.transform.rotate(surface, bucket)
            self.cache[key] = rotated
        return rotated


class Assets:
    def __init__(self) -> None:
        self.background = pygame.transform.smoothscale(load_image("game_bg_2_hd.jpg", False), (WIDTH, HEIGHT))
        self.bottom = load_image("bottom.png")
        self.num_digits = self._load_number_digits()
        self.coin_anims = {
            "small": slice_vertical(load_image("coinAni1.png"), 60, 60, 10),
            "large": slice_vertical(load_image("coinAni2.png"), 60, 60, 10),
        }
        self.bullet_frames = slice_rects(load_image("bullet.png"), BULLET_RECTS)
        self.web_frames = slice_rects(load_image("web.png"), WEB_RECTS)
        self.fish_frames: Dict[str, List[pygame.Surface]] = {}
        self.cannon_frames: Dict[int, List[pygame.Surface]] = {}
        self.plus_up = self.bottom.subsurface((44, 72, 44, 31)).copy()
        self.plus_down = self.bottom.subsurface((0, 72, 44, 31)).copy()
        self.minus_up = self.bottom.subsurface((132, 72, 44, 31)).copy()
        self.minus_down = self.bottom.subsurface((88, 72, 44, 31)).copy()

        for spec in FISH_SPECS:
            total = spec.swim_frames + spec.capture_frames
            self.fish_frames[spec.name] = slice_vertical(load_image(spec.file), spec.frame_w, spec.frame_h, total)

        for spec in CANNON_SPECS:
            self.cannon_frames[spec.power] = slice_vertical(
                load_image(spec.file), spec.frame_w, spec.frame_h, spec.frames
            )

    def _load_number_digits(self) -> Dict[str, pygame.Surface]:
        sheet = load_image("number_black.png")
        digits: Dict[str, pygame.Surface] = {}
        for index, digit in enumerate("9876543210"):
            digits[digit] = sheet.subsurface((0, index * 24, 20, 24)).copy()
        return digits
