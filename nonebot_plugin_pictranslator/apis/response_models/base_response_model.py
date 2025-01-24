from typing import Any

from pydantic import BaseModel
from typing_extensions import Self

from ...define import PYDANTIC_V2

# if PYDANTIC_V2:
#     from pydantic import model_validator
#     model_validator = model_validator(mode='before')
# else:
#     from pydantic import root_validator
#     model_validator = root_validator(pre=True)

__all__ = ['BaseResponseModel']


class BaseResponseModel(BaseModel):
    class Config:
        if PYDANTIC_V2:
            populate_by_name = True
        else:
            allow_population_by_field_name = True

    def to_dict(self, **kwargs) -> dict:
        if PYDANTIC_V2:
            return super().model_dump(**kwargs)
        return super().dict(**kwargs)

    def to_json(self, **kwargs) -> str:
        if PYDANTIC_V2:
            if 'ensure_ascii' in kwargs:
                kwargs.pop('ensure_ascii')
            return super().model_dump_json(**kwargs)
        return super().json(**kwargs)

    @classmethod
    def from_obj(cls, obj: Any) -> Self:
        if PYDANTIC_V2:
            return cls.model_validate(obj)
        return cls.parse_obj(obj)

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        if PYDANTIC_V2:
            return super().model_validate_json(json_str)
        return super().parse_raw(json_str)

    # @model_validator
    # @classmethod
    # def strip_whitespace(cls, values):
    #     for field, value in values.items():
    #         if isinstance(value, str):
    #             values[field] = value.strip()
    #     return values
