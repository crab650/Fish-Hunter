from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple


class BusinessStats:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.days: Dict[str, Dict[str, int]] = {}
        self.load()
        self.ensure_today()

    @property
    def today_key(self) -> str:
        return date.today().isoformat()

    def ensure_today(self) -> Dict[str, int]:
        day = self.days.setdefault(
            self.today_key,
            {"inserted": 0, "wagered": 0, "paid": 0, "captures": 0},
        )
        self.trim()
        return day

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if isinstance(data, dict):
            self.days = {
                str(day): {
                    "inserted": int(values.get("inserted", 0)),
                    "wagered": int(values.get("wagered", 0)),
                    "paid": int(values.get("paid", 0)),
                    "captures": int(values.get("captures", 0)),
                }
                for day, values in data.items()
                if isinstance(values, dict)
            }

    def save(self) -> None:
        self.trim()
        self.path.write_text(json.dumps(self.days, indent=2), encoding="utf-8")

    def trim(self) -> None:
        keys = sorted(self.days.keys())
        for key in keys[:-5]:
            del self.days[key]

    def add(self, field: str, amount: int) -> None:
        day = self.ensure_today()
        day[field] = day.get(field, 0) + amount
        self.save()

    def reset_today(self) -> None:
        self.days[self.today_key] = {"inserted": 0, "wagered": 0, "paid": 0, "captures": 0}
        self.save()

    def reset_all(self) -> None:
        self.days = {}
        self.ensure_today()
        self.save()

    def recent_days(self) -> List[Tuple[str, Dict[str, int]]]:
        return [(key, self.days[key]) for key in sorted(self.days.keys(), reverse=True)[:5]]
