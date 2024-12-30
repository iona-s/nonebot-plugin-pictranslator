from typing import Union, Optional

from httpx import AsyncClient

from .apis.tianapi import TianApi
from .apis.youdao import YoudaoApi
from .apis.tencent import TencentApi

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
    source_language: str,
    target_language: str,
) -> str:
    async with AsyncClient() as client:
        api = YoudaoApi(client)  # TODO implement choose api
        if source_language == 'auto':
            source_language = await api.language_detection(text)
            if source_language is None:
                return '查询出错'
        if target_language == 'auto':
            target_language = 'en' if source_language == 'zh' else 'zh'
        return await api.text_translate(
            text,
            source_language,
            target_language,
        )


async def handle_image_translate(
    base64_image: bytes,
    source_language: str,
    target_language: str,
) -> tuple[list[str], Optional[bytes]]:
    async with AsyncClient() as client:
        api = YoudaoApi(client)  # TODO implement choose api
        if target_language == 'auto':
            target_language = 'en' if source_language == 'zh' else 'zh'
        return await api.image_translate(
            base64_image,
            source_language,
            target_language,
        )


async def handle_ocr(
    image: Union[str, bytes],
) -> list[str]:
    async with AsyncClient() as client:
        api = TencentApi(client)
        return await api.ocr(image)
