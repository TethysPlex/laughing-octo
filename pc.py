import re

from . import pc_text as text
from .characters import CharacterBook

BRANCHES = ("list", "lst", "load", "save", "del", "rm", "new", "tag", "untagall", "rename")


def split_pc(arguments: str) -> tuple[str, str]:
    for branch in BRANCHES:
        if arguments.lower().startswith(branch):
            return branch, arguments[len(branch):].strip()
    return "help", ""


def nickname(book: CharacterBook, raw: str, fallback: str = "", index=True) -> str:
    """Resolve one-based indices before names, as SeaDice's getNicknameRaw does."""
    if index and re.fullmatch(r"[+-]?[0-9]+", raw):
        number = int(raw)
        if 0 < number <= len(book.characters):
            return book.characters[number - 1]["name"]
    name = (raw or fallback).replace("\n", "").replace("\r", "")
    # SeaDice limits names to 90 bytes. Avoid cutting a UTF-8 code point in half.
    return name.encode("utf-8")[:90].decode("utf-8", errors="ignore")


def rename(book: CharacterBook, key: str, arguments: str) -> str:
    words = arguments.split()
    if not words:
        return text.HELP
    if len(words) == 1:
        character = book.bound(key)
        name = words[0]
    else:
        character = book.by_name(nickname(book, words[0]))
        name = words[1]
    if character is None:
        return text.RENAME_MISSING
    if book.by_name(name) is not None:
        return text.RENAME_EXISTS
    character["name"] = name
    if book.chat(key)["binding"] == character["id"]:
        book.chat(key)["name"] = name
    return text.RENAMED


def handle_pc(arguments: str, book: CharacterBook, key: str, sender_name: str) -> str:
    """Modify a detached book; caller commits once, including all chat bindings."""
    branch, rest = split_pc(arguments)
    player = book.player_name(key, sender_name)
    if branch == "help":
        return text.HELP
    if branch in ("list", "lst"):
        rows = []
        for index, character in enumerate(book.characters, 1):
            marker = "[★]" if book.binding_chats(character["id"]) else "[×]"
            if book.chat(key)["binding"] == character["id"]:
                marker = "[√]"
            rows.append(f'{index:2d} {marker} {character["name"]}')
        if not rows:
            return text.EMPTY_LIST.format(player=player)
        return text.LIST.format(player=player, rows="\n".join(rows))
    if branch == "rename":
        return rename(book, key, rest)

    name = nickname(
        book, rest, fallback=player if branch in ("new", "save") else "",
        index=branch != "new",
    )
    character = book.by_name(name)
    if branch == "new":
        if character is not None:
            return text.EXISTS
        if not name:
            return text.HELP
        book.bind(key, book.create(name, {}))
        return text.NEW.format(name=name)
    if branch == "tag":
        if name:
            if character is None:
                return text.TAG_MISSING.format(name=name)
            book.bind(key, character)
            return text.TAG.format(name=name)
        current = book.bound(key)
        if current is None:
            return text.NOT_BOUND
        book.chat(key)["binding"] = 0
        book.chat(key)["name"] = current["name"]
        return text.UNTAG.format(name=current["name"])
    if branch == "untagall":
        if not name:
            character = book.bound(key)
        bindings = book.binding_chats(character["id"]) if character is not None else []
        if not bindings:
            return text.NO_BINDINGS
        groups = [book.chat(chat_key)["label"] for chat_key in bindings]
        for chat_key in bindings:
            book.chat(chat_key)["binding"] = 0
        if key in bindings:
            book.chat(key)["name"] = ""
        return text.UNBOUND_ALL.format(groups="\n".join(groups))
    if branch == "save":
        if character is not None and book.binding_chats(character["id"]):
            return text.SAVE_BOUND.format(name=name)
        if not name:
            return text.HELP
        attributes = book.active_attributes(key)
        if character is None:
            book.create(name, attributes)
        else:
            character["attributes"] = dict(attributes)
        return text.SAVED.format(name=name)
    if branch == "load":
        if character is None:
            return text.MISSING
        # Upstream loads into the active sheet, even when it is bound. Snapshot
        # before replacing: loading a card onto itself must not erase its data.
        book.replace_active(key, character["attributes"])
        book.chat(key)["name"] = name
        return text.LOADED.format(name=name)
    if branch in ("del", "rm"):
        if not name:
            return text.HELP
        if character is None:
            return text.MISSING
        if book.binding_chats(character["id"]):
            return text.DELETE_BOUND.format(name=name)
        book.characters.remove(character)
        return text.DELETED.format(name=name)
    return text.HELP
