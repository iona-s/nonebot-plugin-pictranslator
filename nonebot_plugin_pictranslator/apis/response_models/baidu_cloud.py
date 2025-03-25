from pydantic import Field

from .baidu import FixBaiduLangCodeModel
from .base_response_model import BaseResponseModel


class TextTranslationResult(BaseResponseModel):
    source_text: str = Field(..., alias='src', description='源文本')
    target_text: str = Field(..., alias='dst', description='目标文本')


class TextTranslationContent(FixBaiduLangCodeModel):
    source: str = Field(..., alias='from', description='源语言')
    target: str = Field(..., alias='to', description='目标语言')
    trans_result: list[TextTranslationResult] = Field(
        ..., description='翻译结果'
    )

    @property
    def translation_result(self) -> TextTranslationResult:
        full_source_text = '\n'.join(
            [result.source_text for result in self.trans_result]
        )
        full_target_text = '\n'.join(
            [result.target_text for result in self.trans_result]
        )
        return TextTranslationResult(
            src=full_source_text, dst=full_target_text
        )


class TextTranslationResponse(BaseResponseModel):
    content: TextTranslationContent = Field(
        ..., alias='result', description='翻译结果数据'
    )


class ImageTranslationSection(BaseResponseModel):
    source_text: str = Field(..., alias='src', description='源文本')
    target_text: str = Field(..., alias='dst', description='目标文本')


class ImageTranslationContent(FixBaiduLangCodeModel):
    source: str = Field(..., alias='from', description='源语言')
    target: str = Field(..., alias='to', description='目标语言')
    source_text: str = Field(..., alias='sumSrc', description='未分段翻译原文')
    target_text: str = Field(..., alias='sumDst', description='未分段翻译结果')
    sections: list[ImageTranslationSection] = Field(
        ..., alias='content', description='详细分段识别内容'
    )
    render_image: str = Field(
        ..., alias='pasteImg', description='翻译结果图片base64串'
    )


class ImageTranslationResponse(BaseResponseModel):
    content: ImageTranslationContent = Field(
        ..., alias='data', description='翻译结果数据'
    )


class WordsResultContent(BaseResponseModel):
    words: str = Field(..., description='分行识别结果')


class ParagraphsResultContent(BaseResponseModel):
    words_result_idx: list[int] = Field(
        ..., description='该段落在words_result中的索引'
    )


class OcrResponse(BaseResponseModel):
    direction: int = Field(default=0, description='文字方向，未启用')
    words_result: list[WordsResultContent] = Field(..., description='识别结果')
    paragraphs_result: list[ParagraphsResultContent] = Field(
        ..., description='段落识别结果'
    )

    @property
    def paragraphs(self) -> list[str]:
        content = []
        for paragraph_info in self.paragraphs_result:
            first_index = paragraph_info.words_result_idx[0]
            last_index = paragraph_info.words_result_idx[-1]
            content.append(
                ''.join(
                    [
                        words_result.words
                        for words_result in self.words_result[
                            first_index : last_index + 1
                        ]
                    ]
                )
            )
        return content
