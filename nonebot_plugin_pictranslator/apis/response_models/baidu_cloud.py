from pydantic import Field

from .base_response_model import BaseResponseModel


class WordsResultData(BaseResponseModel):
    words: str = Field(..., description='分行识别结果')


class ParagraphsResultData(BaseResponseModel):
    words_result_idx: list[int] = Field(
        ..., description='该段落在words_result中的索引'
    )


class OcrResponse(BaseResponseModel):
    direction: int = Field(default=0, description='文字方向，未启用')
    words_result: list[WordsResultData] = Field(..., description='识别结果')
    paragraphs_result: list[ParagraphsResultData] = Field(
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
