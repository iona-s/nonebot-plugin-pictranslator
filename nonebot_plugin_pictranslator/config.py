from typing import Literal, Optional

from nonebot import get_plugin_config
from pydantic import Field, BaseModel

__all__ = ['config', 'Config']


class Config(BaseModel):
    tianapi_key: Optional[str] = Field(
        default=None,
        description='天行数据API的key，用于中英词典查询',
    )
    # TODO add baidu
    translate_api_choice: Literal['tencent', 'youdao', 'random', 'all'] = (
        Field(
            default='all',
            description='选择翻译所使用的API',
        )
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
        description='是否启用腾讯API，填写了上两项则默认启用',
    )

    def initialize(self) -> None:
        for name in ['tencent', 'youdao']:  # TODO add baidu
            if getattr(self, f'use_{name}') is None:
                if getattr(self, f'{name}_id') and getattr(
                    self,
                    f'{name}_key',
                ):
                    setattr(self, f'use_{name}', True)
                else:
                    setattr(self, f'use_{name}', False)


config = get_plugin_config(Config)
config.initialize()
