import re
import secrets

from .parsing import CommandError

MAX_COINS = 100


def roll_coins(arguments: str, card: dict[str, int], player: str) -> str:
    target = arguments.strip()
    if target.startswith("+"):
        target = target[1:].strip()
    if not target:
        raise CommandError("请提供属性名或硬币数量。例：.c力量 或 .c2")
    if re.fullmatch(r"[0-9]+", target):
        count = int(target)
    elif target in card:
        count = card[target]
    else:
        raise CommandError(f"未发现属性“{target}”，请先用 .st{target}数值 录入。")
    if not 0 <= count <= MAX_COINS:
        raise CommandError(f"硬币数量须为 0–{MAX_COINS} 的整数。")
    results = [secrets.randbelow(2) for _ in range(count)]
    faces = "".join("●" if value else "○" for value in results) or "（未投掷硬币）"
    return f"{player}进行了“{target}”检定：\n{faces} -> {sum(results)}"
