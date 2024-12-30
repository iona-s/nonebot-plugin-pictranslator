from pydantic import Field

from .base_response_model import BaseResponseModel


class TextTranslationResponse(BaseResponseModel):
    error_code: str = Field(..., alias='errorCode', description='错误码')
    query: str = Field(..., alias='query', description='查询内容')
    translation: list[str] = Field(
        ...,
        alias='translation',
        description='翻译结果',
    )
    langs: str = Field(..., alias='l', description='源语言和目标语言')

    @property
    def source(self) -> str:
        source = self.langs.split('2')[0]
        if source == 'zh-CHS':
            return 'zh'
        return source

    @property
    def target(self) -> str:
        target = self.langs.split('2')[1]
        if target == 'zh-CHS':
            return 'zh'
        return target

    @property
    def target_text(self) -> str:
        return self.translation[0]
