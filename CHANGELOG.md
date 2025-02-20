# v1.0.5
### 问题修复
1. `ocr`指令未正常使用插件配置项中的`pictranlate_command_start`
2. 腾讯ocrapi返回的日语语言代码不符合ISO 639标准，导致无法正确给出语言名称

# v1.0.4
### 新增功能
1. 增加`pictranlate_command_start`配置项\
用于配置命令的起始字符，默认使用`nonebot`的`COMMAND_START`配置项
