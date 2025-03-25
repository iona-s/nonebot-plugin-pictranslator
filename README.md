<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-pictranslator

_✨ NoneBot 翻译插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/iona-s/nonebot-plugin-pictranslator.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-pictranslator">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-pictranslator.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

一个基于Nonebot2的插件，提供多个api的文本及图片翻译功能，附带中英词典和ocr功能。

### 支持的API
一般来说只要百度API就够用了，如果想同时返回多个API的结果，可以在[配置](#-配置)中填入多个api并将对应`TRANSLATE_MODE`该为`all`

|                     API                     | 图片翻译 | 文本翻译 | 语种识别 | ocr | 词典 |
|:-------------------------------------------:|:----:|:----:|:----:|:---:|:--:|
|        [有道](https://ai.youdao.com/)         |  ✅   |  ✅   |  ❌   |  ❌  | ❌  |
|  [百度翻译开放平台](https://fanyi-api.baidu.com/)   |  ✅   |  ✅   |  ✅   |  ❌  | ❌  |
|        [百度智能云](https://ai.baidu.com)        |  ✅   |  ✅   |  ❌   |  ✅  | 🚧 |
| [腾讯](https://cloud.tencent.com/product/tmt) |  ✅   |  ✅   |  ✅   |  ✅  | ❌  |
| [天聚数行](https://www.tianapi.com/apiview/49)  |  ❌   |  ❌   |  ❌   |  ❌  | ✅  |

有道整体来说质量最好，但免费额度只一次性发放\
百度智能云翻译相关资源为一次性发放，OCR为每月刷新，词典不提供免费资源，创建应用时注意把OCR和机器翻译一同勾上\
百度翻译开放平台和腾讯的免费额度均每月刷新\
腾讯图片翻译不返回渲染后图片，为插件本地渲染，同时只能横向分行识别，质量较差\
天聚数行只提供词典功能

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-pictranslator

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-pictranslator
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-pictranslator
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-pictranslator
</details>
<details>
<summary>uv</summary>

    uv add nonebot-plugin-pictranslator
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-pictranslator
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_pictranslator"]

</details>

## 🎉 使用
**需至少配置一个api才能使用**\
要自动识别语种，需要配置腾讯或百度api\
详见[配置](#-配置)
### 指令表
所有指令默认使用`nonebot`的`COMMAND_START`配置项作为起始字符，可在[配置](#-配置)中修改

|        指令        | 权限 | 需要@ | 范围 |                  说明                   |
|:----------------:|:--:|:---:|:--:|:-------------------------------------:|
|    词典/查词 <单词>    | 群员 |  否  | 群聊 |                查询单词释义                 |
| (图片)翻译/<语言>译<语言> | 群员 |  否  | 群聊 | 核心翻译功能，使用`<语言>译<语言>`来指定源语言和目标语言，可回复触发 |
|       ocr        | 群员 |  否  | 群聊 |            进行图片文字提取，可回复触发             |

### 示例
以下指令均默认使用`/`作为起始字符
- 词典功能  需配置天行api
    ```
    /词典 hello
    ```
以下指令均可回复触发，或是先只发指令后发送内容
- 文本翻译功能
    ```
    /翻译 你好
    /中译英 你好
    ```
- 图片翻译功能
    ```
    /翻译 [图片]
    /中译英 [图片]
    ```
- ocr功能  需配置腾讯api
    ```
    /ocr [图片]
    ```

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中视情况添加

|            配置项             |   必填   |              默认值               |                        可填值                         |                               说明                               |
|:--------------------------:|:------:|:------------------------------:|:--------------------------------------------------:|:--------------------------------------------------------------:|
| PICTRANSLATE_COMMAND_START |   否    |  同`nonebot`自身的`COMMAND_START`  |                     Array[str]                     |           配置命令的起始字符，默认使用`nonebot`自身的`COMMAND_START`            |
|     OCR_USE_IMAGE_URL      |   否    |             false              |                        bool                        |            是否允许在调用ocr api时传递图片url而不是图片本身，可能会有一些未知问题            |
|    TEXT_TRANSLATE_APIS     |   否    | ['tencent', 'baidu', 'youdao'] | Array['tencent', 'baidu', 'youdao', 'baidu_cloud'] |                    启用哪些API，并以什么优先级调用进行文本翻译                     |
|    IMAGE_TRANSLATE_APIS    |   否    |      ['baidu', 'tencent']      |                         同上                         |                          图片翻译API选择，同上                          |
|          OCR_APIS          |   否    |   ['baidu_cloud', 'tencent']   |          Array['baidu_cloud', 'tencent']           |                          ocrAPI选择，同上                           |
|    TEXT_TRANSLATE_MODE     |   否    |             'auto'             |              'auto', 'random', 'all'               | 文本翻译模式，`auto`代表依优先级调用第一个可用API，`random`为随机选用一个，`all`代表调用全部可用api |
|    IMAGE_TRANSLATE_MODE    |   否    |               同上               |                         同上                         |                           图片翻译模式，同上                            |
|          OCR_MODE          |   否    |               同上               |                         同上                         |                            ocr模式，同上                            |
|          腾讯API相关           |   /    |               /                |                         /                          |    详见[腾讯文档](https://cloud.tencent.com/document/product/551)    |
|         TENCENT_ID         | 若使用则必填 |               无                |                       String                       |                        腾讯API的secret_id                         |
|        TENCENT_KEY         | 若使用则必填 |               无                |                       String                       |                        腾讯API的secret_key                        |
|        USE_TENCENT         |   否    |               /                |                        Bool                        |                     是否启用腾讯API，填写了上两项则默认启用                      |
|     TENCENT_PROJECT_ID     |   否    |               0                |                        Int                         |                        腾讯API的project_id                        |
|     TENCENT_API_REGION     |   否    |          ap-shanghai           |                       String                       |                         腾讯API的region参数                         |
|          有道API相关           |   /    |               /                |                         /                          |          详见[有道文档](https://ai.youdao.com/doc.s#guide)           |
|         YOUDAO_ID          | 若使用则必填 |               无                |                       String                       |                          有道翻译API的应用ID                          |
|         YOUDAO_KEY         | 若使用则必填 |               无                |                       String                       |                          有道翻译API的应用密钥                          |
|         USE_YOUDAO         |   否    |               /                |                        Bool                        |                    是否启用有道翻译API，填写了上两项则默认启用                     |
|          百度API相关           |   /    |               /                |                         /                          |          详见[百度文档](https://fanyi-api.baidu.com/doc/11)          |
|          BAIDU_ID          | 若使用则必填 |               无                |                       String                       |                        百度翻译开放平台的APP ID                         |
|         BAIDU_KEY          | 若使用则必填 |               无                |                       String                       |                          百度翻译开放平台的密钥                           |
|         USE_BAIDU          |   否    |               /                |                        Bool                        |                    是否启用百度翻译API，填写了上两项则默认启用                     |
|          百度API相关           |   /    |               /                |                         /                          |  详见[百度智能云文档](https://ai.baidu.com/ai-doc/REFERENCE/Tktjypljq)  |
|       BAIDU_CLOUD_ID       | 若使用则必填 |               无                |                       String                       |                        百度智能云的应用API KEY                         |
|      BAIDU_CLOUD_KEY       | 若使用则必填 |               无                |                       String                       |                       百度智能云的应用Secret KEY                       |
|      USE_BAIDU_CLOUD       |   否    |               /                |                        Bool                        |                    是否启用百度智能云API，填写了上两项则默认启用                    |
|        TIANAPI_KEY         | 若使用则必填 |               无                |                       String                       |                      天聚数行APIkey，用于中英词典查询                       |


## 📜 TODOs
- [ ] ocr实现指定目标语言
- [ ] 在命令中指定所使用的api
- [ ] 实现`auto`模式下一个接口资源使用完后自动切换到下一个
