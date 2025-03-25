from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256
from hmac import new as hmac_new
from io import BytesIO
from json import dumps
from math import floor
from time import time
from typing import Literal, Optional, Union
from uuid import uuid4

from httpx import __version__ as httpx_version
from langcodes import Language
from PIL import Image, ImageDraw, ImageFont

from ..config import config
from ..define import LANGUAGE_TYPE
from .base_api import TranslateApi
from .response_models.tencent import (
    ImageTranslationContent,
    ImageTranslationResponse,
    LanguageDetectionContent,
    LanguageDetectionResponse,
    OcrContent,
    OcrResponse,
    TextTranslationContent,
    TextTranslationResponse,
)

__all__ = ['TencentApi']

# TODO 图片翻译好像有点问题


class TencentApi(TranslateApi):
    @staticmethod
    def _get_language(lang: LANGUAGE_TYPE) -> str:
        if lang == 'auto':
            return 'auto'
        if lang.maximize() == Language.get('zh-Hant').maximize():
            return 'zh-TW'
        return lang.language

    @staticmethod
    def _sign(key: bytes, msg: str) -> bytes:
        return hmac_new(key, msg.encode('utf-8'), sha256).digest()

    def _construct_headers(
        self,
        action: Literal[
            'LanguageDetect',
            'TextTranslate',
            'ImageTranslate',
            'GeneralBasicOCR',
        ],
        payload: dict,
        *,
        service: str = 'tmt',
    ) -> dict:
        host = f'{service}.tencentcloudapi.com'
        version = {
            'LanguageDetect': '2018-03-21',
            'TextTranslate': '2018-03-21',
            'ImageTranslate': '2018-03-21',
            'GeneralBasicOCR': '2018-11-19',
        }[action]
        algorithm = 'TC3-HMAC-SHA256'
        timestamp = int(time())
        date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
            '%Y-%m-%d',
        )
        http_request_method = 'POST'
        canonical_uri = '/'
        canonical_querystring = ''
        ct = 'application/json; charset=utf-8'
        canonical_headers = (
            f'content-type:{ct}\nhost:{host}\nx-tc-action:{action.lower()}\n'
        )
        signed_headers = 'content-type;host;x-tc-action'
        if httpx_version.split('.')[1] > '27':
            dumped_payload = dumps(
                payload,
                ensure_ascii=False,
                separators=(',', ':'),
                allow_nan=False,
            )
        else:
            dumped_payload = dumps(payload)
        hashed_request_payload = sha256(
            dumped_payload.encode('utf-8'),
        ).hexdigest()
        canonical_request = (
            http_request_method
            + '\n'
            + canonical_uri
            + '\n'
            + canonical_querystring
            + '\n'
            + canonical_headers
            + '\n'
            + signed_headers
            + '\n'
            + hashed_request_payload
        )
        credential_scope = date + '/' + service + '/' + 'tc3_request'
        hashed_canonical_request = sha256(
            canonical_request.encode('utf-8'),
        ).hexdigest()
        string_to_sign = (
            algorithm
            + '\n'
            + str(timestamp)
            + '\n'
            + credential_scope
            + '\n'
            + hashed_canonical_request
        )
        secret_date = self._sign(
            ('TC3' + config.tencent_key).encode('utf-8'),
            date,
        )
        secret_service = self._sign(secret_date, service)
        secret_signing = self._sign(secret_service, 'tc3_request')
        signature = hmac_new(
            secret_signing,
            string_to_sign.encode('utf-8'),
            sha256,
        ).hexdigest()
        authorization = (
            algorithm
            + ' '
            + 'Credential='
            + config.tencent_id
            + '/'
            + credential_scope
            + ', '
            + 'SignedHeaders='
            + signed_headers
            + ', '
            + 'Signature='
            + signature
        )
        return {
            'Authorization': authorization,
            'Content-Type': 'application/json; charset=utf-8',
            'Host': host,
            'X-TC-Action': action,
            'X-TC-Timestamp': str(timestamp),
            'X-TC-Version': version,
            'X-TC-Region': config.tencent_api_region,
        }

    async def _language_detection(
        self,
        text: str,
    ) -> Optional[LanguageDetectionContent]:
        payload = {
            'Text': text,
            'ProjectId': config.tencent_project_id,
        }
        headers = self._construct_headers('LanguageDetect', payload)
        result = await self._handle_request(
            url='https://tmt.tencentcloudapi.com',
            method='POST',
            response_model=LanguageDetectionResponse,
            json=payload,
            headers=headers,
        )
        return None if result is None else result.response

    async def language_detection(self, text: str) -> Optional[Language]:
        result = await self._language_detection(text)
        if result is None:
            return None
        return Language.get(result.lang)

    async def _text_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> Optional[TextTranslationContent]:
        payload = {
            'SourceText': text,
            'Source': source_language,
            'Target': target_language,
            'ProjectId': config.tencent_project_id,
        }
        headers = self._construct_headers('TextTranslate', payload)
        result = await self._handle_request(
            url='https://tmt.tencentcloudapi.com',
            method='POST',
            response_model=TextTranslationResponse,
            json=payload,
            headers=headers,
        )
        return None if result is None else result.response

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
            return '腾讯翻译出错'
        source_language = Language.get(result.source)
        target_language = Language.get(result.target)
        return (
            f'腾讯翻译:\n{source_language.language_name("zh")}->'
            f'{target_language.language_name("zh")}:\n'
            f'{result.target_text}'
        )

    async def _image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> Optional[ImageTranslationContent]:
        payload = {
            'SessionUuid': f'session-{uuid4()}',
            'Scene': 'doc',
            'Data': base64_image.decode('utf-8'),
            'Source': source_language,
            'Target': target_language,
            'ProjectId': config.tencent_project_id,
        }
        headers = self._construct_headers('ImageTranslate', payload)
        result = await self._handle_request(
            url='https://tmt.tencentcloudapi.com',
            method='POST',
            response_model=ImageTranslationResponse,
            json=payload,
            headers=headers,
        )
        return None if result is None else result.response

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
            return ['腾讯翻译出错']
        source_language = Language.get(result.source)
        target_language = Language.get(result.target)
        msgs = [
            f'腾讯翻译:\n{source_language.language_name("zh")}->'
            f'{target_language.language_name("zh")}:\n',
        ]
        seg_translation_msgs = ['逐行翻译:']
        # 腾讯是分行识别的，故增加一个整段文本
        whole_source_text = ''
        img = Image.open(BytesIO(b64decode(base64_image)))
        for image_record in result.image_records:
            seg_translation_msgs.append(
                f'{image_record.source_text}\n->{image_record.target_text}\n',
            )
            whole_source_text += image_record.source_text
            cropped_img = img.crop(
                (
                    image_record.x,
                    image_record.y,
                    image_record.x + image_record.width,
                    image_record.y + image_record.height,
                ),
            )
            average_color = cropped_img.resize((1, 1)).getpixel((0, 0))
            bg = Image.new(
                'RGB',
                (image_record.width, image_record.height),
                average_color,
            )
            bg_draw = ImageDraw.Draw(bg)
            _font = (
                'msyh.ttc' if target_language.language == 'zh' else 'arial.ttf'
            )
            _, _, text_width, text_height = bg_draw.textbbox(
                (0, 0),
                image_record.target_text,
                font=ImageFont.truetype(_font, 100),
            )
            horizontal_ratio = image_record.width / text_width
            vertical_ratio = image_record.height / text_height
            line_number = floor(vertical_ratio / horizontal_ratio)
            line_number = line_number if line_number > 0 else 1
            actual_font_size = (
                min(
                    floor(100 * horizontal_ratio * line_number),
                    floor(100 * vertical_ratio / line_number),
                )
                - 1
            )
            font = ImageFont.truetype(_font, actual_font_size)
            luminance = (
                0.299 * average_color[0]
                + 0.587 * average_color[1]
                + 0.114 * average_color[2]
            )
            bg_draw.multiline_text(
                (0, 0),
                image_record.target_text,
                font=font,
                fill='white' if luminance < 128 else 'black',  # noqa: PLR2004
            )
            img.paste(bg, (image_record.x, image_record.y))
        img_output = BytesIO()
        img.save(img_output, format='PNG')
        msgs.append(img_output.getvalue())
        # 腾讯图片翻译识别是每行分开的，故尝试合一起整段翻译
        max_text_length = 6000
        if len(whole_source_text) < max_text_length:
            msgs.extend(['整段翻译:', f'{whole_source_text}'])
            result = await self._text_translate(
                whole_source_text,
                result.source,
                result.target,
            )
            if result is None:
                msgs.append('整段翻译失败')
            else:
                msgs.append(f'->{result.target_text}')
        else:
            msgs.append('文本过长，不提供整段翻译')
        msgs.extend(seg_translation_msgs)
        return msgs

    async def _ocr(self, image: Union[str, bytes]) -> Optional[OcrContent]:
        if isinstance(image, str):
            payload = {'ImageUrl': image}
        else:
            payload = {'ImageBase64': image.decode('utf-8')}
        payload.update(
            {
                'LanguageType': 'auto',
            },
        )
        headers = self._construct_headers(
            'GeneralBasicOCR',
            payload,
            service='ocr',
        )
        result = await self._handle_request(
            url='https://ocr.tencentcloudapi.com',
            method='POST',
            response_model=OcrResponse,
            json=payload,
            headers=headers,
        )
        return None if result is None else result.response

    async def ocr(self, image: Union[str, bytes]) -> list[str]:
        result = await self._ocr(image)
        if result is None:
            return ['OCR失败']
        msgs = [
            f'腾讯OCR结果\n'
            f'语言: {Language.get(result.lang).display_name("zh")}'
        ]
        seg_msgs = ['分行:']
        whole_text = ''
        for text in result.text_detections:
            seg_msgs.append(text.text)
            whole_text += text.text
        msgs.extend(['整段:', whole_text])
        msgs.extend(seg_msgs)
        return msgs
