from typing import Optional

from .base_api import TranslateApi


class BaiduApi(TranslateApi):
    async def text_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        raise NotImplementedError

    async def image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> tuple[list[str], Optional[bytes]]:
        raise NotImplementedError

    async def language_detection(self, text: str) -> str:
        raise NotImplementedError
