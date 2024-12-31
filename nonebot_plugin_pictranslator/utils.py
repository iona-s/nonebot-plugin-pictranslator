from typing import Union, Optional

from nonebot.params import Message
from nonebot_plugin_alconna.uniseg import (
    Text,
    Image,
    Reply,
    UniMsg,
    CustomNode,
    UniMessage,
)

from .define import LANGUAGE_INDEX

__all__ = ['get_languages', 'extract_images', 'add_node', 'extract_from_reply']


def get_languages(
    source: Optional[str],
    target: Optional[str],
) -> tuple[str, Optional[str]]:
    if source and target:
        source_language = LANGUAGE_INDEX.get(source, None)
        target_language = LANGUAGE_INDEX.get(target, None)
        if not source_language or not target_language:
            return '语言输入有误或不支持', None
    else:
        source_language = 'auto'
        target_language = 'auto'
    return source_language, target_language


async def extract_from_reply(
    msg: UniMsg,
    seg_type: Union[type[Image], type[Text]],
) -> Optional[list[Union[Image, Text]]]:
    if Reply not in msg:
        return None
    msg = await UniMessage.generate(message=msg[Reply, 0].msg)
    return msg[seg_type]  # noqa


async def extract_images(msg: UniMsg) -> list[Image]:
    if Reply in msg and isinstance((raw_reply := msg[Reply, 0].msg), Message):
        msg = await UniMessage.generate(message=raw_reply)
    return msg[Image]  # noqa


def add_node(
    nodes: list[CustomNode],
    content: Union[str, bytes],
    bot_id: str,
) -> list[CustomNode]:
    if isinstance(content, str):
        if len(content) > 3000:  # qq消息长度限制，虽然大概率也不会超过
            for i in range(0, len(content), 2999):
                if i + 2999 > len(content):
                    message_segment = content[i:]
                else:
                    message_segment = content[i : i + 2999]
                nodes.append(
                    CustomNode(
                        uid=bot_id,
                        name='翻译姬',
                        content=message_segment.strip(),
                    ),
                )
        else:
            nodes.append(
                CustomNode(
                    uid=bot_id,
                    name='翻译姬',
                    content=content.strip(),
                ),
            )
    elif isinstance(content, bytes):
        nodes.append(
            CustomNode(
                uid=bot_id,
                name='翻译姬',
                content=UniMessage.image(raw=content),
            ),
        )
    return nodes
