from typing import Optional, Union

from langcodes import Language

from ..config import config
from ..define import LANGUAGE_TYPE
from .base_api import TranslateApi
from .response_models.baidu_cloud import (
    OcrResponse,
)


class BaiduCloudApi(TranslateApi):
    @staticmethod
    def _get_language(lang: LANGUAGE_TYPE) -> str:
        raise NotImplementedError

    async def language_detection(self, text: str) -> Optional[Language]:
        raise NotImplementedError

    async def text_translate(
        self,
        text: str,
        source_language: LANGUAGE_TYPE,
        target_language: Language,
    ) -> str:
        raise NotImplementedError

    async def image_translate(
        self,
        base64_image: bytes,
        source_language: LANGUAGE_TYPE,
        target_language: Language,
    ) -> list[Union[str, bytes]]:
        raise NotImplementedError

    async def _get_access_token(self) -> str:
        url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': config.baidu_cloud_id,
            'client_secret': config.baidu_cloud_key,
        }

        payload = ''

        resp = await self._request(url, 'POST', params=params, data=payload)
        return resp.json()['access_token']

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
