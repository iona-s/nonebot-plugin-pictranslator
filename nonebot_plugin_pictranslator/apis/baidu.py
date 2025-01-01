from io import BytesIO
from uuid import uuid4
from hashlib import md5
from typing import Optional
from base64 import b64decode

from ..config import config
from .base_api import TranslateApi
from ..define import LANGUAGE_NAME_INDEX
from .response_models.baidu import (
    ImageTranslationResponse,
    LanguageDetectionResponse,
    LanguageTranslationResponse,
)


class BaiduApi(TranslateApi):
    @staticmethod
    def sign(payload: dict, q: str, *, sign_image: bool = False) -> dict:
        salt = str(uuid4())
        extra = 'APICUIDmac' if sign_image else ''
        sign_string = (
            f'{config.baidu_id}'
            f'{q}'
            f'{salt}'
            f'{extra}'
            f'{config.baidu_key}'
        )
        sign = md5(sign_string.encode()).hexdigest()
        payload.update(
            {
                'appid': config.baidu_id,
                'salt': salt,
                'sign': sign,
            },
        )
        return payload

    async def _language_detection(
        self,
        text: str,
    ) -> Optional[LanguageDetectionResponse]:
        payload = {
            'q': text,
        }
        payload = self.sign(payload, text)
        return await self._handle_request(
            url='https://fanyi-api.baidu.com/api/trans/vip/language',
            method='POST',
            response_model=LanguageDetectionResponse,
            data=payload,
        )

    async def language_detection(self, text: str) -> Optional[str]:
        result = await self._language_detection(text)
        if result is None:
            return None
        return result.data.lang

    async def _text_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> Optional[LanguageTranslationResponse]:
        payload = {
            'q': text,
            'from': source_language,
            'to': target_language,
        }
        payload = self.sign(payload, text)
        return await self._handle_request(
            url='https://fanyi-api.baidu.com/api/trans/vip/translate',
            method='POST',
            response_model=LanguageTranslationResponse,
            data=payload,
        )

    async def text_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        result = await self._text_translate(
            text,
            source_language,
            target_language,
        )
        if result is None:
            return '百度翻译出错'
        data = result.data[0]
        source_language_name = LANGUAGE_NAME_INDEX[result.source]
        target_language_name = LANGUAGE_NAME_INDEX[result.target]
        return (
            f'百度翻译:\n{source_language_name}->{target_language_name}\n'
            f'{data.target_text}'
        )

    async def _image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> Optional[ImageTranslationResponse]:
        payload = {
            'from': source_language,
            'to': target_language,
            'cuid': 'APICUID',
            'mac': 'mac',
            'version': '3',
            'paste': '1',
        }
        image_io = BytesIO(b64decode(base64_image))
        image_md5 = md5(image_io.read()).hexdigest()
        payload = self.sign(payload, image_md5, sign_image=True)
        image = {'image': ('image.png', image_io, 'multipart/form-data')}
        return await self._handle_request(
            url='https://fanyi-api.baidu.com/api/trans/sdk/picture',
            method='POST',
            response_model=ImageTranslationResponse,
            log_kwargs_to_trace=True,
            log_response_to_trace=True,
            data=payload,
            files=image,
        )

    async def image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> tuple[list[str], Optional[bytes]]:
        result = await self._image_translate(
            base64_image,
            source_language,
            target_language,
        )
        if result is None:
            return ['百度翻译出错'], None
        data = result.data
        source_language_name = LANGUAGE_NAME_INDEX[data.source]
        target_language_name = LANGUAGE_NAME_INDEX[data.target]
        msgs = [
            f'百度翻译:\n{source_language_name}->{target_language_name}',
            '分段翻译:',
        ]
        for section in data.content:
            msgs.append(f'{section.source_text}\n->{section.target_text}')
        return msgs, b64decode(data.render_image)
