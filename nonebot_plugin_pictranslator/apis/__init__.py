from .base_api import TA
from .baidu import BaiduApi
from .tianapi import TianApi
from .youdao import YoudaoApi
from .tencent import TencentApi

__all__ = [
    'AVAILABLE_TRANSLATION_APIS',
    'TianApi',
    'YoudaoApi',
    'TencentApi',
    'TA',
]

AVAILABLE_TRANSLATION_APIS: dict[str, type[TA]] = {
    'youdao': YoudaoApi,
    'tencent': TencentApi,
    'baidu': BaiduApi,
}
