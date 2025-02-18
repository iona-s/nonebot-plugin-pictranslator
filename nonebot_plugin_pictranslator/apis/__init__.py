from typing import Literal

from ..config import config
from ..define import SUPPORTED_API
from .baidu import BaiduApi
from .base_api import TA
from .tencent import TencentApi
from .tianapi import TianApi
from .youdao import YoudaoApi

__all__ = ['TA', 'TencentApi', 'TianApi', 'get_apis']

AVAILABLE_TRANSLATION_APIS: dict[SUPPORTED_API, type[TA]] = {
    'youdao': YoudaoApi,
    'tencent': TencentApi,
    'baidu': BaiduApi,
}


def get_apis(
    api_type: Literal['image', 'text'],
    *,
    language_detection: bool = False,
) -> list[type[TA]]:
    apis = [
        AVAILABLE_TRANSLATION_APIS.get(name)
        for name in getattr(config, f'{api_type}_translate_apis')
    ]
    if language_detection and YoudaoApi in apis:
        apis.remove(YoudaoApi)
    return apis
