# Shuk-光鸭云盘 (GuangYaDisk)

MoviePilot / Emby / Jellyfin 光鸭云盘存储插件（fork 维护版）。

> 当前维护仓库：`https://github.com/liheng-lk/Guangyadisk`
>
> 本仓库基于上游项目继续维护，保留原项目作者与历史贡献说明；当前 fork 的兼容修复、文档与发布由 `liheng-lk` 维护。

## 当前版本

**v2.2.5**

本版本主要完成两项兼容升级：

1. 兼容新版 MoviePilot 的 `get_item_strict()` 存储查询接口；
2. 登录页支持 **扫码登录 / 短信登录** 两种方式切换，并修复扫码设备码请求参数。

扫码登录仍为推荐方式。当前实现会向 `/v1/auth/device/code` 传递 `client_id`、`device_id` 与完整 `scope`，二维码直接编码服务端返回的 `verification_uri_complete`，授权完成后通过 `/v1/auth/token` 获取 `access_token` 与 `refresh_token`。

短信登录作为备用方式，使用 captcha → 发送验证码 → 校验验证码 → signin 的流程获取 Token。

## 功能

- 光鸭云盘 App 扫码授权登录
- 手机号短信验证码登录
- Token 自动刷新
- 文件浏览、上传、下载、删除、重命名、新建目录
- MoviePilot 外部存储挂载
- `/stream` HTTP 流式代理，支持 Range
- `/browse` 目录浏览 API
- `/webdav` WebDAV 访问，可用于 Emby / Jellyfin
- Vue 前端管理界面
- 延迟彻底删除与回收站清理

## 安装

### MoviePilot 插件市场

在 MoviePilot 的自定义插件源中添加：

```text
https://github.com/liheng-lk/Guangyadisk
```

刷新插件市场后搜索 **Shuk-光鸭云盘** 并安装。

### 本地安装

实际插件目录为：

```text
plugins.v2/shukguangyadisk/
```

如需手动安装，将该目录复制到 MoviePilot 对应的插件目录后重启 MoviePilot。

> 注意：旧文档中的 `plugins.v2/shuk-guangyadisk/` 为历史目录写法，当前仓库实际目录没有连字符。

## 登录方式

### 方式一：扫码登录（推荐）

1. 打开插件页面，选择 **扫码登录**。
2. 插件请求新的设备码，并生成二维码。
3. 使用光鸭云盘 App 扫码并确认授权。
4. 插件轮询授权状态，成功后自动保存 `access_token` 与 `refresh_token`。

### 方式二：短信登录

1. 在插件页面切换到 **短信登录**。
2. 输入光鸭云盘账号绑定手机号并发送验证码。
3. 输入短信验证码并登录。
4. 登录成功后同样保存 `access_token` 与 `refresh_token`，后续文件操作与扫码登录完全一致。

## MoviePilot 兼容说明

新版 MoviePilot 的 `StorageBase` 增加了 `get_item_strict(path)` 查询接口。旧版 GuangYaApi 只实现 `get_item()`，因此在新版整理/覆盖检查等流程中会出现：

```text
'GuangYaApi' object has no attribute 'get_item_strict'
```

当前维护版采用兼容层处理：保留原有 GuangYaApi 文件操作实现，并补充 `get_item_strict()`，保持上传、下载、移动、复制、删除等原逻辑不变。

## Emby / Jellyfin

### WebDAV

插件提供 `/webdav` 端点，可用于目录扫描和流式访问。具体访问地址取决于 MoviePilot 的部署地址和插件路由前缀。

### HTTP 流式代理

```text
GET /plugin/shuk-guangyadisk/browse?path=/BMH
GET /plugin/shuk-guangyadisk/stream?path=/BMH/电影/example.mkv
```

`/stream` 支持 HTTP Range，可用于拖动播放进度。

## 目录结构

```text
plugins.v2/shukguangyadisk/
├── __init__.py                 # 当前 fork 插件入口、双登录 API、版本元数据
├── _plugin_legacy.py           # 原插件主实现
├── guangya_api.py              # MoviePilot 新版兼容入口
├── guangya_api_legacy.py       # 原 GuangYaApi 完整实现
├── guangya_client.py           # 当前扫码 / 短信认证兼容层
├── guangya_client_legacy.py    # 原 HTTP / OAuth 客户端
├── webdav_provider.py          # WebDAV 适配器
├── plugin.json                 # 插件元数据
├── requirements.txt
└── dist/
    └── assets/
        ├── remoteEntry.js      # 双登录页面入口
        ├── remoteEntry_legacy.js
        └── __federation_expose_DualLoginPage.js
```

兼容层采用“保留原实现 + 小入口包装”的方式，目的是尽量降低升级 MoviePilot 时误伤原文件操作逻辑的风险。

## 版本历史

| 版本 | 说明 |
|---|---|
| **2.2.5** | 新增扫码 / 短信双登录；修复扫码 `device_id` 与 scope 参数；新增双登录页面 |
| 2.2.4 | 兼容新版 MoviePilot `get_item_strict`；同步 fork 文档、插件源、版本与维护者信息 |
| 2.2.3 | 重新构建 Vue 前端，修复组件自动关闭/加载问题 |
| 2.2.2 | 修复 Vue 表单、CSS 引用和 ZIP 目录问题 |
| 2.2.1 | 修复 WebDAV 语法及首次初始化问题 |
| 2.2.0 | 新增 WebDAV 服务端 |
| 2.1.0 | 新增 `/stream` 与 `/browse` |

## 开发与反馈

当前维护仓库：

```text
https://github.com/liheng-lk/Guangyadisk
```

Issue 与 Pull Request 请优先提交到当前维护仓库。

## 上游致谢

本项目为 fork 维护版本，基于原 GuangYaDisk / ShukGuangYaDisk 项目的代码和历史工作继续维护。原作者及既有贡献记录保留在 Git 历史中。

## License

MIT
