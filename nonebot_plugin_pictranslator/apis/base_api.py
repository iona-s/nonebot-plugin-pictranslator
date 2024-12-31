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
        log_kwargs_to_trace: bool = False,
        **kwargs,
    ) -> Optional[Response]:
        try:
            debug_msg = f'Requesting [{method}] {url}'
            if log_kwargs_to_trace:
                logger.debug(debug_msg)
                logger.trace(f'with {kwargs}')
            else:
                debug_msg += f' with {kwargs}'
                logger.debug(debug_msg)
            return await self.client.request(method, url, **kwargs)
        except Exception as e:
            logger.error(f'Request [{method}] {url} failed: {e}')
            logger.exception(e)
            return None

    async def _handle_request(
        self,
        url: str,
        method: str,
        response_model: type[R],
        *,
        log_kwargs_to_trace: bool = False,
        log_response_to_trace: bool = False,
        **kwargs,
    ) -> Optional[R]:
        response = await self._request(
            url,
            method,
            log_kwargs_to_trace,
            **kwargs,
        )
        if response is None:
            return None
        if log_response_to_trace:
            logger.debug(f'Response status code: {response.status_code}')
            logger.trace(f'Response: {response.text}')
        else:
            logger.debug(f'Response [{response.status_code}] {response.text}')
        try:
            return response_model.from_obj(response.json())
        except ValidationError as e:
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
