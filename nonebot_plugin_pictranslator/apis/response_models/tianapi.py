from typing import Optional

from pydantic import Field

from .base_response_model import BaseResponseModel

__all__ = ['DictionaryResponse']


class Result(BaseResponseModel):
    word: str = Field(..., description='单词')
    content: str = Field(..., description='内容')


class DictionaryResponse(BaseResponseModel):
    code: int = Field(..., description='状态码')
    msg: str = Field(..., description='错误信息')
    result: Optional[Result] = Field(
        default=None,
        description='返回结果集',
    )
