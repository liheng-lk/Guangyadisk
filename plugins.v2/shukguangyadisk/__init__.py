"""光鸭云盘助手插件入口。

主实现保留在 _plugin_legacy.py，本入口补充当前 fork 的版本、认证能力与紧凑配置表单。
扫码登录沿用 KoWming 原实现；目录浏览、整理上传、下载、移动、复制、WebDAV 等存储能力继续沿用原实现。
"""

import time
from typing import Any, Dict, List, Optional, Tuple

from ._plugin_legacy import ShukGuangYaDisk as _LegacyPlugin


class ShukGuangYaDisk(_LegacyPlugin):
    """光鸭云盘助手。"""

    plugin_name = "光鸭云盘助手"
    plugin_desc = "MoviePilot 光鸭云盘存储助手，支持扫码/短信登录、目录浏览、整理上传、下载、移动、复制和 Emby 直连。"
    plugin_version = "2.2.15"
    plugin_author = "liheng-lk"
    author_url = "https://github.com/liheng-lk/Guangyadisk"

    _sms_verification_id: str = ""
    _sms_phone_number: str = ""
    _sms_captcha_token: str = ""

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """返回双栏紧凑配置表单。"""
        form = [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "props": {"dense": True},
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 8},
                                "content": [
                                    {
                                        "component": "VCard",
                                        "props": {"variant": "outlined", "class": "mb-3"},
                                        "content": [
                                            {
                                                "component": "VCardTitle",
                                                "props": {"class": "text-subtitle-1 font-weight-bold"},
                                                "text": "运行配置"
                                            },
                                            {
                                                "component": "VCardText",
                                                "content": [
                                                    {
                                                        "component": "VRow",
                                                        "content": [
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VSwitch",
                                                                        "props": {
                                                                            "model": "enabled",
                                                                            "label": "启用光鸭云盘助手",
                                                                            "color": "primary",
                                                                            "density": "compact",
                                                                            "hide-details": True
                                                                        }
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VSwitch",
                                                                        "props": {
                                                                            "model": "permanently_delete",
                                                                            "label": "删除时彻底删除",
                                                                            "color": "error",
                                                                            "density": "compact",
                                                                            "hide-details": True
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "component": "VRow",
                                                        "content": [
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VTextField",
                                                                        "props": {
                                                                            "model": "poll_interval",
                                                                            "label": "轮询间隔（秒）",
                                                                            "type": "number",
                                                                            "min": 2,
                                                                            "max": 30,
                                                                            "density": "compact",
                                                                            "variant": "outlined",
                                                                            "hide-details": "auto"
                                                                        }
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VSelect",
                                                                        "props": {
                                                                            "model": "page_size",
                                                                            "label": "分页大小",
                                                                            "items": [50, 100, 200, 500],
                                                                            "density": "compact",
                                                                            "variant": "outlined",
                                                                            "hide-details": "auto"
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "component": "VRow",
                                                        "content": [
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VSelect",
                                                                        "props": {
                                                                            "model": "order_by",
                                                                            "label": "排序字段",
                                                                            "items": [
                                                                                {"title": "名称", "value": 1},
                                                                                {"title": "大小", "value": 2},
                                                                                {"title": "更新时间", "value": 3}
                                                                            ],
                                                                            "density": "compact",
                                                                            "variant": "outlined",
                                                                            "hide-details": "auto"
                                                                        }
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VSelect",
                                                                        "props": {
                                                                            "model": "sort_type",
                                                                            "label": "排序方向",
                                                                            "items": [
                                                                                {"title": "升序", "value": 1},
                                                                                {"title": "降序", "value": 2}
                                                                            ],
                                                                            "density": "compact",
                                                                            "variant": "outlined",
                                                                            "hide-details": "auto"
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "component": "VCard",
                                        "props": {"variant": "outlined"},
                                        "content": [
                                            {
                                                "component": "VCardTitle",
                                                "props": {"class": "text-subtitle-1 font-weight-bold"},
                                                "text": "高级参数"
                                            },
                                            {
                                                "component": "VCardText",
                                                "content": [
                                                    {
                                                        "component": "VRow",
                                                        "content": [
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VTextField",
                                                                        "props": {
                                                                            "model": "client_id",
                                                                            "label": "Client ID",
                                                                            "density": "compact",
                                                                            "variant": "outlined",
                                                                            "readonly": True,
                                                                            "hide-details": "auto"
                                                                        }
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "component": "VCol",
                                                                "props": {"cols": 12, "sm": 6},
                                                                "content": [
                                                                    {
                                                                        "component": "VTextField",
                                                                        "props": {
                                                                            "model": "device_id",
                                                                            "label": "设备 ID",
                                                                            "density": "compact",
                                                                            "variant": "outlined",
                                                                            "readonly": True,
                                                                            "hide-details": "auto"
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VCard",
                                        "props": {"variant": "outlined", "class": "mb-3"},
                                        "content": [
                                            {
                                                "component": "VCardTitle",
                                                "props": {"class": "text-subtitle-1 font-weight-bold"},
                                                "text": "账号会话"
                                            },
                                            {
                                                "component": "VCardText",
                                                "content": [
                                                    {
                                                        "component": "VAlert",
                                                        "props": {
                                                            "type": "info",
                                                            "variant": "tonal",
                                                            "density": "compact",
                                                            "text": "扫码或短信登录请在“状态页”完成。Token 会自动保存和刷新，设置页无需手工维护。"
                                                        }
                                                    },
                                                    {
                                                        "component": "VTextField",
                                                        "props": {
                                                            "model": "access_token",
                                                            "label": "Access Token",
                                                            "type": "password",
                                                            "density": "compact",
                                                            "variant": "outlined",
                                                            "readonly": True,
                                                            "hide-details": "auto",
                                                            "class": "mt-3"
                                                        }
                                                    },
                                                    {
                                                        "component": "VTextField",
                                                        "props": {
                                                            "model": "refresh_token",
                                                            "label": "Refresh Token",
                                                            "type": "password",
                                                            "density": "compact",
                                                            "variant": "outlined",
                                                            "readonly": True,
                                                            "hide-details": "auto",
                                                            "class": "mt-3"
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "component": "VCard",
                                        "props": {"variant": "outlined"},
                                        "content": [
                                            {
                                                "component": "VCardTitle",
                                                "props": {"class": "text-subtitle-1 font-weight-bold"},
                                                "text": "使用建议"
                                            },
                                            {
                                                "component": "VCardText",
                                                "content": [
                                                    {
                                                        "component": "VAlert",
                                                        "props": {
                                                            "type": "success",
                                                            "variant": "tonal",
                                                            "density": "compact",
                                                            "text": "常规使用保持默认参数即可。轮询间隔建议 5–10 秒，分页大小建议 100；只有目录特别大时再调高分页。"
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        config = {
            "enabled": self._enabled,
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "client_id": self._client_id,
            "device_id": self._device_id,
            "poll_interval": self._poll_interval or 5,
            "page_size": self._page_size or 100,
            "order_by": self._order_by or 3,
            "sort_type": self._sort_type or 1,
            "permanently_delete": self._permanently_delete,
        }
        return form, config

    def get_api(self) -> List[Dict[str, Any]]:
        """返回插件 API。"""
        apis = list(super().get_api())
        apis.extend([
            {
                "path": "/login/sms/send",
                "endpoint": self.send_sms_code,
                "auth": "bear",
                "methods": ["POST"],
                "summary": "发送光鸭云盘短信验证码",
            },
            {
                "path": "/login/sms/verify",
                "endpoint": self.verify_sms_login,
                "auth": "bear",
                "methods": ["POST"],
                "summary": "校验短信验证码并完成光鸭云盘登录",
            },
        ])
        return apis

    def _activate_storage_after_login(self) -> None:
        """登录成功后启用并重新初始化存储适配器。"""
        self._enabled = True
        config = {
            "enabled": True,
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "client_id": self._client_id,
            "device_id": self._device_id,
            "poll_interval": self._poll_interval,
            "page_size": self._page_size,
            "order_by": self._order_by,
            "sort_type": self._sort_type,
            "permanently_delete": self._permanently_delete,
        }
        self.update_config(config)
        self.init_plugin(config)

    def send_sms_code(self, payload: dict) -> Dict[str, Any]:
        """发送短信验证码。"""
        payload = payload or {}
        phone = str(payload.get("phone_number") or payload.get("phone") or "").strip()
        if not phone:
            return {"success": False, "stage": "moviepilot", "message": "请输入手机号"}
        if not self._client:
            from .guangya_client import GuangYaClient
            self._client = GuangYaClient(
                access_token=None,
                refresh_token=None,
                client_id=self._client_id,
                device_id=self._device_id,
            )
            self._device_id = self._client.device_id
        result = self._client.request_sms_code(
            phone_number=phone,
            captcha_token=str(payload.get("captcha_token") or "").strip(),
        )
        if result.get("success"):
            self._sms_phone_number = result.get("phone_number") or phone
            self._sms_verification_id = result.get("verification_id") or ""
            self._sms_captcha_token = result.get("captcha_token") or ""
        return result

    def verify_sms_login(self, payload: dict) -> Dict[str, Any]:
        """校验短信验证码并完成登录。"""
        payload = payload or {}
        phone = str(payload.get("phone_number") or payload.get("phone") or self._sms_phone_number or "").strip()
        verification_id = str(payload.get("verification_id") or self._sms_verification_id or "").strip()
        captcha_token = str(payload.get("captcha_token") or self._sms_captcha_token or "").strip()
        code = str(payload.get("verification_code") or payload.get("verify_code") or "").strip()
        if not phone or not verification_id or not code:
            return {"success": False, "stage": "moviepilot", "message": "手机号、verification_id 和验证码不能为空"}
        if not captcha_token:
            return {"success": False, "stage": "moviepilot", "message": "captcha_token 已丢失，请重新获取短信验证码"}
        if not self._client:
            return {"success": False, "stage": "moviepilot", "message": "请先发送短信验证码"}

        result = self._client.signin_by_sms(
            phone_number=phone,
            verification_id=verification_id,
            verification_code=code,
            captcha_token=captcha_token,
        )
        if not result.get("success"):
            return result

        self._access_token = result.get("access_token") or ""
        self._refresh_token = result.get("refresh_token") or ""
        self._activate_storage_after_login()

        self._sms_verification_id = ""
        self._sms_phone_number = ""
        self._sms_captcha_token = ""
        return {
            "success": True,
            "message": "短信登录成功，光鸭云盘存储已启用",
            "device_id": self._device_id,
            "enabled": True,
        }

    def poll_login(self) -> Dict[str, Any]:
        """轮询扫码登录状态并保存 Token。"""
        if not self._device_code:
            return {"success": False, "message": "请先获取二维码", "waiting": False, "stage": "missing_device_code"}
        if self._qr_expires_at and time.time() > self._qr_expires_at:
            return {"success": False, "message": "二维码已过期，请重新获取", "waiting": False, "stage": "expired"}

        from .guangya_client import GuangYaClient
        temp_client = GuangYaClient(
            access_token=None,
            refresh_token=None,
            client_id=self._client_id,
            device_id=self._device_id,
        )
        result = temp_client.poll_device_code(self._device_code)

        if result and result.get("waiting"):
            return {
                "success": False,
                "message": result.get("message") or "等待扫码确认...",
                "waiting": True,
                "stage": "authorization_pending",
            }
        if not result or not result.get("access_token"):
            return {
                "success": False,
                "message": "已扫码，等待光鸭返回登录令牌...",
                "waiting": True,
                "stage": "token_pending",
            }

        self._access_token = str(result.get("access_token") or "").strip()
        self._refresh_token = str(result.get("refresh_token") or "").strip()
        if not self._access_token:
            return {"success": False, "message": "光鸭未返回 access_token", "waiting": False, "stage": "missing_access_token"}

        self._activate_storage_after_login()
        self._device_code = ""
        self._user_code = ""
        self._verification_uri = ""
        self._qr_expires_at = 0

        return {
            "success": True,
            "message": "扫码登录成功，登录信息已保存",
            "device_id": self._device_id,
            "enabled": True,
            "has_access_token": bool(self._access_token),
            "has_refresh_token": bool(self._refresh_token),
        }


__all__ = ["ShukGuangYaDisk"]
