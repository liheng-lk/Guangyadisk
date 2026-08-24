const CHANNEL_LIST = [
  { name: "光鸭云盘资源分享频道", id: "yunpanguangya" },
  { name: "光鸭云盘影视热更频道", id: "regengguangya" },
  { name: "115网盘影视热更频道", id: "regeng115" },
  { name: "123云盘影视热更频道", id: "regeng123" },
  { name: "123云盘资源频道", id: "tuoxiede123" },
  { name: "123Pan分享频道", id: "x123panfxme" },
  { name: "123 Share", id: "wei_123share" },
  { name: "123 Share 2", id: "wei_123_share" },
  { name: "Qukan Movie", id: "QukanMovie" },
  { name: "光鸭 HDHive", id: "guangya_hdhive" },
  { name: "光鸭云盘资源频道", id: "pan_guangya" },
];

const CHANNEL_MAP = new Map(
  CHANNEL_LIST.map((item) => [item.id.toLowerCase(), item.id])
);

const TELEGRAM_HOSTS = [
  "t.me",
  "telegram.me",
  "telegram.org",
  "telesco.pe",
  "telegram-cdn.org",
  "cdn-telegram.org",
];

const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
  "AppleWebKit/537.36 (KHTML, like Gecko) " +
  "Chrome/151.0.0.0 Safari/537.36";

function resolveChannel(name) {
  if (!name) return null;
  return CHANNEL_MAP.get(name.toLowerCase()) || null;
}

function isTelegramHost(hostname) {
  hostname = hostname.toLowerCase();
  return TELEGRAM_HOSTS.some(
    (host) => hostname === host || hostname.endsWith("." + host)
  );
}

function getChannelFromTelegramUrl(url) {
  try {
    const u = new URL(url);
    if (
      u.hostname !== "t.me" &&
      u.hostname !== "www.t.me" &&
      u.hostname !== "telegram.me"
    ) {
      return null;
    }

    const parts = u.pathname.split("/").filter(Boolean);
    let channel;
    let rest = [];

    if (parts[0] === "s") {
      channel = parts[1];
      rest = parts.slice(2);
    } else {
      channel = parts[0];
      rest = parts.slice(1);
    }

    const canonical = resolveChannel(channel);
    if (!canonical) return null;

    return {
      channel: canonical,
      rest,
      search: u.search,
      hash: u.hash,
    };
  } catch {
    return null;
  }
}

function localChannelUrl(url, origin) {
  const parsed = getChannelFromTelegramUrl(url);
  if (!parsed) return null;

  let path = `/${parsed.channel}`;
  if (parsed.rest.length) path += "/" + parsed.rest.join("/");

  return origin + path + parsed.search + parsed.hash;
}

function makeAssetProxyUrl(url, base, origin) {
  try {
    const absolute = new URL(url, base);

    if (
      absolute.protocol !== "http:" &&
      absolute.protocol !== "https:"
    ) {
      return url;
    }

    if (!isTelegramHost(absolute.hostname)) return url;

    return (
      origin +
      "/__tgproxy?url=" +
      encodeURIComponent(absolute.href)
    );
  } catch {
    return url;
  }
}

