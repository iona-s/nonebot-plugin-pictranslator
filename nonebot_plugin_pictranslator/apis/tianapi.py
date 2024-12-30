from typing import Optional

from ..config import config
from .base_api import BaseApi
from .response_models.tianapi import DictionaryResponse


class TianApi(BaseApi):
    async def query_dictionary(
        self,
        word: str,
    ) -> Optional[DictionaryResponse]:
        url = f'https://apis.tianapi.com/enwords/index?key={config.tianapi_key}&word={word}'
        return await self._handle_request(url, 'get', DictionaryResponse)
