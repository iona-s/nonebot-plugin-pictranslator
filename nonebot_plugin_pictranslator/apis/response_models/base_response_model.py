from typing import Any
from typing_extensions import Self

from pydantic import VERSION, BaseModel

PYDANTIC_V2 = int(VERSION.split('.', 1)[0]) == 2

if PYDANTIC_V2:
    from pydantic import model_validator
else:
    from pydantic import root_validator  # noqa

__all__ = ['BaseResponseModel']


class BaseResponseModel(BaseModel):
    class Config:
        if PYDANTIC_V2:
            populate_by_name = True
        else:
            allow_population_by_field_name = True

    def to_dict(self, **kwargs):
        if PYDANTIC_V2:
            return super().model_dump(**kwargs)
        return super().dict(**kwargs)  # noqa

    def to_json(self, **kwargs):
        if PYDANTIC_V2:
            if 'ensure_ascii' in kwargs:
                kwargs.pop('ensure_ascii')
            return super().model_dump_json(**kwargs)
        return super().json(**kwargs)  # noqa

    @classmethod
    def from_obj(cls, obj: Any) -> Self:
        if PYDANTIC_V2:
            return cls.model_validate(obj)
        return cls.parse_obj(obj)  # noqa

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        if PYDANTIC_V2:
            return super().model_validate_json(json_str)
        return super().parse_raw(json_str)  # noqa

    if PYDANTIC_V2:

        @model_validator(mode='before')
        @classmethod
        def strip_whitespace(cls, values):
            for field, value in values.items():
                if isinstance(value, str):
                    values[field] = value.strip()
            return values

    else:

        @root_validator(pre=True)  # noqa
        def strip_whitespace(cls, values):  # noqa
            for field, value in values.items():
                if isinstance(value, str):
                    values[field] = value.strip()
            return values
