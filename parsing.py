import ast
import operator
import re
from dataclasses import dataclass
from fractions import Fraction

MAX_VALUE = 1_000_000
MAX_INPUT = 2000
NAME = re.compile(r"[^\W\d]+", re.UNICODE)
EXPRESSION = re.compile(r"[0-9+\-*/()%\s]+")
COMMAND_PATTERN = r"(?is)^[.。](character|char|ch|角色|pc|st|c)(.*)$"
COMMAND = re.compile(COMMAND_PATTERN)


class CommandError(ValueError):
    pass


@dataclass(frozen=True)
class Update:
    name: str
    relative: bool
    expression: str
    value: int


def command_parts(text: str) -> tuple[str, str] | None:
    match = COMMAND.fullmatch(text.strip())
    if not match:
        return None
    if len(text) > MAX_INPUT:
        raise CommandError(f"指令过长，请限制在 {MAX_INPUT} 字符内。")
    command = match[1].lower()
    if command in ("character", "char", "ch", "角色"):
        command = "pc"
    return command, match[2].strip()


def evaluate(expression: str) -> int:
    if len(expression) > 128:
        raise CommandError("表达式过长。")
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise CommandError("表达式格式错误。") from exc
    if len(list(ast.walk(tree))) > 64:
        raise CommandError("表达式过于复杂。")
    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
    }

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            value = Fraction(node.value)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            if isinstance(node.op, ast.USub):
                value = -value
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](visit(node.left), visit(node.right))
        else:
            raise CommandError("表达式仅支持整数、括号和 + - * / // %。")
        if abs(value) > MAX_VALUE:
            raise CommandError(f"表达式中间值和属性值不能超过 ±{MAX_VALUE}。")
        return value

    try:
        result = Fraction(visit(tree.body))
    except ZeroDivisionError as exc:
        raise CommandError("表达式不能除以零。") from exc
    if result.denominator != 1:
        raise CommandError("属性值和增减值必须是整数。")
    return int(result)


def parse_updates(text: str) -> list[Update]:
    updates = []
    position = 0
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        name = NAME.match(text, position)
        if not name or len(name[0]) > 32:
            raise CommandError("属性名限 1–32 个汉字、字母或下划线，不含数字和空格。")
        position = name.end()
        expression = EXPRESSION.match(text, position)
        if not expression or not expression[0].strip():
            raise CommandError(f"属性“{name[0]}”缺少数值。例：.st力量6体质4")
        raw = expression[0].strip()
        relative = raw.startswith(("+", "-"))
        value = evaluate(raw[1:].strip() if relative else raw)
        if relative and raw[0] == "-":
            value = -value
        updates.append(Update(name[0], relative, raw, value))
        position = expression.end()
    if not updates:
        raise CommandError("请提供属性和值。例：.st力量6体质4")
    return updates


def select_names(text: str, card: dict[str, int]) -> list[str]:
    selected = []
    for token in text.split():
        if token in card:
            selected.append(token)
            continue
        paths: dict[int, list[list[str]]] = {0: [[]]}
        for offset in range(len(token)):
            for path in paths.get(offset, []):
                for name in card:
                    if token.startswith(name, offset):
                        end = offset + len(name)
                        target = paths.setdefault(end, [])
                        if len(target) < 2:
                            target.append(path + [name])
        matches = paths.get(len(token), [])
        if len(matches) > 1:
            raise CommandError(f"“{token}”有多种属性拆分方式，请用空格分隔。")
        selected.extend(matches[0] if matches else [token])
    return list(dict.fromkeys(selected))
