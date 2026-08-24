# Telegram 公开频道镜像

基于 Cloudflare Workers 的 Telegram 公开频道网页镜像，用于将 `https://t.me/s/<channel>` 的公开 Web Preview 通过自定义域名访问。

当前部署域名示例：

```text
https://tgm.li668.asia/
```

## 当前频道

- `yunpanguangya` - 光鸭云盘资源分享频道
- `regengguangya` - 光鸭云盘影视热更频道
- `regeng115` - 115网盘影视热更频道
- `regeng123` - 123云盘影视热更频道
- `tuoxiede123` - 123云盘资源频道
- `x123panfxme` - 123Pan分享频道
- `wei_123share` - 123 Share
- `wei_123_share` - 123 Share 2
- `QukanMovie` - Qukan Movie
- `guangya_hdhive` - 光鸭 HDHive
- `pan_guangya` - 光鸭云盘资源频道

频道导入 JSON：`channels.json`

Worker 同时提供：

```text
/channels.json
```

用于直接返回当前频道列表。

## 部署到 Cloudflare Workers

1. 登录 Cloudflare Dashboard。
2. 打开 Workers & Pages。
3. 创建一个 Worker。
4. 将 `worker.js` 全部复制到 Worker 编辑器中。
5. 点击 Deploy。
6. 在 Worker 的 Domains / Custom Domains 中绑定自己的子域名，例如：

```text
tgm.example.com
```

7. 访问：

```text
https://tgm.example.com/yunpanguangya
```

## 新增频道

只需要修改 `worker.js` 顶部的 `CHANNEL_LIST`：

```javascript
const CHANNEL_LIST = [
  { name: "频道名称", id: "telegram_channel_id" },
];
```

例如新增：

```text
https://t.me/example_channel
```

加入：

```javascript
{ name: "示例频道", id: "example_channel" },
```

重新部署后即可访问：

```text
https://你的镜像域名/example_channel
```

同时建议同步更新仓库中的 `channels.json`。

## 工作方式

Worker 会：

- 请求 Telegram 公开频道 Web Preview；
- 保留 Telegram 原网页布局；
- 使用 `HTMLRewriter` 流式改写页面；
- 将 Telegram 自身图片、CSS、JS、背景图等资源通过 `/__tgproxy` 中转；
- 保留第三方网盘和外部网站原始链接；
- 支持频道内部消息链接和 `?before=` 历史翻页参数；
- 对 Telegram 静态资源设置缓存，提高二次访问速度。

## 限制

该方案只适用于 Telegram 本身通过公开 Web Preview 暴露的内容。

普通公开群组如果 Telegram 网页只显示 `VIEW IN TELEGRAM` 落地页，而不公开群消息正文，则 Worker 无法通过纯网页反代获取完整聊天记录。例如群组页指向资源频道时，应优先镜像对应广播频道。

私有频道、私有邀请链接、仅登录可见内容、Telegram 客户端专属功能不在本方案范围内。

## 安全

`/__tgproxy` 仅允许 Telegram 相关域名，避免 Worker 变成任意网址开放代理。
