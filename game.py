from __future__ import annotations

import sys
from typing import Dict, List, Tuple

import pygame

from assets import Assets, RotationCache, load_ui_font
from business_stats import BusinessStats
from config import (
    ASSET_DIR,
    CANNON_COSTS,
    CANNON_X,
    FPS,
    HEIGHT,
    PAYOUT_RATE_OPTIONS,
    POWER_BUTTON_CENTER_OFFSET,
    POWER_BUTTON_Y,
    STATS_FILE,
    WIDTH,
    fish_reward,
)
from effects import CoinEffect, FloatingScore, WebEffect
from entities import Bullet, Cannon, Fish
from fish_manager import FishManager
from payout import PayoutController
from ui import draw_bottom_ui, draw_config_overlay


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Fish Hunter Python")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18, bold=True)
        self.bios_font = load_ui_font(19)
        self.bios_small_font = load_ui_font(15)
        self.assets = Assets()
        self.rotations = RotationCache()
        self.fish_manager = FishManager()
        self.fish_manager.spawn_group()
        self.cannon = Cannon()
        self.bullets = [Bullet() for _ in range(32)]
        self.webs: List[WebEffect] = []
        self.floating_scores: List[FloatingScore] = []
        self.coin_effects: List[CoinEffect] = []
        self.payout = PayoutController(target_rate=0.80)
        self.stats = BusinessStats(STATS_FILE)
        self.config_open = False
        self.coins = 0
        self.captured = 0
        self.fire_cooldown = 0
        self.minus_rect = pygame.Rect(
            CANNON_X - POWER_BUTTON_CENTER_OFFSET - 22,
            POWER_BUTTON_Y,
            44,
            31,
        )
        self.plus_rect = pygame.Rect(
            CANNON_X + POWER_BUTTON_CENTER_OFFSET - 22,
            POWER_BUTTON_Y,
            44,
            31,
        )
        self.running = True

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.config_open:
                        self.config_open = False
                    else:
                        self.running = False
                elif event.key == pygame.K_F2:
                    self.config_open = not self.config_open
                elif self.config_open:
                    if event.key == pygame.K_c:
                        self.reset_machine_accounting()
                    elif event.key == pygame.K_r:
                        self.stats.reset_all()
                        self.reset_machine_accounting()
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.adjust_payout_rate(1 if event.key == pygame.K_RIGHT else -1)
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.cannon.set_power(1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.cannon.set_power(-1)
                elif event.key == pygame.K_F1:
                    self.coins = min(999999, self.coins + 50)
                    self.stats.add("inserted", 50)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.config_open:
                    continue
                if self.plus_rect.collidepoint(event.pos):
                    self.cannon.set_power(1)
                elif self.minus_rect.collidepoint(event.pos):
                    self.cannon.set_power(-1)
                else:
                    self.try_fire(event.pos)

    def try_fire(self, target: Tuple[int, int]) -> None:
        shot_cost = CANNON_COSTS[self.cannon.power - 1]
        if self.fire_cooldown > 0 or self.coins < shot_cost:
            return
        bullet = next((item for item in self.bullets if not item.active), None)
        if bullet is None:
            return
        self.cannon.aim(target)
        self.cannon.fire()
        start_x = self.cannon.x + self.cannon.aim_dx * 58
        start_y = self.cannon.y + self.cannon.aim_dy * 58
        bullet.fire(start_x, start_y, self.cannon.aim_dx, self.cannon.aim_dy, self.cannon.angle, self.cannon.power)
        self.coins -= shot_cost
        self.payout.record_wager(shot_cost)
        self.stats.add("wagered", shot_cost)
        self.fire_cooldown = 8

    def update(self) -> None:
        if self.config_open:
            return
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        earned = self.fish_manager.update()
        if earned:
            self.coins = min(999999, self.coins + earned)
            self.payout.record_paid(earned)
            self.stats.add("paid", earned)
        grid = self.fish_manager.build_grid()
        for bullet in self.bullets:
            if not bullet.active:
                continue
            bullet.update()
            if not bullet.active:
                continue
            if self.bullet_hit(bullet, grid):
                self.release_web(bullet, grid)
                bullet.active = False

        self.webs = [web for web in self.webs if not web.done]
        self.floating_scores = [score for score in self.floating_scores if not score.done]
        self.coin_effects = [coin for coin in self.coin_effects if not coin.done]

    def bullet_hit(self, bullet: Bullet, grid: Dict[Tuple[int, int], List[Fish]]) -> bool:
        bullet_radius = 8 + bullet.power * 2
        for fish in self.fish_manager.nearby(bullet.x, bullet.y, grid):
            dist2 = (fish.x - bullet.x) ** 2 + (fish.y - bullet.y) ** 2
            if dist2 <= (fish.radius + bullet_radius) ** 2:
                return True
        return False

    def release_web(self, bullet: Bullet, grid: Dict[Tuple[int, int], List[Fish]]) -> None:
        self.webs.append(WebEffect(bullet.x, bullet.y, bullet.power))
        radius = 48 + bullet.power * 17
        for fish in self.fish_manager.nearby(bullet.x, bullet.y, grid):
            dist2 = (fish.x - bullet.x) ** 2 + (fish.y - bullet.y) ** 2
            if fish.spec is None:
                continue
            if dist2 <= (fish.radius + radius) ** 2 and self.payout.should_capture(fish.spec, bullet.power):
                score = fish_reward(fish.spec.coin)
                self.payout.reserve_award(score)
                fish.capture()
                self.captured += 1
                self.stats.add("captures", 1)
                self.floating_scores.append(FloatingScore(fish.x, fish.y - fish.radius, score))
                self.coin_effects.append(CoinEffect(fish.x, fish.y, score))

    def reset_machine_accounting(self) -> None:
        self.payout.reset()
        self.captured = 0
        self.stats.reset_today()

    def adjust_payout_rate(self, direction: int) -> None:
        current = min(
            range(len(PAYOUT_RATE_OPTIONS)),
            key=lambda index: abs(PAYOUT_RATE_OPTIONS[index] - self.payout.target_rate),
        )
        next_index = max(0, min(len(PAYOUT_RATE_OPTIONS) - 1, current + direction))
        self.payout.target_rate = PAYOUT_RATE_OPTIONS[next_index]

    def draw(self) -> None:
        self.screen.blit(self.assets.background, (0, 0))
        self.fish_manager.draw(self.screen, self.assets, self.rotations)
        for bullet in self.bullets:
            bullet.draw(self.screen, self.assets, self.rotations)
        if not self.config_open:
            for web in self.webs:
                web.draw(self.screen, self.assets)
            for coin in self.coin_effects:
                coin.draw(self.screen, self.assets)
            for score in self.floating_scores:
                score.draw(self.screen, self.font)
        draw_bottom_ui(self)
        self.cannon.draw(self.screen, self.assets, self.rotations)
        if self.config_open:
            draw_config_overlay(self)
        pygame.display.flip()


def main() -> int:
    if not ASSET_DIR.exists():
        print(f"Asset folder not found: {ASSET_DIR}", file=sys.stderr)
        return 1
    Game().run()
    return 0
