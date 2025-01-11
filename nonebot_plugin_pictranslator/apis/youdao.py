from time import time
from uuid import uuid4
from hashlib import sha256
from typing import Optional
from base64 import b64decode

from langcodes import Language

from ..config import config
from .base_api import TranslateApi
from .response_models.youdao import (
    TextTranslationResponse,
    ImageTranslationResponse,
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
        # 顺便将zh转换为zh-CHS
        if payload['from'] == 'zh':
            payload['from'] = 'zh-CHS'
        if payload['to'] == 'zh':
            payload['to'] = 'zh-CHS'

        salt = str(uuid4())
        curtime = str(int(time()))
        input_str = payload['q']
        if len(input_str) > 20:
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

    async def language_detection(self, text: str) -> Optional[str]:  # noqa
        error_msg = '有道翻译API不支持语言检测'
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
    ) -> tuple[list[str], Optional[bytes]]:
        result = await self._image_translate(
            base64_image,
            self._get_language(source_language),
            self._get_language(target_language),
        )
        if result is None:
            return ['有道翻译出错'], None
        source_language = Language.get(result.source)
        target_language = Language.get(result.target)
        msgs = [
            f'有道翻译:\n{source_language.display_name("zh")}->'
            f'{target_language.display_name("zh")}',
            '分翻译:',
        ]
        for section in result.regions:
            msgs.append(f'{section.source_text}\n->{section.target_text}')
        return msgs, b64decode(result.render_image)
