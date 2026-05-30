"""Core moving game entities.

中文：定義魚、子彈和炮台的狀態、移動、動畫和繪製邏輯。
English: Defines state, movement, animation, and drawing logic for fish, bullets, and the cannon.
"""

from __future__ import annotations

import math
import random
from typing import Optional, Tuple

import pygame

from assets import Assets, RotationCache
from config import CANNON_X, CANNON_Y, FPS, HEIGHT, WIDTH, FishSpec, fish_reward


class Fish:
    """One active or pooled fish object.

    中文：魚會從物件池重複使用；reset() 套用魚種資料和初始位置，capture() 進入捕獲動畫。
    English: Fish instances are reused from a pool; reset() applies fish data and spawn position, while capture() starts the capture animation.
    """

    __slots__ = (
        "active",
        "spec",
        "x",
        "y",
        "speed",
        "angle",
        "dx",
        "dy",
        "frame",
        "tick",
        "captured",
        "capture_timer",
        "capture_duration",
        "capture_scale",
        "can_turn",
        "has_shown",
        "turn_timer",
        "dest_angle",
    )

    def __init__(self) -> None:
        self.active = False
        self.spec: Optional[FishSpec] = None
        self.x = 0.0
        self.y = 0.0
        self.speed = 0.0
        self.angle = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.frame = 0
        self.tick = 0
        self.captured = False
        self.capture_timer = 0
        self.capture_duration = FPS // 2
        self.capture_scale = 1.0
        self.can_turn = False
        self.has_shown = False
        self.turn_timer = 0
        self.dest_angle: Optional[float] = None

    @property
    def radius(self) -> float:
        assert self.spec is not None
        return min(self.spec.frame_w, self.spec.frame_h) * self.spec.radius_scale

    def reset(self, spec: FishSpec, x: float, y: float, speed: float, angle: float) -> None:
        self.active = True
        self.spec = spec
        self.x = x
        self.y = y
        self.speed = speed
        self.frame = random.randrange(spec.swim_frames)
        self.tick = 0
        self.captured = False
        self.capture_timer = 0
        self.capture_duration = FPS // 2
        self.capture_scale = 1.0
        self.can_turn = False
        self.has_shown = False
        self.dest_angle = None
        self.set_angle(angle)
        self.turn_timer = random.randint(FPS * 5, FPS * 10)

    def set_angle(self, angle: float) -> None:
        self.angle = angle % 360
        rad = math.radians(self.angle)
        self.dx = math.cos(rad) * self.speed
        self.dy = math.sin(rad) * self.speed

    def maybe_turn(self) -> None:
        """Occasionally choose a new heading while inside the play area.

        中文：讓魚群路徑不要完全直線，畫面會比較自然。
        English: Keeps fish movement from being perfectly straight so the scene feels more natural.
        """
        if random.random() > 0.80:
            direction = 1 if random.random() > 0.5 else -1
            self.dest_angle = self.angle + random.randint(20, 30) * direction
        self.turn_timer = random.randint(FPS * 5, FPS * 10)

    def update(self) -> Optional[int]:
        """Advance movement/animation and return a payout when capture finishes.

        中文：一般狀態會移動和轉向；被捕獲後縮小播放動畫，結束時回傳獎金。
        English: Normal fish move and turn; captured fish shrink through their animation and return the award when finished.
        """
        if not self.active or self.spec is None:
            return None

        self.tick += 1
        if self.tick % 10 == 0:
            if self.captured:
                self.frame = self.spec.swim_frames + (
                    (self.frame + 1 - self.spec.swim_frames) % self.spec.capture_frames
                )
            else:
                self.frame = (self.frame + 1) % self.spec.swim_frames

        if self.captured:
            self.capture_timer -= 1
            self.capture_scale = max(0.0, self.capture_timer / self.capture_duration)
            if self.capture_timer <= 0:
                coin = fish_reward(self.spec.coin)
                self.active = False
                return coin
            return None

        self.x += self.dx
        self.y += self.dy

        if self.dest_angle is not None:
            delta = (self.dest_angle - self.angle + 540) % 360 - 180
            if abs(delta) <= 0.2:
                self.set_angle(self.dest_angle)
                self.dest_angle = None
            else:
                self.set_angle(self.angle + (0.2 if delta > 0 else -0.2))
        elif self.can_turn:
            self.turn_timer -= 1
            if self.turn_timer <= 0:
                self.maybe_turn()

        if -self.spec.frame_w < self.x < WIDTH + self.spec.frame_w and -self.spec.frame_h < self.y < HEIGHT + self.spec.frame_h:
            self.has_shown = True
        if 100 < self.x < WIDTH - 100 and 100 < self.y < HEIGHT - 100:
            self.can_turn = True

        return None

    def is_out(self) -> bool:
        assert self.spec is not None
        margin = max(self.spec.frame_w, self.spec.frame_h) + 80
        return self.x < -margin or self.x > WIDTH + margin or self.y < -margin or self.y > HEIGHT + margin

    def capture(self) -> bool:
        if self.captured or self.spec is None:
            return False
        self.captured = True
        self.capture_duration = FPS // 2
        self.capture_timer = self.capture_duration
        self.capture_scale = 1.0
        self.frame = self.spec.swim_frames
        return True

    def draw(self, screen: pygame.Surface, assets: Assets, rotations: RotationCache) -> None:
        if not self.active or self.spec is None:
            return
        frame = assets.fish_frames[self.spec.name][self.frame]
        image = rotations.get(frame, -self.angle)
        if self.captured:
            width = max(1, int(image.get_width() * self.capture_scale))
            height = max(1, int(image.get_height() * self.capture_scale))
            image = pygame.transform.smoothscale(image, (width, height))
        rect = image.get_rect(center=(round(self.x), round(self.y)))
        screen.blit(image, rect)