function rewriteStyle(style, base, origin) {
  if (!style) return style;

  return style.replace(
    /url\(\s*(['"]?)(.*?)\1\s*\)/gi,
    (match, quote, rawUrl) => {
      if (rawUrl.startsWith("data:") || rawUrl.startsWith("blob:")) {
        return match;
      }
      return `url("${makeAssetProxyUrl(rawUrl, base, origin)}")`;
    }
  );
}

function rewriteSrcset(srcset, base, origin) {
  if (!srcset) return srcset;

  return srcset
    .split(",")
    .map((entry) => {
      const parts = entry.trim().split(/\s+/);
      if (!parts[0]) return entry;
      parts[0] = makeAssetProxyUrl(parts[0], base, origin);
      return parts.join(" ");
    })
    .join(", ");
}

class AssetAttributeRewriter {
  constructor(attribute, base, origin) {
    this.attribute = attribute;
    this.base = base;
    this.origin = origin;
  }

  element(element) {
    const value = element.getAttribute(this.attribute);
    if (!value) return;

    element.setAttribute(
      this.attribute,
      makeAssetProxyUrl(value, this.base, this.origin)
    );
  }
}

class LinkRewriter {
  constructor(base, origin) {
    this.base = base;
    this.origin = origin;
  }

  element(element) {
    const href = element.getAttribute("href");
    if (!href) return;

    try {
      const absolute = new URL(href, this.base);
      const local = localChannelUrl(absolute.href, this.origin);

      if (local) {
        element.setAttribute("href", local);
        return;
      }

      element.setAttribute("href", absolute.href);
    } catch {
      // Leave malformed/relative links untouched.
    }
  }
}

class StyleRewriter {
  constructor(base, origin) {
    this.base = base;
    this.origin = origin;
  }

  element(element) {
    const style = element.getAttribute("style");
    if (!style) return;

    element.setAttribute(
      "style",
      rewriteStyle(style, this.base, this.origin)
    );
  }
}

class SrcsetRewriter {
  constructor(base, origin) {
    this.base = base;
    this.origin = origin;
  }

  element(element) {
    const srcset = element.getAttribute("srcset");
    if (!srcset) return;

    element.setAttribute(
      "srcset",
      rewriteSrcset(srcset, this.base, this.origin)
    );
  }
}

async function fetchTelegram(target, request) {
  const headers = new Headers();

  headers.set("User-Agent", USER_AGENT);
  headers.set("Accept", request.headers.get("Accept") || "*/*");
  headers.set("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8");
  headers.set("Referer", "https://t.me/");

  const range = request.headers.get("Range");
  if (range) headers.set("Range", range);

  return fetch(target, {
    method: request.method === "HEAD" ? "HEAD" : "GET",
    headers,
    redirect: "follow",
  });
}

async function proxyAsset(request, incoming) {
  const target = incoming.searchParams.get("url");
  if (!target) return new Response("Missing URL", { status: 400 });

  let targetUrl;
  try {
    targetUrl = new URL(target);
  } catch {
    return new Response("Invalid URL", { status: 400 });
  }

  if (!isTelegramHost(targetUrl.hostname)) {
    return new Response("Forbidden", { status: 403 });
  }

  const upstream = await fetchTelegram(targetUrl.href, request);
  const contentType = upstream.headers.get("content-type") || "";
  const headers = new Headers(upstream.headers);

  headers.delete("content-security-policy");
  headers.delete("content-security-policy-report-only");
  headers.delete("x-frame-options");
  headers.delete("content-length");
  headers.set("cache-control", "public, max-age=3600");

  if (contentType.includes("text/css")) {
    let css = await upstream.text();

    css = css.replace(
      /url\(\s*(['"]?)(.*?)\1\s*\)/gi,
      (match, quote, rawUrl) => {
        if (rawUrl.startsWith("data:") || rawUrl.startsWith("blob:")) {
          return match;
        }
        return `url("${makeAssetProxyUrl(
          rawUrl,
          targetUrl.href,
          incoming.origin
        )}")`;
      }
    );

    css = css.replace(
      /@import\s+(['"])(.*?)\1/gi,
      (match, quote, rawUrl) =>
        '@import "' +
        makeAssetProxyUrl(rawUrl, targetUrl.href, incoming.origin) +
        '"'
    );

    headers.set("content-type", "text/css; charset=UTF-8");
    return new Response(css, { status: upstream.status, headers });
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers,
  });
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function homepage() {
  const channelHtml = CHANNEL_LIST.map(
    (item) => `
      <a class="channel" href="/${encodeURIComponent(item.id)}">
        <div class="name">${escapeHtml(item.name)}</div>
        <div class="username">@${escapeHtml(item.id)}</div>
      </a>`
  ).join("");

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Telegram 频道镜像</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: #f4f5f7;
      color: #111827;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    }
    main { max-width: 680px; margin: 50px auto; padding: 20px; }
    h1 { margin: 0 0 8px; font-size: 28px; }
    .subtitle { margin: 0 0 26px; color: #6b7280; font-size: 14px; }
    .channel {
      display: block;
      background: white;
      padding: 18px 20px;
      margin-top: 12px;
      border-radius: 14px;
      text-decoration: none;
      color: #111827;
      border: 1px solid rgba(0,0,0,.06);
      box-shadow: 0 2px 10px rgba(0,0,0,.05);
      transition: transform .15s ease, box-shadow .15s ease;
    }
    .channel:hover {
      transform: translateY(-1px);
      box-shadow: 0 5px 18px rgba(0,0,0,.08);
    }
    .name { font-size: 16px; font-weight: 600; }
    .username { margin-top: 5px; color: #6b7280; font-size: 13px; }
  </style>
</head>
<body>
  <main>
    <h1>Telegram 频道镜像</h1>
    <p class="subtitle">公开频道快速访问</p>
    ${channelHtml}
  </main>
</body>
</html>`;
}

export default {
  async fetch(request) {
    const incoming = new URL(request.url);

    if (incoming.pathname === "/__tgproxy") {
      return proxyAsset(request, incoming);
    }

    if (incoming.pathname === "/channels.json") {
      return Response.json(CHANNEL_LIST, {
        headers: { "cache-control": "public, max-age=300" },
      });
    }

    if (incoming.pathname === "/" || incoming.pathname === "") {
      return new Response(homepage(), {
        headers: {
          "content-type": "text/html; charset=UTF-8",
          "cache-control": "public, max-age=300",
        },
      });
    }

    const parts = incoming.pathname.split("/").filter(Boolean);
    const channel = resolveChannel(parts[0]);

    if (!channel) {
      return new Response("404 - Channel not allowed", { status: 404 });
    }

    let telegramPath = `/s/${channel}`;
    if (parts.length > 1) {
      telegramPath += "/" + parts.slice(1).join("/");
    }

    const telegramUrl = new URL("https://t.me" + telegramPath);
    incoming.searchParams.forEach((value, key) => {
      telegramUrl.searchParams.append(key, value);
    });

    const upstream = await fetchTelegram(telegramUrl.href, request);

    if (!upstream.ok) {
      return new Response(`Telegram upstream error: ${upstream.status}`, {
        status: upstream.status,
      });
    }

    const headers = new Headers(upstream.headers);
    headers.delete("content-security-policy");
    headers.delete("content-security-policy-report-only");
    headers.delete("x-frame-options");
    headers.delete("content-length");
    headers.delete("content-encoding");
    headers.set("cache-control", "public, max-age=60");

    const base = telegramUrl.href;
    const origin = incoming.origin;

    return new HTMLRewriter()
      .on("a[href]", new LinkRewriter(base, origin))
      .on("img[src]", new AssetAttributeRewriter("src", base, origin))
      .on("video[src]", new AssetAttributeRewriter("src", base, origin))
      .on("source[src]", new AssetAttributeRewriter("src", base, origin))
      .on("script[src]", new AssetAttributeRewriter("src", base, origin))
      .on("link[href]", new AssetAttributeRewriter("href", base, origin))
      .on("iframe[src]", new AssetAttributeRewriter("src", base, origin))
      .on("[srcset]", new SrcsetRewriter(base, origin))
      .on("[style]", new StyleRewriter(base, origin))
      .transform(
        new Response(upstream.body, {
          status: upstream.status,
          headers,
        })
      );
  },
};
