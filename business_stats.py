"""Five-day machine business statistics storage.

中文：用 JSON 保存最近五天的投幣、子彈投入、吐分和捕獲數，供 F2 設定畫面顯示。
English: Stores the latest five days of inserted coins, wagered shots, payouts, and captures for the F2 setup screen.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple


class BusinessStats:
    """Small JSON-backed daily counter store.

    中文：資料量很小，所以直接讀寫整個 JSON 檔；每次更新後都保存，避免遊戲關閉時遺失帳務。
    English: The data is tiny, so the whole JSON file is read/written directly; every update is saved to avoid losing accounting data.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.days: Dict[str, Dict[str, int]] = {}
        self.load()
        self.ensure_today()

    @property
    def today_key(self) -> str:
        return date.today().isoformat()

    def ensure_today(self) -> Dict[str, int]:
        """Return today's row, creating it when needed.

        中文：所有統計欄位都用 0 起始，讓 UI 可以安全讀取。
        English: Initializes every counter to 0 so the UI can read fields safely.
        """
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
        """Keep only the newest five dates.

        中文：F2 畫面只顯示五天資料，舊資料會被移除以保持檔案簡單。
        English: The F2 screen only displays five days, so older rows are removed to keep the file simple.
        """
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
