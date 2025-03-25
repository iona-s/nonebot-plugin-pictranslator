from typing import Literal, Optional

from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel, Field

from .define import (
    ALL_APIS,
    SUPPORTED_IMAGE_TRANSLATE_API,
    SUPPORTED_IMAGE_TRANSLATE_APIS,
    SUPPORTED_OCR_API,
    SUPPORTED_OCR_APIS,
    SUPPORTED_TEXT_TRANSLATE_API,
    SUPPORTED_TEXT_TRANSLATE_APIS,
)

__all__ = ['Config', 'config']


class Config(BaseModel):
    pictranslate_command_start: set[str] = Field(
        default=None,
        description='配置命令的起始字符',
    )
    ocr_use_image_url: bool = Field(
        default=False,
        description='是否允许在调用ocr相应api时使用图片url',
    )

    text_translate_apis: list[SUPPORTED_TEXT_TRANSLATE_API] = Field(
        default=None,
        description='文本翻译API的优先级，从高到低，默认以腾讯->百度->有道的顺序调用',
    )
    image_translate_apis: list[SUPPORTED_IMAGE_TRANSLATE_API] = Field(
        default=None,
        description='图片翻译API的优先级，从高到低，默认以百度->有道->腾讯的顺序调用',
    )
    ocr_apis: list[SUPPORTED_OCR_API] = Field(
        default=None,
        description='ocr的优先级，从高到低，默认以百度智能云->腾讯的顺序调用',
    )
    # auto为选择优先级最高的api，random为随机选择一个，all为使用全部api'
    text_translate_mode: Literal['auto', 'random', 'all'] = Field(
        default='auto',
        description='文本翻译模式',
    )
    image_translate_mode: Literal['auto', 'random', 'all'] = Field(
        default='auto',
        description='图片翻译模式',
    )
    ocr_mode: Literal['auto', 'random', 'all'] = Field(
        default='auto', description='ocr模式'
    )

    tencent_id: Optional[str] = Field(
        default=None,
        description='腾讯API的secret_id',
    )
    tencent_key: Optional[str] = Field(
        default=None,
        description='腾讯API的secret_key',
    )
    use_tencent: Optional[bool] = Field(
        default=None,
        description='是否启用腾讯API，填写了上两项则默认启用',
    )
    tencent_project_id: Optional[int] = Field(
        default=0,
        description='腾讯翻译API的project_id',
    )
    tencent_api_region: Optional[str] = Field(
        default='ap-shanghai',
        description='腾讯翻译API的region参数',
    )

    youdao_id: Optional[str] = Field(
        default=None,
        description='有道翻译API的应用id',
    )
    youdao_key: Optional[str] = Field(
        default=None,
        description='有道翻译API的应用秘钥',
    )
    use_youdao: Optional[bool] = Field(
        default=None,
        description='是否启用有道API，填写了上两项则默认启用',
    )

    baidu_id: Optional[str] = Field(
        default=None,
        description='百度翻译API的应用id',
        coerce_numbers_to_str=True,
    )

    baidu_key: Optional[str] = Field(
        default=None,
        description='百度翻译API的应用秘钥',
    )
    use_baidu: Optional[bool] = Field(
        default=None,
        description='是否启用百度开放翻译平台API，填写了上两项则默认启用',
    )

    baidu_cloud_id: Optional[str] = Field(
        default=None,
        description='百度智能云API的应用APIKEY',
        coerce_numbers_to_str=True,
    )
    baidu_cloud_key: Optional[str] = Field(
        default=None,
        description='百度智能云API的应用Secret KEY',
    )
    use_baidu_cloud: Optional[bool] = Field(
        default=None,
        description='是否启用百度智能云API，填写了上两项则默认启用',
    )

    tianapi_key: Optional[str] = Field(
        default=None,
        description='天行数据API的key，用于中英词典查询',
    )
    use_tianapi: Optional[bool] = Field(
        default=None,
        description='是否启用天行数据API，填写了上一项则默认启用',
    )

    def initialize(self) -> None:  # noqa C901
        if self.pictranslate_command_start is None:
            self.pictranslate_command_start = get_driver().config.command_start
        if self.use_tianapi is None and self.tianapi_key:
            self.use_tianapi = True
        for name in ALL_APIS:
            if (
                getattr(self, f'use_{name}') is None
                and getattr(self, f'{name}_id')
                and getattr(self, f'{name}_key')
            ):
                setattr(self, f'use_{name}', True)
        if self.text_translate_apis is None:
            self.text_translate_apis = []
            for name in SUPPORTED_TEXT_TRANSLATE_APIS:
                # TODO baidu_cloud WIP
                if getattr(self, f'use_{name}'):
                    self.text_translate_apis.append(name)
        if self.image_translate_apis is None:
            self.image_translate_apis = []
            for name in SUPPORTED_IMAGE_TRANSLATE_APIS:
                if getattr(self, f'use_{name}'):
                    self.image_translate_apis.append(name)
        if self.ocr_apis is None:
            self.ocr_apis = []
            for name in SUPPORTED_OCR_APIS:
                if getattr(self, f'use_{name}'):
                    self.ocr_apis.append(name)

    @property
    def command_start_pattern(self) -> str:
        if (
            not self.pictranslate_command_start
            or self.pictranslate_command_start == {''}
        ):
            return ''
        command_start = list(self.pictranslate_command_start)
        if len(command_start) == 1:
            return command_start[0]
        if '' in command_start:
            command_start.remove('')
        pattern = '(?:' + '|'.join(command_start) + ')'
        if '' in self.pictranslate_command_start:
            pattern += '?'
        return pattern


config = get_plugin_config(Config)
config.initialize()
