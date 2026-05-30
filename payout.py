from __future__ import annotations

import random

from config import FishSpec, fish_reward


class PayoutController:
    def __init__(self, target_rate: float = 0.80) -> None:
        self.target_rate = target_rate
        self.total_wagered = 0
        self.total_paid = 0
        self.pending_awards = 0

    @property
    def available_return(self) -> float:
        return self.total_wagered * self.target_rate - self.total_paid - self.pending_awards

    def record_wager(self, amount: int) -> None:
        self.total_wagered += amount

    def reserve_award(self, amount: int) -> None:
        self.pending_awards += amount

    def record_paid(self, amount: int) -> None:
        self.total_paid += amount
        self.pending_awards = max(0, self.pending_awards - amount)

    def capture_chance(self, spec: FishSpec, power: int) -> float:
        reward = fish_reward(spec.coin)
        if self.total_wagered <= 0 or reward <= 0:
            return 0.0

        base_chance = spec.capture_rate * (1.0 + (power - 1) * 0.04)
        budget_ratio = self.available_return / reward
        if budget_ratio <= 0:
            budget_factor = 0.02
        elif budget_ratio < 1:
            budget_factor = max(0.04, budget_ratio ** 1.35)
        else:
            budget_factor = min(1.35, 1.0 + (budget_ratio - 1.0) * 0.18)

        max_chance = 0.62 if spec.coin < 10 else 0.42 if spec.coin < 50 else 0.22
        return max(0.0, min(max_chance, base_chance * budget_factor))

    def should_capture(self, spec: FishSpec, power: int) -> bool:
        return random.random() < self.capture_chance(spec, power)

    def reset(self) -> None:
        self.total_wagered = 0
        self.total_paid = 0
        self.pending_awards = 0
