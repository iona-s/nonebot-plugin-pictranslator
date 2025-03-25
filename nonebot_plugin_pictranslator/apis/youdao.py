from base64 import b64decode
from hashlib import sha256
from time import time
from typing import Optional, Union
from uuid import uuid4

from langcodes import Language

from ..config import config
from .base_api import TranslateApi
from .response_models.youdao import (
    ImageTranslationResponse,
    TextTranslationResponse,
)

__all__ = ['YoudaoApi']

from ..define import LANGUAGE_TYPE


class YoudaoApi(TranslateApi):
    @staticmethod
    def _get_language(lang: LANGUAGE_TYPE) -> str:
        if lang == 'auto':
            return 'auto'
        if lang.maximize() == Language.get('zh-Hant').maximize():
            return 'zh-CHT'
        if lang.language == 'zh':
            return 'zh-CHS'
        return lang.language

    @staticmethod
    def sign(payload: dict) -> dict:
        salt = str(uuid4())
        curtime = str(int(time()))
        input_str = payload['q']
        threshold = 20
        if len(input_str) > threshold:
            input_str = input_str[:10] + str(len(input_str)) + input_str[-10:]
        sign_str = (
            config.youdao_id + input_str + salt + curtime + config.youdao_key
        )
        signed = sha256(sign_str.encode()).hexdigest()
        payload.update(
            {
                'appKey': config.youdao_id,
                'salt': salt,
                'sign': signed,
                'signType': 'v3',
                'curtime': curtime,
            },
        )
        return payload

    async def language_detection(self, text: str) -> Optional[str]:
        error_msg = '有道翻译API不提供语言检测'
        raise NotImplementedError(error_msg)

    async def _text_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> Optional[TextTranslationResponse]:
        payload = {
            'q': text,
            'from': source_language,
            'to': target_language,
        }
        payload = self.sign(payload)
        return await self._handle_request(
            url='https://openapi.youdao.com/api',
            method='POST',
            response_model=TextTranslationResponse,
            data=payload,
        )

    async def text_translate(
        self,
        text: str,
        source_language: LANGUAGE_TYPE,
        target_language: Language,
    ) -> str:
        result = await self._text_translate(
            text,
            self._get_language(source_language),
            self._get_language(target_language),
        )
        if result is None:
            return '有道翻译出错'
        source_language = Language.get(result.source)
        target_language = Language.get(result.target)
        return (
            f'有道翻译:\n{source_language.display_name("zh")}->'
            f'{target_language.display_name("zh")}\n'
            f'{result.target_text}'
        )

    async def _image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> Optional[ImageTranslationResponse]:
        payload = {
            'type': '1',
            'q': base64_image.decode(),
            'from': source_language,
            'to': target_language,
            'render': '1',
        }
        payload = self.sign(payload)
        return await self._handle_request(
            url='https://openapi.youdao.com/ocrtransapi',
            method='POST',
            response_model=ImageTranslationResponse,
            data=payload,
        )

    async def image_translate(
        self,
        base64_image: bytes,
        source_language: LANGUAGE_TYPE,
        target_language: Language,
    ) -> list[Union[str, bytes]]:
        result = await self._image_translate(
            base64_image,
            self._get_language(source_language),
            self._get_language(target_language),
        )
        if result is None:
            return ['有道翻译出错']
        source_language = Language.get(result.source)
        target_language = Language.get(result.target)
        msgs = [
            f'有道翻译:\n'
            f'{source_language.display_name("zh")}->'
            f'{target_language.display_name("zh")}',
            b64decode(result.render_image),
            '分段翻译:',
        ]
        msgs.extend(
            [
                f'{section.source_text}\n->{section.target_text}'
                for section in result.sections
            ],
        )
        return msgs
