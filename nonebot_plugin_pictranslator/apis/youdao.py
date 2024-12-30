from time import time
from uuid import uuid4
from hashlib import sha256
from typing import Optional

from ..config import config
from .base_api import TranslateApi
from ..define import LANGUAGE_NAME_INDEX
from .response_models.youdao import TextTranslationResponse

__all__ = ['YoudaoApi']


class YoudaoApi(TranslateApi):
    @staticmethod
    def sign(payload: dict) -> dict:
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

    async def language_detection(self, text: str) -> Optional[str]:
        raise NotImplementedError

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
        source_language: str,
        target_language: str,
    ) -> Optional[str]:
        result = await self._text_translate(
            text,
            source_language,
            target_language,
        )
        if result is None:
            return None
        source_language = LANGUAGE_NAME_INDEX[result.source]
        target_language = LANGUAGE_NAME_INDEX[result.target]
        return f'{source_language} -> {target_language}\n{result.target_text}'

    async def image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> Optional[str]:
        raise NotImplementedError
