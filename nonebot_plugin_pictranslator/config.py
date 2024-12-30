from typing import Optional

from nonebot import get_plugin_config
from pydantic import Field, BaseModel

__all__ = ['config', 'Config']


class Config(BaseModel):
    tianapi_key: Optional[str] = Field(
        default=None,
        description='天行数据API的key，用于中英词典查询',
    )

    tencent_id: Optional[str] = Field(
        default=None,
        description='腾讯API的secret_id',
    )
    tencent_key: Optional[str] = Field(
        default=None,
        description='腾讯API的secret_key',
    )
    enable_tencent: Optional[bool] = Field(
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
    enable_youdao: Optional[bool] = Field(
        default=None,
        description='是否启用腾讯API，填写了上两项则默认启用',
    )

    # youdao_app_id: Optional[str] = Field(
    #     default=None,
    #     description='有道翻译API的app_id',
    # )
    # youdao_secret_key: Optional[str] = Field(
    #     default=None,
    #     description='有道翻译API的secret_key',
    # )
    # youdao_use_llm: Optional[bool] = Field(
    #     default=False,
    #     description='是否使用有道翻译的大模型翻译功能',
    # )

    def initialize(self) -> None:
        if self.enable_tencent is None:
            if self.tencent_id and self.tencent_project_id:
                self.enable_tencent = True
            else:
                self.enable_tencent = False
        if self.enable_youdao is None:
            if self.youdao_id and self.youdao_key:
                self.enable_youdao = True
            else:
                self.enable_youdao = False


config = get_plugin_config(Config)
config.initialize()
