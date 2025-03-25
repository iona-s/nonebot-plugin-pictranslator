from nonebot import require

require('nonebot_plugin_alconna')
require('nonebot_plugin_waiter')
from base64 import b64encode
from pathlib import Path
from re import IGNORECASE, match
from typing import Any, Union

from langcodes import Language
from nonebot import Bot, on_regex
from nonebot.params import Event, Matcher, RegexGroup
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot_plugin_alconna.uniseg import (
    Image,
    Reference,
    Reply,
    Text,
    UniMessage,
    UniMsg,
    image_fetch,
)
from nonebot_plugin_waiter import waiter

from .config import Config, config
from .translate import (
    handle_dictionary,
    handle_image_translate,
    handle_ocr,
    handle_text_translate,
)
from .utils import (
    add_node,
    extract_from_reply,
    extract_images,
    get_language,
    unescape_text,
)

__plugin_meta__ = PluginMetadata(
    name='nonebot-plugin-pictranslator',
    description='一个支持图片翻译的nonebot2插件',
    usage='/翻译 [要翻译的内容]',
    type='application',
    homepage='https://github.com/iona-s/nonebot-plugin-pictranslator',
    config=Config,
    supported_adapters=inherit_supported_adapters(
        'nonebot_plugin_alconna',
        'nonebot_plugin_waiter',
    ),
)

command_start_pattern = config.command_start_pattern
dictionary_handler = on_regex(rf'^{command_start_pattern}(?:词典|查词)(.+)')
translate_re_pattern = (
    rf'^{command_start_pattern}'
    r'(图片)?([\S]+)?译([\S]+)? ?([.\s\S]*)'
)
translate_handler = on_regex(translate_re_pattern)
ocr_handler = on_regex(rf'^{command_start_pattern}ocr', flags=IGNORECASE)


@dictionary_handler.handle()
async def dictionary(match_group: tuple[Any, ...] = RegexGroup()) -> None:
    if config.tianapi_key is None:
        await dictionary_handler.finish(
            '未配置天行数据API的key，无法使用词典功能',
        )
    word = match_group[0].strip()
    result = await handle_dictionary(word)
    await dictionary_handler.finish(await UniMessage(Text(result)).export())


@translate_handler.handle()
async def translate(  # noqa: C901 PLR0912 PLR0915
    bot: Bot,
    event: Event,
    matcher: Matcher,
    match_group: tuple[Any, ...] = RegexGroup(),
) -> None:
    msg = await UniMessage.generate(event=event)
    plain_text = msg.extract_plain_text()
    new_match = match(translate_re_pattern, plain_text)
    source_language = get_language(new_match.group(2), auto_flags={None, '翻'})
    target_language = get_language(new_match.group(3))
    if source_language is None or target_language is None:
        await translate_handler.finish('语言输入有误或不支持')

    image_search = bool(match_group[0])
    images = await extract_images(msg)
    translate_content = images if images else match_group[3].strip()
    if Reply in msg:
        images = await extract_from_reply(msg, Image)
        if images:
            translate_content = images
        else:
            if image_search:
                await translate_handler.finish('未检测到图片')
            text_content = await extract_from_reply(msg, Text)
            translate_content = text_content[0].text if text_content else None
    if not translate_content:

        @waiter(waits=['message'], keep_session=True)
        async def wait_msg(_msg: UniMsg) -> UniMsg:
            return _msg

        waited_msg: UniMessage = await wait_msg.wait(
            '请在30秒内发送要翻译的内容',
            timeout=30,
        )
        if not waited_msg:
            await translate_handler.finish('操作超时')
        images = await extract_images(waited_msg)
        if images:
            translate_content = images
        else:
            if image_search:
                await translate_handler.finish('未检测到图片')
            translate_content = waited_msg.extract_plain_text()

    # 进行文本翻译
    if isinstance(translate_content, str):
        await translate_handler.send('翻译中...')
        results = await handle_text_translate(
            unescape_text(translate_content),
            source_language,
            target_language,
        )
        for result in results:
            await translate_handler.send(
                await UniMessage(Text(result)).export(),
            )
        return

    # 进行图片翻译
    base64_images = []
    for image in translate_content:
        if image.path:
            base64_images.append(Path(image.path).read_bytes())
            continue
        # TODO 增加图片大小检测？
        base64_images.append(
            b64encode(
                await image_fetch(event, bot, matcher.state, image),
            ),
        )
    notice_msg = '翻译中...'
    if target_language == 'auto':
        if source_language == 'auto' or source_language.language != 'zh':
            target_language = Language.make('zh')
            notice_msg += '\n图片翻译无法自动选择目标语言，默认翻译为中文'
        else:
            target_language = Language.make('en')
            notice_msg += '\n未指定目标语言，默认翻译为英文'
        notice_msg += '\n可使用[图片翻译<语言>]来指定'
    await translate_handler.send(notice_msg)
    for base64_image in base64_images:
        results = await handle_image_translate(
            base64_image,
            source_language,
            target_language,
        )
        for result_per_api in results:
            nodes = []
            for msg in result_per_api:
                add_node(nodes, msg, bot.self_id)
            await translate_handler.send(
                await UniMessage(Reference(nodes=nodes)).export(),
            )


# TODO 添加指定目标语言
@ocr_handler.handle()
async def ocr(bot: Bot, event: Event, matcher: Matcher) -> None:  # noqa: C901
    if not config.use_tencent:
        await ocr_handler.finish('未启用腾讯API，无法使用OCR功能')
    msg = await UniMessage.generate(event=event)
    images = await extract_images(msg)
    if not images:

        @waiter(waits=['message'], keep_session=True)
        async def wait_msg(_msg: UniMsg) -> UniMsg:
            return _msg

        waited_msg = await wait_msg.wait(
            '请在30秒内发送要识别的图片',
            timeout=30,
        )
        if not waited_msg:
            await ocr_handler.finish('操作超时')
        images = await extract_images(waited_msg)
    if not images:
        await ocr_handler.finish('未检测到图片')
    ocr_images: list[Union[str, bytes]] = []
    for image in images:
        if image.url and config.ocr_use_image_url:
            ocr_images.append(image.url)
            continue
        if image.path:
            ocr_images.append(Path(image.path).read_bytes())
            continue
        ocr_images.append(
            b64encode(
                await image_fetch(event, bot, matcher.state, image),
            ),
        )
    await ocr_handler.send('识别中...')
    for image in ocr_images:
        results = await handle_ocr(image)
        for msgs in results:
            nodes = []
            for msg in msgs:
                add_node(nodes, msg, bot.self_id)
            await ocr_handler.send(
                await UniMessage(Reference(nodes=nodes)).export(),
            )
