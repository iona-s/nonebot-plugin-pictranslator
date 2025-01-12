from typing import Union, Optional

from nonebot import logger
from httpx import AsyncClient
from langcodes import Language

from .config import config
from .define import LANGUAGE_TYPE
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


async def handle_text_translate(
    text: str,
    source_language: LANGUAGE_TYPE,
    target_language: LANGUAGE_TYPE,
) -> list[str]:
    results = []
    api_names = config.text_translate_apis
    apis = [AVAILABLE_TRANSLATION_APIS[name] for name in api_names]
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
                    for api_class in apis:
                        if api_class == YoudaoApi:
                            continue
                        api = api_class(client)
                        source_language = await api.language_detection(text)
                        if source_language is None:
                            results.append('语种识别出错，已默认翻译为中文')
                            source_language: LANGUAGE_TYPE = 'auto'
                            break
                        if not source_language.has_name_data():
                            warn_msg = f'语种识别可能有误 {source_language}'
                            results.append(warn_msg)
                            logger.warning(warn_msg)
                        break
            if source_language == 'auto' or source_language.language != 'zh':
                target_language = Language.make('zh')
            else:
                target_language = Language.make('en')
        if config.text_translate_mode == 'auto':
            apis = [apis.pop(0)]
            # TODO 调用次数用完自动使用下一个可用，但感觉不太用的上
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
) -> list[tuple[list[str], Optional[bytes]]]:
    results = []
    api_names = config.image_translate_apis
    apis = [AVAILABLE_TRANSLATION_APIS.get(name) for name in api_names]
    if not apis:
        return [(['无可用翻译API'], None)]
    if config.image_translate_mode == 'auto':
        apis = [apis.pop(0)]
        # TODO 调用次数用完自动使用下一个可用，但感觉不太用的上
    async with AsyncClient() as client:
        for api_class in apis:
            api: TA = api_class(client)
            msgs, image = await api.image_translate(
                base64_image,
                source_language,
                target_language,
            )
            results.append((msgs, image))
    return results


async def handle_ocr(
    image: Union[str, bytes],
) -> list[str]:
    async with AsyncClient() as client:
        api = TencentApi(client)
        return await api.ocr(image)
