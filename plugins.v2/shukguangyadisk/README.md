# Shuk-光鸭云盘

当前维护仓库：`https://github.com/liheng-lk/Guangyadisk`

MoviePilot / Emby / Jellyfin 光鸭云盘存储插件，支持 **扫码登录 + 短信登录**、文件管理、存储挂载、流式播放与 WebDAV。

## 版本

当前版本：**2.2.5**

### v2.2.5

- 新增 **扫码登录 / 短信登录** 两种登录方式切换；
- 修复扫码设备码请求，补充 `device_id`；
- 扫码 scope 更新为 `user profile sso offline_access`；
- 二维码使用接口返回的 `verification_uri_complete`；
- 授权成功后自动保存 `access_token` 与 `refresh_token`；
- 保留短信验证码登录作为扫码登录的备用方式。

### v2.2.4

兼容新版 MoviePilot `get_item_strict()` 存储接口，解决：

```text
'GuangYaApi' object has no attribute 'get_item_strict'
```

## 安装

MoviePilot 自定义插件源填写：

```text
https://github.com/liheng-lk/Guangyadisk
```

当前实际插件目录：

```text
plugins.v2/shukguangyadisk/
```

## 登录

### 扫码登录（推荐）

进入插件页面选择 **扫码登录**，使用光鸭云盘 App 扫描二维码并确认授权。插件会自动轮询授权结果并保存 Token。

### 短信登录

进入插件页面选择 **短信登录**，输入账号绑定手机号，获取短信验证码并完成登录。

两种登录方式登录成功后共用相同的文件管理、WebDAV、流式播放和 Token 自动刷新逻辑。

## 功能

- 扫码授权登录
- 短信验证码登录
- Token 自动刷新
- 文件浏览、上传、下载、删除、重命名、新建目录
- MoviePilot 外部存储
- `/stream` HTTP Range 流式代理
- `/browse` 目录浏览
- `/webdav` WebDAV
- Emby / Jellyfin 访问

## 维护说明

本仓库为 fork 维护版本。当前兼容修复与发布由 `liheng-lk` 维护，上游项目和历史贡献保留在 Git 历史中。

## License

MIT
