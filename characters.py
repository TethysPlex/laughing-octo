from copy import deepcopy


class InvalidCardData(ValueError):
    pass


def validate_attributes(value):
    if not isinstance(value, dict) or any(
        not isinstance(name, str) or type(number) is not int
        for name, number in value.items()
    ):
        raise InvalidCardData("Invalid attribute map")


class CharacterBook:

    def __init__(self, value=None):
        if value is None:
            value = {"version": 1, "next_id": 1, "characters": [], "chats": {}}
        self._validate(value)
        self.data = deepcopy(value)

    @staticmethod
    def _validate(value):
        if (
            not isinstance(value, dict)
            or type(value.get("version")) is not int
            or value["version"] != 1
            or type(value.get("next_id")) is not int
            or value["next_id"] < 1
            or not isinstance(value.get("characters"), list)
            or not isinstance(value.get("chats"), dict)
        ):
            raise InvalidCardData("Invalid character document")
        ids, names = set(), set()
        for character in value["characters"]:
            if (
                not isinstance(character, dict)
                or type(character.get("id")) is not int
                or not 0 < character["id"] < value["next_id"]
                or character["id"] in ids
                or not isinstance(character.get("name"), str)
                or not character["name"]
                or character["name"] in names
            ):
                raise InvalidCardData("Invalid character")
            validate_attributes(character.get("attributes"))
            ids.add(character["id"])
            names.add(character["name"])
        for key, chat in value["chats"].items():
            if (
                not isinstance(key, str)
                or not isinstance(chat, dict)
                or not isinstance(chat.get("name"), str)
                or not isinstance(chat.get("label"), str)
                or type(chat.get("binding")) is not int
                or (chat["binding"] != 0 and chat["binding"] not in ids)
            ):
                raise InvalidCardData("Invalid chat binding")
            validate_attributes(chat.get("attributes"))

    @property
    def characters(self):
        return self.data["characters"]

    def ensure_chat(self, key: str, label: str):
        if key not in self.data["chats"]:
            self.data["chats"][key] = {
                "label": label,
                "name": "",
                "binding": 0,
                "attributes": {},
            }

    def chat(self, key: str):
        return self.data["chats"][key]

    def by_id(self, character_id: int):
        return next((c for c in self.characters if c["id"] == character_id), None)

    def by_name(self, name: str):
        return next((c for c in self.characters if c["name"] == name), None)

    def bound(self, key: str):
        return self.by_id(self.chat(key)["binding"])

    def active_attributes(self, key: str) -> dict[str, int]:
        character = self.bound(key)
        return (character if character is not None else self.chat(key))["attributes"]

    def replace_active(self, key: str, attributes: dict[str, int]):
        character = self.bound(key)
        target = character if character is not None else self.chat(key)
        target["attributes"] = dict(attributes)

    def player_name(self, key: str, nickname: str) -> str:
        return self.chat(key)["name"] or nickname

    def create(self, name: str, attributes: dict[str, int]):
        character = {
            "id": self.data["next_id"],
            "name": name,
            "attributes": dict(attributes),
        }
        self.data["next_id"] += 1
        self.characters.append(character)
        return character

    def bind(self, key: str, character):
        self.chat(key)["binding"] = character["id"]
        self.chat(key)["name"] = character["name"]

    def binding_chats(self, character_id: int):
        return [
            key for key, chat in self.data["chats"].items()
            if chat["binding"] == character_id
        ]
