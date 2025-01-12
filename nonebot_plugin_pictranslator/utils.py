from typing import Union, Optional

from nonebot import logger
from nonebot.params import Message
from langcodes import Language, LanguageTagError
from nonebot_plugin_alconna.uniseg import (
    Text,
    Image,
    Reply,
    UniMsg,
    CustomNode,
    UniMessage,
)

from .define import LANGUAGE_TYPE

__all__ = ['get_languages', 'extract_images', 'add_node', 'extract_from_reply']


def get_language(
    lang: Optional[str],
) -> Optional[Language]:
    if lang is None:
        return None
    lang_str = lang + '文' if not lang.endswith(('语', '文')) else lang
    try:
        result_lang = Language.find(lang_str)
    except LookupError:
        try:
            result_lang = Language.get(lang)
        except LanguageTagError:
            pass
        else:
            if result_lang.has_name_data():
                return result_lang
        logger.error(f'无法识别的语言: {lang}')
        return None
    return result_lang


def get_languages(
    source: Optional[str],
    target: Optional[str],
) -> Union[tuple[None, None], tuple[LANGUAGE_TYPE, LANGUAGE_TYPE]]:
    if source and target:
        source_language = get_language(source)
        target_language = get_language(target)
        if not source_language or not target_language:
            return None, None
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
