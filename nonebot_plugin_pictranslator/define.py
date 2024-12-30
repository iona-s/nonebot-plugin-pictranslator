LANGUAGE_NAME_INDEX = {
    'zh': '简体中文',
    'zh-TW': '繁体中文',
    'en': '英语',
    'ja': '日语',
    'ko': '韩语',
    'fr': '法语',
    'es': '西班牙语',
    'it': '意大利语',
    'de': '德语',
    'tr': '土耳其语',
    'ru': '俄语',
    'pt': '葡萄牙语',
    'vi': '越南语',
    'id': '印尼语',
    'th': '泰语',
    'ms': '马来西亚语',
    'ar': '阿拉伯语',
    'hi': '印地语',
}
LANGUAGE_SURNAMES = {
    'zh': ['中文', '中'],
    'zh-TW': ['繁体', '繁', '繁中'],
    'en': ['英'],
    'ja': ['日'],
    'ko': ['韩'],
    'fr': ['法'],
    'es': ['西', '西班牙'],
    'it': ['意', '意大利'],
    'de': ['德', '德国'],
    'tr': ['土', '土耳其'],
    'ru': ['俄'],
    'pt': ['葡'],
    'vi': ['越'],
    'id': ['印尼'],
    'th': ['泰'],
    'ms': ['马来', '马'],
    'ar': ['阿拉伯', '阿'],
    'hi': ['印地', '印'],
}
LANGUAGE_INDEX = {
    name: language for language, name in LANGUAGE_NAME_INDEX.items()
}
for language in LANGUAGE_NAME_INDEX:
    LANGUAGE_INDEX[language] = language
for language, surnames in LANGUAGE_SURNAMES.items():
    for surname in surnames:
        LANGUAGE_INDEX[surname] = language
LANGUAGE_INDEX['翻'] = 'auto'
