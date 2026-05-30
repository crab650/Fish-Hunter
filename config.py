"""Shared configuration and gameplay tuning tables.

中文：集中管理畫面尺寸、機台吐分率、炮台成本、魚種倍率和 sprite 切割資訊，方便之後調整玩法。
English: Centralizes screen size, payout-rate options, cannon costs, fish rewards, and sprite slicing data for easier gameplay tuning.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "images"
STATS_FILE = ROOT / "business_stats.json"

WIDTH = 980
HEIGHT = 545
FPS = 60
MAX_FISH = 100
FISH_CELL = 180

BOTTOM_BAR_WIDTH = 765
BOTTOM_X = (WIDTH - BOTTOM_BAR_WIDTH) // 2
BOTTOM_Y = HEIGHT - 70
CANNON_X = BOTTOM_X + 425
CANNON_Y = HEIGHT - 10
POWER_BUTTON_Y = BOTTOM_Y + 36
POWER_BUTTON_CENTER_OFFSET = 96

PAYOUT_RATE_OPTIONS = (0.60, 0.70, 0.80, 0.90, 0.96)
CANNON_COSTS = (5, 10, 15, 20, 25, 30, 40)
REWARD_SCALE = 5


def fish_reward(base_coin: int) -> int:
    """Convert a fish's base coin value into the actual payout.

    中文：高價魚使用更高倍率，讓大魚和鯊魚有明顯獎勵差距；REWARD_SCALE 可全域放大或縮小獎金。
    English: High-value fish use larger multipliers so big fish and sharks feel distinct; REWARD_SCALE adjusts all awards globally.
    """
    if base_coin >= 100:
        return base_coin * 8 * REWARD_SCALE
    if base_coin >= 50:
        return base_coin * 6 * REWARD_SCALE
    if base_coin >= 20:
        return base_coin * 4 * REWARD_SCALE
    if base_coin >= 10:
        return base_coin * 3 * REWARD_SCALE
    return base_coin * 2 * REWARD_SCALE


@dataclass(frozen=True)
class FishSpec:
    """Static data for one fish type.

    中文：包含素材檔名、每格尺寸、動畫幀數、基礎獎勵、基礎捕獲率、群組大小和移動速度。
    English: Holds asset name, frame size, animation counts, base reward, base capture rate, group size, and movement speed.
    """

    name: str
    file: str
    frame_w: int
    frame_h: int
    swim_frames: int
    capture_frames: int
    coin: int
    capture_rate: float
    max_group: int
    min_speed: float
    max_speed: float
    radius_scale: float = 0.35


FISH_SPECS: Tuple[FishSpec, ...] = (
    FishSpec("fish1", "fish1.png", 55, 37, 4, 4, 1, 0.55, 8, 0.5, 1.2),
    FishSpec("fish2", "fish2.png", 78, 64, 4, 4, 3, 0.50, 6, 0.5, 1.2),
    FishSpec("fish3", "fish3.png", 72, 56, 4, 4, 5, 0.45, 6, 0.5, 1.2),
    FishSpec("fish4", "fish4.png", 77, 59, 4, 4, 8, 0.40, 6, 0.5, 1.2),
    FishSpec("fish5", "fish5.png", 107, 122, 4, 4, 10, 0.35, 5, 0.5, 1.2),
    FishSpec("fish6", "fish6.png", 105, 79, 8, 4, 20, 0.30, 3, 0.5, 1.2),
    FishSpec("fish8", "fish8.png", 174, 126, 8, 4, 40, 0.20, 3, 0.5, 0.8),
    FishSpec("fish9", "fish9.png", 166, 183, 8, 4, 50, 0.15, 2, 0.5, 0.8),
    FishSpec("fish10", "fish10.png", 178, 187, 6, 4, 60, 0.10, 2, 0.5, 0.8),
    FishSpec("fish7", "fish7.png", 92, 151, 6, 4, 30, 0.25, 5, 0.5, 0.8),
    FishSpec("shark1", "shark1.png", 509, 270, 8, 4, 100, 0.05, 1, 0.5, 0.6, 0.28),
    FishSpec("shark2", "shark2.png", 516, 273, 8, 4, 200, 0.02, 1, 0.5, 0.6, 0.28),
)


@dataclass(frozen=True)
class CannonSpec:
    """Static data for one cannon level.

    中文：不同炮台等級對應不同圖片、動畫幀數和 power 值。
    English: Each cannon level maps to its image, animation frame count, and power value.
    """

    file: str
    frame_w: int
    frame_h: int
    frames: int
    power: int


CANNON_SPECS: Tuple[CannonSpec, ...] = (
    CannonSpec("cannon1.png", 74, 74, 5, 1),
    CannonSpec("cannon2.png", 74, 76, 5, 2),
    CannonSpec("cannon3.png", 74, 76, 5, 3),
    CannonSpec("cannon4.png", 74, 83, 5, 4),
    CannonSpec("cannon5.png", 74, 85, 5, 5),
    CannonSpec("cannon6.png", 74, 90, 5, 6),
    CannonSpec("cannon7.png", 74, 94, 5, 7),
)

BULLET_RECTS: Tuple[Tuple[int, int, int, int], ...] = (
    (86, 0, 24, 26),
    (61, 0, 25, 29),
    (32, 35, 27, 31),
    (30, 82, 29, 33),
    (0, 82, 30, 34),
    (30, 0, 31, 35),
    (0, 44, 32, 38),
)

WEB_RECTS: Tuple[Tuple[int, int, int, int], ...] = (
    (319, 355, 116, 118),
    (0, 399, 137, 142),
    (163, 355, 156, 162),
    (242, 181, 180, 174),
    (0, 244, 163, 155),
    (242, 0, 191, 181),
    (0, 0, 242, 244),
)
