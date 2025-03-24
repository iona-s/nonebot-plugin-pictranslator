from base64 import b64decode
from io import BytesIO
from typing import Optional, Union

from langcodes import Language

from ..config import config
from ..define import BAIDU_LANG_CODE_MAP, LANGUAGE_TYPE
from .base_api import TranslateApi
from .response_models.baidu_cloud import (
    ImageTranslationContent,
    ImageTranslationResponse,
    OcrResponse,
    TextTranslationContent,
    TextTranslationResponse,
)


class BaiduCloudApi(TranslateApi):
    @staticmethod
    def _get_language(lang: LANGUAGE_TYPE) -> str:
        if lang == 'auto':
            return 'auto'
        if lang.maximize() == Language.get('zh-Hant').maximize():
            return 'cht'
        lang = lang.language
        return BAIDU_LANG_CODE_MAP.get(lang, lang)

    async def _get_access_token(self) -> str:
        url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': config.baidu_cloud_id,
            'client_secret': config.baidu_cloud_key,
        }
        resp = await self._request(url, 'POST', params=params)
        return resp.json()['access_token']

    async def language_detection(self, text: str) -> Optional[Language]:
        error_msg = '百度智能云API不提供语言检测'
        raise NotImplementedError(error_msg)

    async def _text_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> Optional[TextTranslationContent]:
        # payload = {
        #     'from': source_language,
        #     'to': target_language,
        #     'q': text,
        # }
        params = {
            'access_token': await self._get_access_token(),
            'from': source_language,
            'to': target_language,
            'q': text,
        }
        result = await self._handle_request(
            url='https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1',
            method='POST',
            response_model=TextTranslationResponse,
            params=params,
            # ??? 为什么都丢到params里去了，百度示例代码写的就有问题
            # data=payload,
        )
        return None if result is None else result.content

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
            return '百度智能云翻译出错'
        content = result.translation_result
        return (
            f'百度智能云翻译:\n{Language.get(result.source).display_name("zh")}->'
            f'{Language.get(result.target).display_name("zh")}\n'
            f'{content.target_text}'
        )

    async def _image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> Optional[ImageTranslationContent]:
        # payload = {
        #     'from': source_language,
        #     'to': target_language,
        #     'v': 3,
        #     'paste': 1,
        # }
        params = {
            'access_token': await self._get_access_token(),
            'from': source_language,
            'to': target_language,
            'v': 3,
            'paste': 1,
        }
        image_io = BytesIO(b64decode(base64_image))
        image = {'image': ('image.png', image_io, 'multipart/form-data')}
        result = await self._handle_request(
            url='https://aip.baidubce.com/file/2.0/mt/pictrans/v1',
            method='POST',
            response_model=ImageTranslationResponse,
            params=params,
            # data=payload,  # 跟文字翻译一样的问题
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
            return ['百度智能云翻译出错']
        msgs = [
            f'百度智能云翻译:\n{Language.get(result.source)}->'
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

    async def _ocr(self, image: Union[str, bytes]) -> Optional[OcrResponse]:
        if isinstance(image, str):
            payload = {'url': image}
        else:
            payload = {'image': image.decode('utf-8')}
        payload.update(
            {
                'paragraph': True,
                # 下面的未使用
                # 'language_type': 'auto_detect',
                # 'detect_direction': False,
                # 'multidirectional_recognize': False,
            }
        )
        params = {
            'access_token': await self._get_access_token(),
        }
        return await self._handle_request(
            url='https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic',
            method='POST',
            response_model=OcrResponse,
            params=params,
            data=payload,
        )

    async def ocr(self, image: Union[str, bytes]) -> list[str]:
        result = await self._ocr(image)
        if not result:
            return ['OCR失败']
        content = ['百度智能云OCR结果']
        content.extend(result.paragraphs)
        return content
