from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .card_storage import CharacterStore
from .characters import InvalidCardData
from .parsing import COMMAND_PATTERN, CommandError, command_parts
from .pc import split_pc
from .pc_text import DELETE_FAILED, INVALID_DATA


@register("astrbot_plugin_coin_st", "TethysPlex", "掷骰判定硬币我也不知道应该叫什么插件系列", "1.0.0")
class CoinSTPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._cards = CharacterStore(self)

    @filter.regex(COMMAND_PATTERN)
    async def on_command(self, event: AstrMessageEvent):
        command, arguments = "", ""
        try:
            parts = command_parts(event.message_str)
            if parts is None:
                return
            command, arguments = parts
            sender = event.get_sender_id()
            if not sender:
                raise CommandError("无法识别发送者，未读取或修改属性。")
            if not event.is_private_chat() and not event.get_group_id():
                raise CommandError("无法识别群聊，未读取或修改属性。")
            reply = await self._cards.execute(
                command, arguments,
                platform=event.get_platform_id(),
                sender=sender,
                group=event.get_group_id(),
                private=event.is_private_chat(),
                sender_name=event.get_sender_name() or sender,
            )
        except InvalidCardData:
            reply = INVALID_DATA
        except CommandError as exc:
            reply = str(exc)
        except Exception as exc:
            logger.error(
                "硬币属性卡处理失败（%s），请检查插件存储和运行环境。",
                type(exc).__name__,
            )
            reply = "处理失败，未能确认操作完成，请稍后重试或联系管理员。"
            if command == "pc":
                reply = "错误: 无法读取或保存角色数据\n"
                if split_pc(arguments)[0] in ("del", "rm"):
                    reply = DELETE_FAILED
        event.stop_event()
        yield event.plain_result(reply)
