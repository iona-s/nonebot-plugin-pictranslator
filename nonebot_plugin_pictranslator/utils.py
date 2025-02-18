from typing import Optional, Union

from langcodes import Language, LanguageTagError
from nonebot import get_driver, logger
from nonebot.params import Message
from nonebot_plugin_alconna import Segment
from nonebot_plugin_alconna.uniseg import (
    CustomNode,
    Image,
    Reply,
    Text,
    UniMessage,
    UniMsg,
)

from .define import LANGUAGE_TYPE

__all__ = ['add_node', 'extract_from_reply', 'extract_images', 'get_languages']


def get_language(
    lang: Optional[str],
) -> Optional[Language]:
    threshold = 10
    if lang is None or len(lang) > threshold:
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
    return msg[seg_type]


async def extract_images(msg: UniMsg) -> list[Image]:
    if Reply in msg and isinstance((raw_reply := msg[Reply, 0].msg), Message):
        msg = await UniMessage.generate(message=raw_reply)
    return msg[Image]


def add_node(
    nodes: list[CustomNode],
    content: Union[str, bytes],
    bot_id: str,
) -> list[CustomNode]:
    global_config = get_driver().config
    nickname = global_config.nickname
    nickname = next(iter(nickname)) if nickname else '翻译姬'

    def _add_node(node_content: Union[str, UniMessage, list[Segment]]) -> None:
        nodes.append(
            CustomNode(
                uid=bot_id,
                name=nickname,
                content=node_content,
            ),
        )

    if isinstance(content, str):
        _add_node(content.strip())
    elif isinstance(content, bytes):
        _add_node(UniMessage.image(raw=content))
    return nodes
