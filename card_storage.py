import asyncio
import json
from copy import deepcopy

from .cards import handle_st
from .characters import CharacterBook
from .coins import roll_coins
from .pc import handle_pc, split_pc
from .pc_text import HELP


def storage_key(parts: list[str]) -> str:
    return json.dumps(parts, ensure_ascii=False, separators=(",", ":"))


class CharacterStore:

    def __init__(self, kv):
        self.kv = kv
        self._lock = asyncio.Lock()

    async def execute(
        self, command: str, arguments: str, *, platform: str, sender: str,
        group: str, private: bool, sender_name: str,
    ) -> str:
        if command == "pc" and split_pc(arguments)[0] == "help":
            return HELP
        owner_key = storage_key(["characters-v1", platform, sender])
        kind = "private" if private else "group"
        group = "" if private else group
        chat_key = storage_key([kind, group])
        async with self._lock:
            stored = await self.kv.get_kv_data(owner_key, None)
            book = CharacterBook(stored)
            before = deepcopy(book.data)
            book.ensure_chat(chat_key, group or f"私聊:{sender}")
            if command == "pc":
                reply = handle_pc(arguments, book, chat_key, sender_name)
            else:
                attributes = book.active_attributes(chat_key)
                player = f"<{book.player_name(chat_key, sender_name)}>"
                if command == "c":
                    reply = roll_coins(arguments, attributes, player)
                else:
                    reply, updated = handle_st(
                        arguments, attributes, player, bound=book.bound(chat_key) is not None,
                    )
                    book.replace_active(chat_key, updated)
            if book.data != before:
                await self.kv.put_kv_data(owner_key, book.data)
            return reply
