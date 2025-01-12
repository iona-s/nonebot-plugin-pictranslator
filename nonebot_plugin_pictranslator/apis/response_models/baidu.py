from typing import Optional
from typing_extensions import Self

from pydantic import Field

from .base_response_model import BaseResponseModel
from ...define import PYDANTIC_V2, REVERSE_BAIDU_LANG_CODE_MAP

if PYDANTIC_V2:
    from pydantic import model_validator

    class ModifiedBaiduModel(BaseResponseModel):
        @model_validator(mode='after')
        def correct_lang(self) -> Self:
            for attr in ('lang', 'source', 'target'):
                value = getattr(self, attr, None)
                if value in REVERSE_BAIDU_LANG_CODE_MAP:
                    setattr(self, attr, REVERSE_BAIDU_LANG_CODE_MAP[value])
            return self

else:
    from pydantic import root_validator  # noqa

    class ModifiedBaiduModel(BaseResponseModel):
        @root_validator  # noqa
        def correct_lang(cls, values):  # noqa N805
            for attr in ('lang', 'source', 'target'):
                value = values.get(attr)
                if value in REVERSE_BAIDU_LANG_CODE_MAP:
                    values[attr] = REVERSE_BAIDU_LANG_CODE_MAP[value]
            return values


class LanguageDetectionData(ModifiedBaiduModel):
    lang: str = Field(..., alias='src', description='语言代码')


class LanguageDetectionResponse(BaseResponseModel):
    error_code: str = Field(..., description='错误码')
    error_msg: str = Field(..., description='错误信息')
    data: LanguageDetectionData = Field(..., description='语言检测结果数据')


class LanguageTranslationData(BaseResponseModel):
    source_text: str = Field(..., alias='src', description='源文本')
    target_text: str = Field(..., alias='dst', description='目标文本')


class LanguageTranslationResponse(ModifiedBaiduModel):
    error_code: Optional[str] = Field(default=None, description='错误码')
    error_msg: Optional[str] = Field(default=None, description='错误信息')
    source: str = Field(..., alias='from', description='源语言')
    target: str = Field(..., alias='to', description='目标语言')
    data: list[LanguageTranslationData] = Field(
        ...,
        alias='trans_result',
        description='翻译结果数据',
    )


class ImageTranslationSection(BaseResponseModel):
    source_text: str = Field(..., alias='src', description='源文本')
    target_text: str = Field(..., alias='dst', description='目标文本')
    # 其余参数用不上


class ImageTranslationData(ModifiedBaiduModel):
    source: str = Field(..., alias='from', description='源语言')
    target: str = Field(..., alias='to', description='目标语言')
    source_text: str = Field(
        ...,
        alias='sumSrc',
        description='识别出来的翻译原文',
    )
    target_text: str = Field(..., alias='sumDst', description='翻译结果')
    render_image: str = Field(
        ...,
        alias='pasteImg',
        description='翻译结果图片base64串',
    )
    content: list[ImageTranslationSection] = Field(
        ...,
        description='详细分段识别内容',
    )


class ImageTranslationResponse(BaseResponseModel):
    error_code: str = Field(..., description='错误码')
    error_msg: str = Field(..., description='错误信息')
    data: ImageTranslationData = Field(..., description='翻译结果数据')
