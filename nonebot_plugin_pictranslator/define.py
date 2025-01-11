from typing import Union, Literal

from pydantic import VERSION
from langcodes import Language

PYDANTIC_V2 = int(VERSION.split('.', 1)[0]) == 2

SUPPORTED_APIS = ('tencent', 'youdao', 'baidu')
SUPPORTED_API = Literal['tencent', 'youdao', 'baidu']

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
