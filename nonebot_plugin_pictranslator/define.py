from typing import Literal, Union

from langcodes import Language
from pydantic import VERSION

PYDANTIC_V2 = int(VERSION.split('.', 1)[0]) == 2  # noqa: PLR2004

ALL_APIS = ('baidu', 'tencent', 'youdao', 'baidu_cloud')
ALL_API = Literal['baidu', 'tencent', 'youdao', 'baidu_cloud']

SUPPORTED_TEXT_TRANSLATE_APIS = ('tencent', 'baidu', 'youdao', 'baidu_cloud')
SUPPORTED_TEXT_TRANSLATE_API = ALL_API

SUPPORTED_IMAGE_TRANSLATE_APIS = ('baidu', 'youdao', 'baidu_cloud', 'tencent')
SUPPORTED_IMAGE_TRANSLATE_API = ALL_API

SUPPORTED_OCR_APIS = ('baidu_cloud', 'tencent')
SUPPORTED_OCR_API = Literal['tencent', 'baidu_cloud']

LANGUAGE_TYPE = Union[Literal['auto'], Language]

# 百度这边很乱，先弄几个常用语言的了
BAIDU_LANG_CODE_MAP = {
    'zh-Hant': 'cht',
    'ja': 'jp',
    'ko': 'kor',
    'fr': 'fra',
    'es': 'spa',
    'ar': 'ara',
    'bg': 'bul',
    'et': 'est',
    'da': 'dan',
    'fi': 'fin',
    'sv': 'swe',
    'vie': 'vi',
}
REVERSE_BAIDU_LANG_CODE_MAP = {v: k for k, v in BAIDU_LANG_CODE_MAP.items()}
