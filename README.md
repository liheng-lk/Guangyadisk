# 光鸭云盘助手

面向 MoviePilot 的光鸭云盘存储插件，由 **liheng-lk** 持续维护与发布。

> 维护仓库：`https://github.com/liheng-lk/Guangyadisk`
>
> 当前版本：**v2.2.16**

## 项目简介

光鸭云盘助手将光鸭云盘接入 MoviePilot，提供扫码/短信登录、网盘目录浏览、整理上传、下载、移动、复制、删除、WebDAV 与媒体直连等能力，并针对新版 MoviePilot 存储接口进行了兼容。

当前项目的功能整合、MoviePilot 适配、双登录流程、Vue UI、上传监控、网络重试与后续版本维护均由 `liheng-lk` 负责。

## 主要功能

- 光鸭云盘 App 扫码授权登录
- 手机号短信验证码登录
- Access Token / Refresh Token 自动保存与刷新
- MoviePilot 外部存储挂载
- 文件浏览、上传、下载、移动、复制、删除、重命名、新建目录
- MoviePilot 整理上传与上传完成确认
- 可选上传进度监控
- OSS 可续传上传与临时 DNS/网络异常重试
- `/stream` HTTP Range 流式代理
- `/browse` 目录浏览 API
- `/webdav` WebDAV 访问，可供 Emby / Jellyfin 等使用
- Vue Federation 插件主页与独立配置页
- PC / 平板 / 手机响应式界面

## 安装

### MoviePilot 插件市场

在 MoviePilot 自定义插件源中添加：

```text
https://github.com/liheng-lk/Guangyadisk
```

刷新插件市场后搜索 **光鸭云盘助手** 并安装。

### 本地安装

插件目录：

```text
plugins.v2/shukguangyadisk/
```

将该目录放入 MoviePilot 对应插件目录并重启 MoviePilot。

> `ShukGuangYaDisk` / `shukguangyadisk` 目前作为 MoviePilot 内部兼容标识保留，以避免已安装用户的插件 ID、配置与存储关系失效；用户可见名称统一为“光鸭云盘助手”。

## 登录方式

### 扫码登录

1. 打开“光鸭云盘助手”插件主页。
2. 选择“扫码登录”。
3. 使用光鸭云盘 App 扫描二维码并确认授权。
4. 插件轮询授权状态并自动保存 `access_token` 与 `refresh_token`。

扫码设备码与 Token 轮询流程按当前可用实现进行适配。

### 短信登录

1. 在登录方式中选择“短信登录”。
2. 输入绑定手机号并获取验证码。
3. 输入验证码完成登录。
4. 登录成功后自动保存 Token，并启用光鸭云盘存储。

## MoviePilot 兼容

项目已适配新版 MoviePilot 的 `StorageBase` 接口，包括 `get_item_strict(path)` 等调用，避免旧版实现出现：

```text
'GuangYaApi' object has no attribute 'get_item_strict'
```

MoviePilot 挂载存储名称统一为：

```text
光鸭云盘助手
```

历史版本中使用过的旧存储名称会在插件内部进行兼容迁移。

## 上传与进度监控

在插件设置中可以开启“上传进度监控”。开启后，可在 MoviePilot 系统日志中搜索：

```text
光鸭云盘助手
```

上传相关日志使用：

```text
【光鸭云盘助手】【上传】
```

网络重试日志使用：

```text
【光鸭云盘助手】【网络】
```

上传完成后如果光鸭任务接口没有及时返回 `fileId`，插件还会对目标目录执行同名/同大小文件确认，降低“文件实际已经上传但 MoviePilot 仍提示转移失败”的概率。

## Emby / Jellyfin

插件提供 WebDAV 与 HTTP 流式代理能力。

### WebDAV

```text
/api/v1/plugin/ShukGuangYaDisk/webdav
```

### HTTP 流式代理

插件同时提供 `/browse` 与 `/stream` API，支持 HTTP Range 请求。

## 开发结构

```text
plugins.v2/shukguangyadisk/
├── __init__.py                 # 当前插件入口与 MoviePilot 兼容层
├── _plugin_legacy.py           # 基础存储实现
├── guangya_api.py              # 当前 GuangYaApi 兼容层
├── guangya_api_legacy.py       # 基础 GuangYaApi 实现
├── guangya_client.py           # 当前认证与网络容错层
├── guangya_client_legacy.py    # 基础 HTTP / 文件 API 客户端
├── webdav_provider.py          # WebDAV 适配器
├── plugin.json
├── package.json
├── vite.config.js
└── dist/
    └── assets/
```

## 维护者

**liheng-lk**

- GitHub：`https://github.com/liheng-lk`
- 项目：`https://github.com/liheng-lk/Guangyadisk`

Issue 与 Pull Request 请提交到当前仓库。

## 致谢与参考

本项目在开发和兼容过程中参考、继承或借鉴了以下开源项目与实现，感谢相关作者和贡献者：

- **ShukeBta / Guangyadisk**：原始 GuangYaDisk / ShukGuangYaDisk 存储插件实现与历史代码基础。
- **KoWming / MoviePilot-Plugins**：光鸭云盘扫码设备码与 Token 轮询流程参考。
- **DDSRem-Dev / guangyaclient**：光鸭云盘短信登录、验证码与认证流程参考。
- **jxxghp / MoviePilot-Plugins**：MoviePilot V2/V3 插件结构、Vue Federation 与插件开发方式参考。
- 其他在 Git 历史、Issue、Pull Request 与依赖项目中留下贡献的开发者。

上述项目及其代码仍受各自许可证和版权声明约束；本仓库保留其必要的版权与许可信息。

## License

MIT License。详见 `LICENSE`。
