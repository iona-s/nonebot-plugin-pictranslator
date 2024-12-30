from pathlib import Path
from asyncio import sleep
from base64 import b64encode
from typing import Any, Union

from nonebot import Bot, require, on_regex, on_startswith

require('nonebot_plugin_alconna')
require('nonebot_plugin_waiter')
from nonebot_plugin_waiter import waiter
from nonebot.params import Event, Matcher, Message, RegexGroup
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot_plugin_alconna.uniseg import (
    Text,
    Image,
    Reply,
    UniMsg,
    Reference,
    CustomNode,
    UniMessage,
    image_fetch,
)

from .config import Config
from .utils import get_languages
from .translate import (
    handle_ocr,
    handle_dictionary,
    handle_text_translate,
    handle_image_translate,
)

__plugin_meta__ = PluginMetadata(
    name='nonebot-plugin-pictranslator',
    description='一个支持图片翻译的nonebot2插件',
    usage='翻译 [要翻译的内容]',
    type='application',
    homepage='https://github.com/iona-s/nonebot-plugin-pictranslator',
    config=Config,
    supported_adapters=inherit_supported_adapters('nonebot_plugin_alconna'),
)


dictionary_handler = on_regex(r'^(?:词典|查词)(.+)')
text_translate_handler = on_regex(r'^(?:翻译|(.+)译([^\s]+)) (.+)')
image_translate_handler = on_regex(r'^图片(?:翻译|(.+)译(.+))')
ocr_handler = on_startswith('ocr')


@dictionary_handler.handle()
async def dictionary(match_group: tuple[Any, ...] = RegexGroup()):
    word = match_group[0].strip()
    result = await handle_dictionary(word)
    await dictionary_handler.finish(await UniMessage(Text(result)).export())


@text_translate_handler.handle()
async def text_translate(match_group: tuple[Any, ...] = RegexGroup()):
    text = match_group[2].strip()  # 受限于单条消息长度一般不会超过api限制
    source_language, target_language = get_languages(
        match_group[0],
        match_group[1],
    )
    if target_language is None:
        await text_translate_handler.finish(source_language)
    result = await handle_text_translate(
        text,
        source_language,
        target_language,
    )
    await text_translate_handler.finish(
        await UniMessage(Text(result)).export(),
    )


async def extract_images(msg: UniMsg) -> list[Image]:
    if Reply in msg and isinstance((raw_reply := msg[Reply, 0].msg), Message):
        msg = await UniMessage.generate(message=raw_reply)
    return msg[Image]


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
                        content=message_segment,
                    ),
                )
        else:
            nodes.append(
                CustomNode(
                    uid=bot_id,
                    name='翻译姬',
                    content=content,
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


@image_translate_handler.handle()
async def image_translate(
    bot: Bot,
    event: Event,
    matcher: Matcher,
    match_group: tuple[Any, ...] = RegexGroup(),
):
    source_language, target_language = get_languages(
        match_group[0],
        match_group[1],
    )
    if target_language is None:
        await image_translate_handler.finish(source_language)
    msg = await UniMessage.generate(event=event)
    images = await extract_images(msg)
    if not images:

        @waiter(waits=['message'], keep_session=True)
        async def wait_msg(_msg: UniMsg) -> UniMsg:
            return _msg

        waited_msg = await wait_msg.wait(
            '请在60秒内发送要翻译的图片',
            timeout=60,
        )
        if not waited_msg:
            await image_translate_handler.finish('操作超时')
        images = await extract_images(waited_msg)
    if not images:
        await image_translate_handler.finish('未检测到图片')
    base64_images = []
    for image in images:
        if image.path:
            base64_images.append(Path(image.path).read_bytes())
            continue
        # TODO 图片大小检测？
        base64_images.append(
            b64encode(
                await image_fetch(event, bot, matcher.state, image),  # noqa
            ),
        )
    msg = '翻译中...'
    if target_language == 'auto':
        msg = '未指定目标语言，默认为中文\n' + msg
        target_language = 'zh'
    await image_translate_handler.send(msg)
    for base64_image in base64_images:
        msgs, image = await handle_image_translate(
            base64_image,
            source_language,
            target_language,
        )
        nodes = []
        for msg in msgs:
            add_node(nodes, msg, bot.self_id)
        if image is not None:
            add_node(nodes, image, bot.self_id)
        await image_translate_handler.send(
            await UniMessage(Reference(nodes=nodes)).export(),
        )
        await sleep(0.1)


@ocr_handler.handle()
async def ocr(bot: Bot, event: Event, matcher: Matcher):
    msg = await UniMessage.generate(event=event)
    images = await extract_images(msg)
    if not images:

        @waiter(waits=['message'], keep_session=True)
        async def wait_msg(_msg: UniMsg) -> UniMsg:
            return _msg

        waited_msg = await wait_msg.wait(
            '请在60秒内发送要识别的图片',
            timeout=60,
        )
        if not waited_msg:
            await ocr_handler.finish('操作超时')
        images = await extract_images(waited_msg)
    if not images:
        await ocr_handler.finish('未检测到图片')
    ocr_images: list[Union[str, bytes]] = []
    for image in images:
        if 'multimedia.nt.qq.com.cn' in image.url:  # 暂时只有qq的图片直接用url
            ocr_images.append(image.url)
            continue
        if image.path:
            ocr_images.append(Path(image.path).read_bytes())
            continue
        ocr_images.append(
            b64encode(
                await image_fetch(event, bot, matcher.state, image),  # noqa
            ),
        )
    await ocr_handler.send('识别中...')
    for image in ocr_images:
        nodes = []
        msgs = await handle_ocr(image)
        for msg in msgs:
            add_node(nodes, msg, bot.self_id)
        await ocr_handler.send(
            await UniMessage(Reference(nodes=nodes)).export(),
        )
        await sleep(0.1)
