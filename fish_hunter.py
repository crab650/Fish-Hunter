"""Command-line entry point for the game.

中文：這個檔案保持很薄，只把執行權交給 game.main()，讓主邏輯集中在 game.py。
English: This file stays thin and delegates execution to game.main(), keeping the main logic in game.py.
"""

from __future__ import annotations

from game import main


if __name__ == "__main__":
    raise SystemExit(main())
