from typing import Literal

from ..config import config
from ..define import ALL_API
from .baidu import BaiduApi
from .baidu_cloud import BaiduCloudApi
from .base_api import TA
from .tencent import TencentApi
from .tianapi import TianApi
from .youdao import YoudaoApi

__all__ = ['TA', 'TencentApi', 'TianApi', 'get_apis']

ALL_APIS: dict[ALL_API, type[TA]] = {
    'youdao': YoudaoApi,
    'tencent': TencentApi,
    'baidu': BaiduApi,
    'baidu_cloud': BaiduCloudApi,
}


def get_apis(
    api_type: Literal['text_translate', 'image_translate', 'ocr'],
    *,
    language_detection: bool = False,
) -> list[type[TA]]:
    apis = [ALL_APIS.get(name) for name in getattr(config, f'{api_type}_apis')]
    if language_detection:
        for api in {BaiduCloudApi, YoudaoApi}:
            if api in apis:
                apis.remove(api)
    return apis
