"""光鸭云盘助手插件入口。

主实现保留在 _plugin_legacy.py，本入口补充当前 fork 的版本与短信认证能力。
扫码登录沿用 KoWming 原实现；目录浏览、整理上传、下载、移动、复制、WebDAV 等存储能力继续沿用原实现。
"""

import time
from typing import Any, Dict, List

from ._plugin_legacy import ShukGuangYaDisk as _LegacyPlugin


class ShukGuangYaDisk(_LegacyPlugin):
    plugin_name = "光鸭云盘助手"
    plugin_desc = "MoviePilot 光鸭云盘存储助手，支持扫码/短信登录、目录浏览、整理上传、下载、移动、复制和 Emby 直连。"
    plugin_version = "2.2.14"
    plugin_author = "liheng-lk"
    author_url = "https://github.com/liheng-lk/Guangyadisk"

    _sms_verification_id: str = ""
    _sms_phone_number: str = ""
    _sms_captcha_token: str = ""

    def get_api(self) -> List[Dict[str, Any]]:
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
