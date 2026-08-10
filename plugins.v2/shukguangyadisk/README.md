# 光鸭云盘助手

MoviePilot 光鸭云盘存储插件，由 **liheng-lk** 维护。

当前仓库：`https://github.com/liheng-lk/Guangyadisk`

当前版本：**2.2.16**

## 功能

- 光鸭云盘 App 扫码登录
- 手机号短信验证码登录
- Token 自动保存与刷新
- MoviePilot 外部存储挂载
- 目录浏览、整理上传、下载、移动、复制、删除、重命名、新建目录
- 可开关的上传进度监控
- OSS 可续传上传与临时网络/DNS异常重试
- 上传后同名/同大小文件确认兜底
- `/stream` HTTP Range 流式代理
- `/browse` 目录浏览 API
- `/webdav` WebDAV
- Vue Federation 插件主页与独立配置页
- PC / 平板 / 手机响应式 UI

## 安装

MoviePilot 自定义插件源：

```text
https://github.com/liheng-lk/Guangyadisk
```

刷新插件市场后搜索：

```text
光鸭云盘助手
```

插件目录仍为：

```text
plugins.v2/shukguangyadisk/
```

该目录名及 `ShukGuangYaDisk` 作为 MoviePilot 内部兼容标识保留，以避免历史安装、配置和 API 路由失效；用户可见名称统一为“光鸭云盘助手”。

## 登录

### 扫码登录

打开插件主页，选择“扫码登录”，使用光鸭云盘 App 扫描二维码并确认授权。插件会自动轮询授权结果并保存 Access Token / Refresh Token。

### 短信登录

切换到“短信登录”，输入绑定手机号并获取验证码，验证成功后自动保存 Token 并启用存储。

## 上传监控

设置页可以开启“上传进度监控”。开启后在 MoviePilot 系统日志搜索：

```text
光鸭云盘助手
```

上传日志：

```text
【光鸭云盘助手】【上传】
```

网络重试日志：

```text
【光鸭云盘助手】【网络】
```

## 维护者

**liheng-lk**

项目地址：`https://github.com/liheng-lk/Guangyadisk`

## 致谢与参考

本项目的历史代码和后续兼容开发参考了多个开源项目，感谢相关作者及贡献者：

- ShukeBta / Guangyadisk：原始存储插件与历史代码基础；
- KoWming / MoviePilot-Plugins：扫码设备码与 Token 轮询流程参考；
- DDSRem-Dev / guangyaclient：短信认证流程参考；
- jxxghp / MoviePilot-Plugins：MoviePilot 插件与 Vue Federation 开发方式参考。

原项目和参考项目的必要版权与许可证声明继续保留。

## License

MIT License。详见仓库根目录 `LICENSE`。
