"""Payout-rate and capture-probability controller.

中文：這裡是機率核心，會根據目標吐分率、已投入、已吐分和保留獎金，動態調整魚被捕獲的機率。
English: This is the probability core; it adjusts capture chance from target payout rate, total wagered, paid amount, and reserved awards.
"""

from __future__ import annotations

import random

from config import FishSpec, fish_reward


class PayoutController:
    """Track machine accounting and convert it into capture odds.

    中文：玩家射出的子彈才算投入；魚被捕獲時先保留獎金，動畫結束實際入帳後再轉成已吐分。
    English: Only fired shots count as input; captured awards are reserved first, then moved to paid when the animation finishes.
    """

    def __init__(self, target_rate: float = 0.80) -> None:
        self.target_rate = target_rate
        self.total_wagered = 0
        self.total_paid = 0
        self.pending_awards = 0

    @property
    def available_return(self) -> float:
        """Current payout budget allowed by the selected target rate.

        中文：可吐額度越高，高獎勵魚越容易被捕獲；可吐額度不足時機率會被壓低。
        English: A higher available budget makes expensive fish easier to catch; low budget suppresses their odds.
        """
        return self.total_wagered * self.target_rate - self.total_paid - self.pending_awards

    def record_wager(self, amount: int) -> None:
        self.total_wagered += amount

    def reserve_award(self, amount: int) -> None:
        self.pending_awards += amount

    def record_paid(self, amount: int) -> None:
        self.total_paid += amount
        self.pending_awards = max(0, self.pending_awards - amount)

    def capture_chance(self, spec: FishSpec, power: int) -> float:
        """Calculate the final capture chance for one fish.

        中文：基礎捕獲率來自魚種，炮台等級提供小幅加成，吐分預算再決定是否放大或壓低機率。
        English: Base odds come from the fish type, cannon power adds a small boost, and payout budget raises or lowers the final chance.
        """
        reward = fish_reward(spec.coin)
        if self.total_wagered <= 0 or reward <= 0:
            return 0.0

        # 中文：高等炮台不是保證中獎，只是讓同一條魚的基礎機率略微提高。
        # English: Higher cannon levels do not guarantee awards; they only slightly improve the base odds.
        base_chance = spec.capture_rate * (1.0 + (power - 1) * 0.04)
        budget_ratio = self.available_return / reward
        if budget_ratio <= 0:
            budget_factor = 0.02
        elif budget_ratio < 1:
            budget_factor = max(0.04, budget_ratio ** 1.35)
        else:
            budget_factor = min(1.35, 1.0 + (budget_ratio - 1.0) * 0.18)

        # 中文：不同價值魚有不同機率上限，避免高價魚在預算充足時變得太容易中。
        # English: Different value tiers have different caps so expensive fish do not become too easy when budget is high.
        max_chance = 0.62 if spec.coin < 10 else 0.42 if spec.coin < 50 else 0.22
        return max(0.0, min(max_chance, base_chance * budget_factor))

    def should_capture(self, spec: FishSpec, power: int) -> bool:
        return random.random() < self.capture_chance(spec, power)

    def reset(self) -> None:
        self.total_wagered = 0
        self.total_paid = 0
        self.pending_awards = 0
