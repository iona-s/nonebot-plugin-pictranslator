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


class ImageTranslationSection(BaseResponseModel):
    source_text: str = Field(..., alias='context', description='原文')
    target_text: str = Field(..., alias='tranContent', description='翻译')
    # 还有很多用不上的用于渲染图片的参数


class ImageTranslationResponse(BaseResponseModel):
    error_code: str = Field(..., alias='errorCode', description='错误码')
    oriencation: str = Field(..., alias='orientation', description='图片方向')
    image_size: list[int] = Field(
        ...,
        alias='image_size',
        description='图片大小',
    )
    source_lang: str = Field(..., alias='lanFrom', description='源语言')
    target_lang: str = Field(..., alias='lanTo', description='目标语言')
    render_image: str = Field(
        ...,
        alias='render_image',
        description='渲染后的图片base64',
    )
    sections: list[ImageTranslationSection] = Field(
        ...,
        alias='resRegions',
        description='分区域识别详细结果',
    )

    @property
    def source(self) -> str:
        if self.source_lang == 'zh-CHS':
            return 'zh'
        return self.source_lang

    @property
    def target(self) -> str:
        if self.target_lang == 'zh-CHS':
            return 'zh'
        return self.target_lang
