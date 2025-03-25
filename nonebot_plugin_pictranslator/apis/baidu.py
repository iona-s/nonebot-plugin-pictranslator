from base64 import b64decode
from hashlib import md5
from io import BytesIO
from typing import Optional, Union
from uuid import uuid4

from langcodes import Language

from ..config import config
from ..define import BAIDU_LANG_CODE_MAP, LANGUAGE_TYPE
from .base_api import TranslateApi
from .response_models.baidu import (
    ImageTranslationContent,
    ImageTranslationResponse,
    LanguageDetectionResponse,
    TextTranslationResponse,
)


class BaiduApi(TranslateApi):
    @staticmethod
    def _get_language(lang: LANGUAGE_TYPE) -> str:
        if lang == 'auto':
            return 'auto'
        if lang.maximize() == Language.get('zh-Hant').maximize():
            return 'cht'
        lang = lang.language
        return BAIDU_LANG_CODE_MAP.get(lang, lang)

    @staticmethod
    def sign(payload: dict, q: str, *, sign_image: bool = False) -> dict:
        salt = str(uuid4())
        extra = 'APICUIDmac' if sign_image else ''
        sign_string = f'{config.baidu_id}{q}{salt}{extra}{config.baidu_key}'
        sign = md5(sign_string.encode()).hexdigest()  # noqa S324
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

    async def language_detection(self, text: str) -> Optional[Language]:
        result = await self._language_detection(text)
        if result is None:
            return None
        return Language.get(result.content.lang)

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
        payload = self.sign(payload, text)
        return await self._handle_request(
            url='https://fanyi-api.baidu.com/api/trans/vip/translate',
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
            return '百度翻译出错'
        return (
            f'百度翻译:\n{Language.get(result.source).display_name("zh")}->'
            f'{Language.get(result.target).display_name("zh")}\n'
            f'{result.translation_result.target_text}'
        )

    async def _image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> Optional[ImageTranslationContent]:
        payload = {
            'from': source_language,
            'to': target_language,
            'cuid': 'APICUID',
            'mac': 'mac',
            'version': '3',
            'paste': '1',
        }
        image_io = BytesIO(b64decode(base64_image))
        image_md5 = md5(image_io.read()).hexdigest()  # noqa S324
        payload = self.sign(payload, image_md5, sign_image=True)
        image = {'image': ('image.png', image_io, 'multipart/form-data')}
        result = await self._handle_request(
            url='https://fanyi-api.baidu.com/api/trans/sdk/picture',
            method='POST',
            response_model=ImageTranslationResponse,
            data=payload,
            files=image,
        )
        return None if result is None else result.content

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
            return ['百度翻译出错']
        if result.source == 'auto':
            source_name = '自动检测'
        else:
            source_name = Language.get(result.source).display_name('zh')
        msgs = [
            f'百度翻译:\n{source_name}->'
            f'{Language.get(result.target).display_name("zh")}\n',
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
