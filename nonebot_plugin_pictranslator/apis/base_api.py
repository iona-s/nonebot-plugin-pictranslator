from abc import ABC, abstractmethod
from typing import TypeVar, Optional

from nonebot import logger
from pydantic import ValidationError
from httpx import Response, AsyncClient

from .response_models.base_response_model import BaseResponseModel

__all__ = ['BaseApi', 'TranslateApi', 'R', 'TA']
R = TypeVar('R', bound=BaseResponseModel)
TA = TypeVar('TA', bound='TranslateApi')


class BaseApi:
    def __init__(self, client: AsyncClient) -> None:
        self.client: AsyncClient = client
        self.client.headers.clear()

    async def _request(
        self,
        url: str,
        method: str,
        **kwargs,
    ) -> Optional[Response]:
        try:
            logger.debug(f'Requesting [{method}] {url}')
            return await self.client.request(method, url, **kwargs)
        except Exception as e:
            logger.debug(f'Request kwargs: {kwargs}')
            logger.error(f'Request Failed: {e}')
            logger.exception(e)
            return None

    async def _handle_request(
        self,
        url: str,
        method: str,
        response_model: type[R],
        **kwargs,
    ) -> Optional[R]:
        response = await self._request(
            url,
            method,
            **kwargs,
        )
        if response is None:
            return None
        logger.debug(f'Response [{response.status_code}]')
        try:
            return response_model.from_obj(response.json())
        except ValidationError as e:
            logger.debug(f'Request kwargs: {kwargs}')
            logger.debug(f'Response content: {response.text}')
            logger.error(e)
            return None


class TranslateApi(BaseApi, ABC):
    @abstractmethod
    async def language_detection(self, text: str) -> Optional[str]:
        pass

    @abstractmethod
    async def text_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        pass

    @abstractmethod
    async def image_translate(
        self,
        base64_image: bytes,
        source_language: str,
        target_language: str,
    ) -> tuple[list[str], Optional[bytes]]:
        pass
