# Shuk-光鸭云盘

当前维护仓库：`https://github.com/liheng-lk/Guangyadisk`

MoviePilot / Emby / Jellyfin 光鸭云盘存储插件，支持扫码登录、文件管理、存储挂载、流式播放与 WebDAV。

## 版本

当前版本：**2.2.4**

v2.2.4 主要修复新版 MoviePilot 调用 `get_item_strict()` 时出现：

```text
'GuangYaApi' object has no attribute 'get_item_strict'
```

当前实现保留原 GuangYaApi 完整逻辑，并通过兼容入口补齐新版存储接口。

## 安装

MoviePilot 自定义插件源填写：

```text
https://github.com/liheng-lk/Guangyadisk
```

当前实际插件目录：

```text
plugins.v2/shukguangyadisk/
```

请不要再使用旧文档中的 `plugins.v2/shuk-guangyadisk/` 路径。

## 主要功能

- 扫码 / 设备码登录
- Token 自动刷新
- 浏览、上传、下载、删除、重命名、新建目录
- MoviePilot 存储挂载
- `/stream` HTTP 流式代理
- `/browse` 目录浏览 API
- `/webdav` WebDAV 服务
- Vue 前端管理页面

## 兼容层结构

```text
shukguangyadisk/
├── __init__.py
├── _plugin_legacy.py
├── guangya_api.py
├── guangya_api_legacy.py
├── guangya_client.py
├── webdav_provider.py
├── plugin.json
└── dist/
```

`guangya_api_legacy.py` 保存原有完整文件操作逻辑；`guangya_api.py` 作为兼容入口增加新版 MoviePilot 所需的 `get_item_strict()`。

`_plugin_legacy.py` 保存原插件主实现；`__init__.py` 负责当前 fork 的版本号、维护者和仓库地址。

## 维护说明

这是基于上游项目继续维护的 fork。原作者及历史贡献保留在 Git 历史中；当前 fork 的兼容修复和发布由 `liheng-lk` 维护。

## License

MIT
