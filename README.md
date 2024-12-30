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

一个基于Nonebot2的插件，提供多个api的文本及图片翻译功能，附带中英词典和ocr功能。\
WIP

## 支持的api
### 词典功能
- [x] [天聚数行](https://www.tianapi.com/apiview/49)

### 图文翻译
- [x] [腾讯](https://ai.qq.com/)
- [ ] [有道](https://ai.youdao.com/)  WIP
- [ ] [百度](https://fanyi-api.baidu.com/)  WIP

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

    plugins = ["nonebot_plugin_template"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|        配置项         |   必填   | 默认值 |  值类型   |                           说明                           |
|:------------------:|:------:|:---:|:------:|:------------------------------------------------------:|
|    TIANAPI_KEY     |   是    |  无  | String |                  天聚数行APIkey，用于中英词典查询                   |
|      腾讯API相关       |   /    |  /  |   /    | 详见[文档](https://cloud.tencent.com/document/product/551) |
|     TENCENT_ID     | 若使用则必填 |  无  | String |                    腾讯API的secret_id                     |
|    TENCENT_KEY     | 若使用则必填 |  无  | String |                    腾讯API的secret_key                    |
|    USE_TENCENT     |   否    |  /  |  Bool  |                 是否启用腾讯API，填写了上两项则默认启用                  |
| TENCENT_PROJECT_ID |   否    |  0  |  Int   |                    腾讯API的project_id                    |
| TENCENT_API_REGION |   否    |  无  | String |                    腾讯API的secret_key                    |
|      有道API相关       |   /    |  /  |   /    |       详见[文档](https://fanyi.youdao.com/openapi/)        |
|     YOUDAO_ID      | 若使用则必填 |  无  | String |                    有道API的secret_id                     |
|     YOUDAO_KEY     | 若使用则必填 |  无  | String |                    有道API的secret_key                    |
|     USE_YOUDAO     |   否    |  /  |  Bool  |                 是否启用有道API，填写了上两项则默认启用                  |
|      百度API相关       |  WIP   |

## 🎉 使用
### 指令表
|        指令        | 权限 | 需要@ | 范围 |                       说明                        |
|:----------------:|:--:|:---:|:--:|:-----------------------------------------------:|
|    词典/查词 [单词]    | 群员 |  否  | 群聊 |                     查询单词意思                      |
| (图片)翻译/[语言]译[语言] | 群员 |  否  | 群聊 | 进行翻译，使用`[语言]译[语言]`来指定源语言和目标语言。在指令前添加`图片`可进行图片翻译 |
|       ocr        | 群员 |  否  | 群聊 |                    进行图片文字提取                     |