class Bullet:
    """Projectile fired by the cannon.

    中文：子彈只負責直線飛行和繪製，命中判定由 Game 搭配 FishManager 的格子查詢處理。
    English: Bullets only handle straight movement and drawing; hit detection is handled by Game with FishManager's spatial grid.
    """

    __slots__ = ("active", "x", "y", "dx", "dy", "angle", "power")

    def __init__(self) -> None:
        self.active = False
        self.x = 0.0
        self.y = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.angle = 0.0
        self.power = 1

    def fire(self, x: float, y: float, dx: float, dy: float, angle: float, power: int) -> None:
        speed = 7.0
        self.active = True
        self.x = x
        self.y = y
        self.dx = dx * speed
        self.dy = dy * speed
        self.angle = angle
        self.power = power

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy
        if self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, screen: pygame.Surface, assets: Assets, rotations: RotationCache) -> None:
        if not self.active:
            return
        frame = assets.bullet_frames[self.power - 1]
        image = rotations.get(frame, -self.angle)
        screen.blit(image, image.get_rect(center=(round(self.x), round(self.y))))


class Cannon:
    """Player cannon at the bottom of the screen.

    中文：保存目前炮台等級、瞄準方向和開火動畫狀態。
    English: Stores the current cannon level, aim direction, and firing animation state.
    """

    def __init__(self) -> None:
        self.power = 1
        self.angle = 0.0
        self.aim_dx = 0.0
        self.aim_dy = -1.0
        self.x = CANNON_X
        self.y = CANNON_Y
        self.fire_frame = 0
        self.fire_ticks = 0

    def set_power(self, delta: int) -> None:
        self.power = ((self.power - 1 + delta) % 7) + 1

    def aim(self, target: Tuple[int, int]) -> None:
        tx, ty = target
        dx = tx - self.x
        dy = ty - self.y
        length = math.hypot(dx, dy)
        if length == 0:
            return
        self.aim_dx = dx / length
        self.aim_dy = dy / length
        self.angle = math.degrees(math.atan2(self.aim_dx, -self.aim_dy))

    def fire(self) -> None:
        self.fire_frame = 0
        self.fire_ticks = 12

    def draw(self, screen: pygame.Surface, assets: Assets, rotations: RotationCache) -> None:
        frames = assets.cannon_frames[self.power]
        if self.fire_ticks > 0:
            frame_index = min(len(frames) - 1, (12 - self.fire_ticks) // 3)
            self.fire_ticks -= 1
        else:
            frame_index = 0
        image = rotations.get(frames[frame_index], -self.angle)
        rect = image.get_rect(center=(self.x, self.y - 24))
        screen.blit(image, rect)
