from __future__ import annotations

import pygame

from config import (
    BOTTOM_X,
    BOTTOM_Y,
    CANNON_COSTS,
    CANNON_X,
    PAYOUT_RATE_OPTIONS,
    WIDTH,
    HEIGHT,
)


def draw_bottom_ui(game: object) -> None:
    bottom = game.assets.bottom.subsurface((0, 0, 765, 72)).copy()
    game.screen.blit(bottom, (BOTTOM_X, BOTTOM_Y))
    mouse_down = pygame.mouse.get_pressed()[0]
    mouse_pos = pygame.mouse.get_pos()
    plus = game.assets.plus_down if mouse_down and game.plus_rect.collidepoint(mouse_pos) else game.assets.plus_up
    minus = game.assets.minus_down if mouse_down and game.minus_rect.collidepoint(mouse_pos) else game.assets.minus_up
    game.screen.blit(minus, game.minus_rect)
    game.screen.blit(plus, game.plus_rect)

    draw_coin_digits(game, BOTTOM_X + 20, BOTTOM_Y + 42)
    power_text = game.small_font.render(
        f"Lv {game.cannon.power}  -{CANNON_COSTS[game.cannon.power - 1]}",
        True,
        (255, 245, 180),
    )
    game.screen.blit(power_text, power_text.get_rect(center=(CANNON_X, BOTTOM_Y + 50)))
    capture_text = game.small_font.render(f"Captured {game.captured}", True, (255, 255, 255))
    game.screen.blit(capture_text, (14, 12))


def draw_coin_digits(game: object, x: int, y: int) -> None:
    text = f"{game.coins:06d}"[-6:]
    for index, digit in enumerate(text):
        game.screen.blit(game.assets.num_digits[digit], (x + index * 23, y))


def draw_config_overlay(game: object) -> None:
    panel = pygame.Rect(26, 22, WIDTH - 52, HEIGHT - 44)
    pygame.draw.rect(game.screen, (0, 0, 120), panel)
    pygame.draw.rect(game.screen, (112, 214, 255), panel, width=3)
    pygame.draw.rect(game.screen, (0, 0, 45), panel.inflate(-18, -18), width=2)

    today = game.stats.ensure_today()
    available = game.payout.available_return
    total_wagered = game.payout.total_wagered
    total_paid = game.payout.total_paid
    target_return = total_wagered * game.payout.target_rate
    house_hold = total_wagered - total_paid - game.payout.pending_awards
    actual_rate = (total_paid / total_wagered * 100) if total_wagered else 0.0

    lines = [
        ("捕魚機台 BIOS 設定畫面", (255, 255, 80)),
        ("=" * 28, (112, 214, 255)),
        (f"目標吐分率      : {game.payout.target_rate * 100:5.1f}%   < 左右鍵調整 >", (210, 255, 210)),
        (f"可選：{' / '.join(str(int(rate * 100)) for rate in PAYOUT_RATE_OPTIONS)}", (112, 214, 255)),
        (f"子彈投入金額    : {total_wagered:8d}", (255, 255, 255)),
        (f"已吐分金額      : {total_paid:8d}", (255, 255, 255)),
        (f"保留未入帳獎金  : {game.payout.pending_awards:8d}", (255, 255, 255)),
        (f"目前可吐額度    : {available:8.1f}", (255, 255, 255)),
        (f"目標應吐金額    : {target_return:8.1f}", (255, 255, 255)),
        (f"實際吐分率      : {actual_rate:7.2f}%", (255, 255, 255)),
        (f"店家保留估算    : {house_hold:8.1f}", (255, 220, 180)),
        ("", (255, 255, 255)),
        (f"玩家目前錢包    : {game.coins:8d}", (255, 255, 255)),
        (f"本輪捕魚數      : {game.captured:8d}", (255, 255, 255)),
        (f"魚 / 子彈數     : {len(game.fish_manager.fishes):3d} / {sum(b.active for b in game.bullets):2d}", (255, 255, 255)),
        (f"今日投幣        : {today.get('inserted', 0):8d}", (210, 255, 210)),
        (f"今日子彈投入    : {today.get('wagered', 0):8d}", (210, 255, 210)),
        (f"今日吐分        : {today.get('paid', 0):8d}", (210, 255, 210)),
        (f"今日捕獲        : {today.get('captures', 0):8d}", (210, 255, 210)),
    ]

    x = panel.x + 28
    y = panel.y + 24
    for text, color in lines:
        if text:
            game.screen.blit(game.bios_font.render(text, True, color), (x, y))
        y += 20

    table_x = panel.x + 510
    table_y = panel.y + 64
    game.screen.blit(game.bios_font.render("最近五天業績", True, (255, 255, 80)), (table_x, table_y))
    table_y += 28
    headers = "日期     投幣   投入   吐分  捕獲  保留"
    game.screen.blit(game.bios_small_font.render(headers, True, (112, 214, 255)), (table_x, table_y))
    table_y += 22
    for day, values in game.stats.recent_days():
        inserted = values.get("inserted", 0)
        wagered = values.get("wagered", 0)
        paid = values.get("paid", 0)
        captures = values.get("captures", 0)
        hold = wagered - paid
        row = f"{day[-5:]} {inserted:5d} {wagered:5d} {paid:5d} {captures:4d} {hold:5d}"
        game.screen.blit(game.bios_small_font.render(row, True, (255, 255, 255)), (table_x, table_y))
        table_y += 20

    help_lines = [
        "F2 / ESC：回到遊戲",
        "← / →  ：調整目標吐分率 60/70/80/90/96",
        "C       ：清零今日與目前機台帳本",
        "R       ：清除五天業績紀錄",
    ]
    help_y = panel.bottom - 88
    for item in help_lines:
        game.screen.blit(game.bios_small_font.render(item, True, (255, 255, 80)), (x, help_y))
        help_y += 18
