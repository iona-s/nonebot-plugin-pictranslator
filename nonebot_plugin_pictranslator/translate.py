from random import choice
from typing import Union

from httpx import AsyncClient
from langcodes import Language
from nonebot import logger

from .apis import (
    TA,
    TianApi,
    get_apis,
)
from .config import config
from .define import LANGUAGE_TYPE

__all__ = [
    'handle_dictionary',
    'handle_image_translate',
    'handle_ocr',
    'handle_text_translate',
]


async def handle_dictionary(word: str) -> str:
    async with AsyncClient() as client:
        api = TianApi(client)
        ret = await api.query_dictionary(word)
        if ret is None:
            return '查询出错'
        if ret.code != 200:  # noqa: PLR2004
            return ret.msg
        return ret.result.word + ':\n' + ret.result.content.replace('|', '\n')


async def handle_text_translate(
    text: str,
    source_language: LANGUAGE_TYPE,
    target_language: LANGUAGE_TYPE,
) -> list[str]:
    results = []
    apis = get_apis('text_translate')
    if not apis:
        return ['无可用翻译API']
    async with AsyncClient() as client:
        if target_language == 'auto':
            if source_language == 'auto':
                detection_api = get_apis(
                    'text_translate', language_detection=True
                )
                if not detection_api:
                    results.append(
                        '有道/百度智能云不提供语言检测API，故默认翻译为中文。'
                        '可使用[译<语言>]来指定',
                    )
                    target_language = Language.make('zh')
                else:
                    api = detection_api.pop()(client)
                    detected_source = await api.language_detection(text)
                    if detected_source is None:
                        results.append('语种识别出错，已默认翻译为中文')
                        target_language = Language.make('zh')
                    else:
                        if not detected_source.has_name_data():
                            warn_msg = f'语种识别可能有误 {detected_source}'
                            results.append(warn_msg)
                            logger.warning(warn_msg)
                        target_language = (
                            Language.make('zh')
                            if detected_source.language != 'zh'
                            else Language.make('en')
                        )
            else:
                target_language = (
                    Language.make('zh')
                    if source_language.language != 'zh'
                    else Language.make('en')
                )
        if config.text_translate_mode == 'auto':
            apis = [apis.pop(0)]
        elif config.text_translate_mode == 'random':
            apis = [choice(apis)]  # noqa S311
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
    source_language: LANGUAGE_TYPE,
    target_language: Language,
) -> list[list[Union[str, bytes]]]:
    results = []
    apis = get_apis('image_translate')
    if not apis:
        return [['无可用翻译API']]
    if config.image_translate_mode == 'auto':
        apis = [apis.pop(0)]
    elif config.image_translate_mode == 'random':
        apis = [choice(apis)]  # noqa S311
    async with AsyncClient() as client:
        for api_class in apis:
            api: TA = api_class(client)
            results.append(
                await api.image_translate(
                    base64_image,
                    source_language,
                    target_language,
                )
            )
    return results


async def handle_ocr(
    image: Union[str, bytes],
) -> list[list[str]]:
    apis = get_apis('ocr')
    if not apis:
        return [['无可用OCRAPI']]
    if config.ocr_mode == 'auto':
        apis = [apis.pop(0)]
    elif config.ocr_mode == 'random':
        apis = [choice(apis)]  # noqa S311
    result = []
    async with AsyncClient() as client:
        for api_class in apis:
            api: TA = api_class(client)
            result.append(await api.ocr(image))
    return result
