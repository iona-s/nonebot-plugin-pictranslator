from random import choice
from typing import Union, Optional

from httpx import AsyncClient

from .config import config
from .apis import (
    TA,
    AVAILABLE_TRANSLATION_APIS,
    TianApi,
    YoudaoApi,
    TencentApi,
)

__all__ = [
    'handle_dictionary',
    'handle_text_translate',
    'handle_image_translate',
    'handle_ocr',
]


async def handle_dictionary(word: str) -> str:
    async with AsyncClient() as client:
        api = TianApi(client)
        ret = await api.query_dictionary(word)
        if ret is None:
            return '查询出错'
        if ret.code != 200:
            return ret.msg
        return ret.result.word + ':\n' + ret.result.content.replace('|', '\n')


async def choose_api() -> list[type[TA]]:
    if config.translate_api_choice == 'all':
        api_choices = []
        for name, api in AVAILABLE_TRANSLATION_APIS.items():
            if getattr(config, f'use_{name}'):
                api_choices.append(api)
        return api_choices
    if config.translate_api_choice == 'random':
        return [choice(list(AVAILABLE_TRANSLATION_APIS.values()))]
    return [AVAILABLE_TRANSLATION_APIS[config.translate_api_choice]]


async def handle_text_translate(
    text: str,
    source_language: str,
    target_language: str,
) -> list[str]:
    results = []
    apis = await choose_api()
    if not apis:
        return ['无可用翻译API']
    async with AsyncClient() as client:
        if target_language == 'auto':
            if source_language == 'auto':
                if apis == [YoudaoApi]:
                    results.append(
                        '有道不提供语言检测API，故默认翻译为中文。'
                        '可使用[译<语言>]来指定',
                    )
                else:
                    if TencentApi in apis:
                        api = TencentApi(client)
                        source_language = await api.language_detection(text)
                        if source_language is None:
                            results.append('查询出错')
            target_language = 'en' if source_language == 'zh' else 'zh'
        for api_class in apis:
            api: TA = api_class(client)
            results.append(
                await api.text_translate(
                    text,
                    source_language,
                    target_language,
                ),
            )
    return results


async def handle_image_translate(
    base64_image: bytes,
    source_language: str,
    target_language: str,
) -> list[tuple[list[str], Optional[bytes]]]:
    results = []
    apis = await choose_api()
    if not apis:
        return [(['无可用翻译API'], None)]
    async with AsyncClient() as client:
        for api_class in apis:
            api: TA = api_class(client)
            extra_msg = None
            if target_language == 'auto':
                target_language = 'en' if source_language == 'zh' else 'zh'
                extra_msg = (
                    '图片翻译无法自动选择目标语言，默认翻译为中文。'
                    '可使用[图片译<语言>]来指定'
                )
            msgs, image = await api.image_translate(
                base64_image,
                source_language,
                target_language,
            )
            if extra_msg:
                msgs.insert(0, extra_msg)
            results.append((msgs, image))
    return results


async def handle_ocr(
    image: Union[str, bytes],
) -> list[str]:
    async with AsyncClient() as client:
        api = TencentApi(client)
        return await api.ocr(image)
