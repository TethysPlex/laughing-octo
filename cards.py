import re

from .parsing import MAX_VALUE, CommandError, parse_updates, select_names

MAX_ATTRIBUTES = 100
HELP = """属性修改指令：
.st show — 展示个人属性（.st 也可）
.st show <属性1> <属性2> ... — 展示指定属性
.st show <数字> — 展示严格高于该值的属性
.st clr — 清空自己的属性
.st del <属性1> <属性2> ... — 删除指定属性
.st help — 显示帮助
.st <属性><值> — 例：.st力量6体质4
.st <属性>±<表达式> — 例：.st敏捷+2 或 .st力量-(2+3)
判定指令：
.c<属性或数量> — 例：.c力量、.c2（也支持 .c+力量、.c+2）
● 为正面（1），○ 为反面（0）"""


def handle_st(
    arguments: str, card: dict[str, int], player: str, *, bound: bool = False,
) -> tuple[str, dict]:
    result = dict(card)
    lowered = arguments.lower()
    if not arguments:
        branch, rest = "show", ""
    else:
        branch, rest = "", arguments
        for keyword in ("show", "help", "clr", "del"):
            if lowered.startswith(keyword):
                branch, rest = keyword, arguments[len(keyword):].strip()
                break
    if branch == "help":
        if rest:
            raise CommandError("帮助指令不接受参数，请使用 .st help。")
        return HELP, result
    if branch == "clr":
        if rest:
            raise CommandError("清空指令不接受参数，请使用 .st clr。")
        return f"{player}的属性数据已经清除，共计{len(card)}条", {}
    if branch == "show":
        if not rest:
            lines = [f"{name}:{value}" for name, value in card.items()]
        elif re.fullmatch(r"[+-]?[0-9]+", rest):
            threshold = int(rest)
            lines = [f"{name}:{value}" for name, value in card.items() if value > threshold]
        else:
            lines = [
                f"{name}:{card[name]}" if name in card else f"{name}:未发现属性记录"
                for name in select_names(rest, card)
            ]
        info = "\n".join(lines) or "未发现属性记录"
        return f"{player}的个人属性为:\n{info}", result
    if branch == "del":
        if not rest:
            raise CommandError("请提供要删除的属性。例：.stdel力量 体质")
        names = select_names(rest, card)
        removed = [name for name in names if name in card]
        for name in removed:
            del result[name]
        return (
            f"{player}的如下属性被成功删除:{' '.join(removed) or '无'}，"
            f"失败{len(names) - len(removed)}项",
            result,
        )

    changes = []
    assigned = 0
    for update in parse_updates(arguments):
        old = result.get(update.name, 0)
        new = old + update.value if update.relative else update.value
        if abs(new) > MAX_VALUE:
            raise CommandError(f"属性值不能超过 ±{MAX_VALUE}。")
        result[update.name] = new
        if update.relative:
            verb = "增加" if update.value >= 0 else "扣除"
            changes.append(
                f"{update.name}: {old} ➯ {new} "
                f"({verb}{update.expression}={abs(update.value)})"
            )
        else:
            assigned += 1
    if len(result) > MAX_ATTRIBUTES:
        raise CommandError(f"每张卡最多保存 {MAX_ATTRIBUTES} 项属性。")
    replies = []
    if assigned:
        replies.append(f"{player}的属性录入完成，本次录入了{assigned}条数据")
    if changes:
        replies.append(f"{player}的属性变化:\n" + "\n".join(changes))
        if bound:
            replies.append("[√] 已绑卡")
    return "\n".join(replies), result
