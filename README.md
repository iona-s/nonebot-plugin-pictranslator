<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-pictranslator

_✨ NoneBot 插件简单描述 ✨_


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

## 支持的api
一般来说只要百度API就够用了，如果想同时返回多个API的结果，可以在[配置](#-配置)中设置对应`TRANSLATE_MODE`为`all`
### 图片翻译
- [x] [有道](https://ai.youdao.com/)  质量最好，但仅在注册账号时发放一次性免费余额
- [x] [百度](https://fanyi-api.baidu.com/)  比有道稍差，不过免费额度每月刷新
- [x] [腾讯](https://ai.qq.com/)  API不支持整段识别，且不返回渲染后的图片，故对复杂图片质量较差，不推荐，尽管免费额度每月刷新

### 文本翻译
- [x] [腾讯](https://ai.qq.com/)  免费额度每月刷新，量大
- [x] [有道](https://ai.youdao.com/)  仅在注册账号时发放一次性免费余额
- [x] [百度](https://fanyi-api.baidu.com/)  免费额度每月刷新，额度比腾讯少

### 词典功能
- [x] [天聚数行](https://www.tianapi.com/apiview/49)

### 语种识别
用于在未指定目标语言时检测源语言来自动选择目标语言
- [x] [腾讯](https://ai.qq.com/)
- [x] [百度](https://fanyi-api.baidu.com/)
- [ ] [有道](https://ai.youdao.com/)  没有对应API

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

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|         配置项          |   必填   |           默认值            |             可填值              |                            说明                            |
|:--------------------:|:------:|:------------------------:|:----------------------------:|:--------------------------------------------------------:|
| TEXT_TRANSLATE_APIS  |   是    | [tencent, baidu, youdao] | List[tencent, baidu, youdao] |                 启用哪些API，并以什么优先级调用进行文本翻译                  |
| IMAGE_TRANSLATE_APIS |   是    | [baidu, youdao, tencent] | List[tencent, youdao, baidu] |                       图片翻译API选择，同上                       |
| TEXT_TRANSLATE_MODE  |   否    |          'auto'          |        'auto', 'all'         |      文本翻译模式，`auto`代表以优先级调用第一个可用API，`all`代表调用全部可用api      |
| IMAGE_TRANSLATE_MODE |   否    |          'auto'          |        'auto', 'all'         |                        图片翻译模式，同上                         |
|       腾讯API相关        |   /    |            /             |              /               | 详见[腾讯文档](https://cloud.tencent.com/document/product/551) |
|      TENCENT_ID      | 若使用则必填 |            无             |            String            |                     腾讯API的secret_id                      |
|     TENCENT_KEY      | 若使用则必填 |            无             |            String            |                     腾讯API的secret_key                     |
|     USE_TENCENT      |   否    |            /             |             Bool             |                  是否启用腾讯API，填写了上两项则默认启用                   |
|  TENCENT_PROJECT_ID  |   否    |            0             |             Int              |                     腾讯API的project_id                     |
|  TENCENT_API_REGION  |   否    |       ap-shanghai        |            String            |                      腾讯API的region参数                      |
|       有道API相关        |   /    |            /             |              /               |       详见[有道文档](https://fanyi.youdao.com/openapi/)        |
|      YOUDAO_ID       | 若使用则必填 |            无             |            String            |                    有道翻译API的secret_id                     |
|      YOUDAO_KEY      | 若使用则必填 |            无             |            String            |                    有道翻译API的secret_key                    |
|      USE_YOUDAO      |   否    |            /             |             Bool             |                 是否启用有道翻译API，填写了上两项则默认启用                  |
|       百度API相关        |   /    |            /             |              /               |       详见[百度文档](https://fanyi-api.baidu.com/doc/11)       |
|       BAIDU_ID       | 若使用则必填 |            无             |            String            |                    百度翻译API的secret_id                     |
|      BAIDU_KEY       | 若使用则必填 |            无             |            String            |                    百度翻译API的secret_key                    |
|      USE_BAIDU       |   否    |            /             |             Bool             |                 是否启用百度翻译API，填写了上两项则默认启用                  |
|     TIANAPI_KEY      |   是    |            无             |            String            |                   天聚数行APIkey，用于中英词典查询                    |

## 🎉 使用
### 指令表
所有指令开头都需要添加`/`

|        指令        | 权限 | 需要@ | 范围 |                  说明                   |
|:----------------:|:--:|:---:|:--:|:-------------------------------------:|
|    词典查词 <单词>     | 群员 |  否  | 群聊 |                查询单词释义                 |
| (图片)翻译/<语言>译<语言> | 群员 |  否  | 群聊 | 核心翻译功能，使用`<语言>译<语言>`来指定源语言和目标语言，可回复触发 |
|       ocr        | 群员 |  否  | 群聊 |            进行图片文字提取，可回复触发             |
