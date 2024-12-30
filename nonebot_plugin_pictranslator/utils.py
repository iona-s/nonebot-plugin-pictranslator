from typing import Optional

from .define import LANGUAGE_INDEX

__all__ = ['get_languages']


def get_languages(
    source: Optional[str],
    target: Optional[str],
) -> tuple[str, Optional[str]]:
    if source and target:
        source_language = LANGUAGE_INDEX.get(source, None)
        target_language = LANGUAGE_INDEX.get(target, None)
        if not source_language or not target_language:
            return '语种输入有误或不支持', None
    else:
        source_language = 'auto'
        target_language = 'auto'
    return source_language, target_language
