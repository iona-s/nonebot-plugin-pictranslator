from typing import Literal, Optional

from nonebot import get_plugin_config
from pydantic import Field, BaseModel

from .define import PYDANTIC_V2, SUPPORTED_API, SUPPORTED_APIS

if PYDANTIC_V2:
    from pydantic import model_validator

    model_validator = model_validator(mode='after')
else:
    from pydantic import root_validator  # noqa

    model_validator = root_validator()  # noqa

__all__ = ['config', 'Config']


class Config(BaseModel):
    text_translate_apis: list[SUPPORTED_API] = Field(
        default=None,
        description='文本翻译API的优先级，从高到低，默认以腾讯->百度->有道的顺序调用',
    )
    image_translate_apis: list[SUPPORTED_API] = Field(
        default=None,
        description='图片翻译API的优先级，从高到低，默认以百度->有道->腾讯的顺序调用',
    )
    text_translate_mode: Literal['auto', 'all'] = Field(
        default='auto',
        description='文本翻译模式，auto为自动选择一个api进行翻译，all为使用全部api进行翻译',
    )
    image_translate_mode: Literal['auto', 'all'] = Field(
        default='auto',
        description='图片翻译模式，auto为自动选择一个api进行翻译，all为使用全部api进行翻译',
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
    )
    baidu_key: Optional[str] = Field(
        default=None,
        description='百度翻译API的应用秘钥',
    )
    use_baidu: Optional[bool] = Field(
        default=None,
        description='是否启用百度API，填写了上两项则默认启用',
    )

    tianapi_key: Optional[str] = Field(
        default=None,
        description='天行数据API的key，用于中英词典查询',
    )
    use_tianapi: Optional[bool] = Field(
        default=None,
        description='是否启用天行数据API，填写了上一项则默认启用',
    )

    @model_validator
    @classmethod
    def initialize(cls, values):
        for field, value in values.items():
            if (
                field == 'use_tianapi'
                and value is None
                and values.get('tianapi_key')
            ):
                values[field] = True
            elif field.startswith('use_') and value is None:
                name = field[4:]
                if values.get(f'{name}_id') and values.get(f'{name}_key'):
                    values[field] = True
        if values.get('text_translate_apis') is None:
            values['text_translate_apis'] = [
                name for name in SUPPORTED_APIS if values.get(f'use_{name}')
            ]
        if values.get('image_translate_apis') is None:
            values['image_translate_apis'] = [
                name for name in SUPPORTED_APIS if values.get(f'use_{name}')
            ]
        return values


config = get_plugin_config(Config)
