from .baidu import BaiduApi
from .base_api import TA
from .tencent import TencentApi
from .tianapi import TianApi
from .youdao import YoudaoApi

__all__ = [
    'AVAILABLE_TRANSLATION_APIS',
    'TA',
    'TencentApi',
    'TianApi',
    'YoudaoApi',
]

AVAILABLE_TRANSLATION_APIS: dict[str, type[TA]] = {
    'youdao': YoudaoApi,
    'tencent': TencentApi,
    'baidu': BaiduApi,
}
