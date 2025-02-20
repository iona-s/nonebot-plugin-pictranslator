from pydantic import Field
from typing_extensions import Self

from .base_response_model import BaseResponseModel

# 分为整体的内容的解析及返回内容的Response部分

__all__ = [
    'ImageTranslationContent',
    'ImageTranslationResponse',
    'LanguageDetectionContent',
    'LanguageDetectionResponse',
    'OcrContent',
    'OcrResponse',
    'TextTranslationContent',
    'TextTranslationResponse',
]

from ...define import PYDANTIC_V2

# 暂时只注意到日语有问题
# 分别是语种识别的jp和ocr的jap
if PYDANTIC_V2:
    from pydantic import model_validator

    class FixTencentLangCodeModel(BaseResponseModel):
        @model_validator(mode='after')
        def correct_lang(self) -> Self:
            for attr in ('lang', 'source', 'target'):
                value = getattr(self, attr, None)
                if value in {'jp', 'jap'}:
                    setattr(self, attr, 'ja')
            return self

else:
    from pydantic import root_validator

    class FixTencentLangCodeModel(BaseResponseModel):
        @root_validator
        def correct_lang(cls, values):  # noqa N805
            for attr in ('lang', 'source', 'target'):
                value = values.get(attr)
                if value in {'jp', 'jap'}:
                    values[attr] = 'ja'
            return values


class LanguageDetectionContent(FixTencentLangCodeModel):
    lang: str = Field(..., alias='Lang', description='语言代码')


class LanguageDetectionResponse(BaseResponseModel):
    response: LanguageDetectionContent = Field(
        ...,
        alias='Response',
        description='返回内容',
    )


class TextTranslationContent(BaseResponseModel):
    target_text: str = Field(..., alias='TargetText', description='目标文本')
    source: str = Field(..., alias='Source', description='源语言')
    target: str = Field(..., alias='Target', description='目标语言')


class TextTranslationResponse(BaseResponseModel):
    response: TextTranslationContent = Field(
        ...,
        alias='Response',
        description='返回内容',
    )


class ImageRecord(BaseResponseModel):
    source_text: str = Field(..., alias='SourceText', description='源文本')
    target_text: str = Field(..., alias='TargetText', description='目标文本')
    x: int = Field(..., alias='X', description='左上角X坐标')
    y: int = Field(..., alias='Y', description='左上角Y坐标')
    width: int = Field(..., alias='W', description='宽度')
    height: int = Field(..., alias='H', description='高度')


class ImageTranslationContent(BaseResponseModel):
    session_uuid: str = Field(
        ...,
        alias='SessionUuid',
        description='会话 UUID',
    )
    source: str = Field(..., alias='Source', description='源语言')
    target: str = Field(..., alias='Target', description='目标语言')
    image_records_dict: dict[str, list[ImageRecord]] = Field(
        ...,
        alias='ImageRecord',
        description='图片记录',
    )

    @property
    def image_records(self) -> list[ImageRecord]:
        return self.image_records_dict['Value']


class ImageTranslationResponse(BaseResponseModel):
    response: ImageTranslationContent = Field(
        ...,
        alias='Response',
        description='返回内容',
    )


class TextDetectionContent(BaseResponseModel):
    text: str = Field(..., alias='DetectedText', description='文本')
    confidence: int = Field(..., alias='Confidence', description='置信度')


class OcrContent(FixTencentLangCodeModel):
    text_detections: list[TextDetectionContent] = Field(
        ...,
        alias='TextDetections',
        description='文本检测',
    )
    lang: str = Field(..., alias='Language', description='语言')


class OcrResponse(BaseResponseModel):
    response: OcrContent = Field(
        ...,
        alias='Response',
        description='返回内容',
    )
