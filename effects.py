from __future__ import annotations

import math

import pygame

from assets import Assets


class WebEffect:
    __slots__ = ("x", "y", "power", "age", "duration")

    def __init__(self, x: float, y: float, power: int) -> None:
        self.x = x
        self.y = y
        self.power = power
        self.age = 0
        self.duration = 14

    @property
    def done(self) -> bool:
        return self.age >= self.duration

    def draw(self, screen: pygame.Surface, assets: Assets) -> None:
        frame = assets.web_frames[self.power - 1]
        scale = 0.8 + 0.25 * math.sin((self.age / self.duration) * math.pi)
        w = max(1, int(frame.get_width() * scale))
        h = max(1, int(frame.get_height() * scale))
        image = pygame.transform.smoothscale(frame, (w, h))
        screen.blit(image, image.get_rect(center=(round(self.x), round(self.y))))
        self.age += 1


class FloatingScore:
    __slots__ = ("x", "y", "value", "age", "duration")

    def __init__(self, x: float, y: float, value: int) -> None:
        self.x = x
        self.y = y
        self.value = value
        self.age = 0
        self.duration = 78

    @property
    def done(self) -> bool:
        return self.age >= self.duration

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        progress = self.age / self.duration
        y = self.y - progress * 62
        alpha = max(0, min(255, int(255 * (1.0 - progress))))
        text = font.render(f"+{self.value}", True, (255, 234, 72))
        text.set_alpha(alpha)
        shadow = font.render(f"+{self.value}", True, (60, 35, 0))
        shadow.set_alpha(alpha)
        rect = text.get_rect(center=(round(self.x), round(y)))
        screen.blit(shadow, rect.move(2, 2))
        screen.blit(text, rect)
        self.age += 1


class CoinEffect:
    __slots__ = ("x", "y", "large", "age", "duration")

    def __init__(self, x: float, y: float, value: int) -> None:
        self.x = x
        self.y = y
        self.large = value >= 30
        self.age = 0
        self.duration = 90

    @property
    def done(self) -> bool:
        return self.age >= self.duration

    def draw(self, screen: pygame.Surface, assets: Assets) -> None:
        frames = assets.coin_anims["large" if self.large else "small"]
        frame = frames[(self.age // 4) % len(frames)]
        progress = self.age / self.duration
        scale = 0.95 + 0.35 * math.sin(progress * math.pi)
        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        image = pygame.transform.smoothscale(frame, (width, height))
        y = self.y - progress * 48
        image.set_alpha(max(0, min(255, int(255 * (1.0 - progress * 0.25)))))
        screen.blit(image, image.get_rect(center=(round(self.x), round(y))))
        self.age += 1
