"""Shuk-光鸭云盘插件入口。

主实现保留在 _plugin_legacy.py，本入口负责当前 fork 的版本、维护者元数据与新版登录 API。
"""

from typing import Any, Dict, List

from ._plugin_legacy import ShukGuangYaDisk as _LegacyPlugin


class ShukGuangYaDisk(_LegacyPlugin):
    plugin_version = "2.2.6"
    plugin_author = "liheng-lk"
    author_url = "https://github.com/liheng-lk/Guangyadisk"

    _sms_verification_id: str = ""
    _sms_phone_number: str = ""
    _sms_captcha_token: str = ""

    def get_api(self) -> List[Dict[str, Any]]:
        apis = list(super().get_api())
        apis.extend(
            [
                {
                    "path": "/login/sms/send",
                    "endpoint": self.send_sms_code,
                    "auth": "bear",
                    "methods": ["POST"],
                    "summary": "发送光鸭云盘短信验证码（当前登录流程）",
                },
                {
                    "path": "/login/sms/verify",
                    "endpoint": self.verify_sms_login,
                    "auth": "bear",
                    "methods": ["POST"],
                    "summary": "校验短信验证码并完成光鸭云盘登录",
                },
            ]
        )
        return apis

    def send_sms_code(self, payload: dict) -> Dict[str, Any]:
        payload = payload or {}
        phone = str(payload.get("phone_number") or payload.get("phone") or "").strip()
        if not phone:
            return {"success": False, "message": "请输入手机号"}
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
        code = str(payload.get("verification_code") or payload.get("verify_code") or "").strip()
        if not phone or not verification_id or not code:
            return {"success": False, "message": "手机号、verification_id 和验证码不能为空"}
        if not self._client:
            return {"success": False, "message": "请先发送短信验证码"}
        result = self._client.signin_by_sms(phone, verification_id, code)
        if not result.get("success"):
            return result

        self._access_token = result.get("access_token") or ""
        self._refresh_token = result.get("refresh_token") or ""
        new_config = {
            "enabled": self._enabled,
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
        self.update_config(new_config)
        self.init_plugin(new_config)
        self._sms_verification_id = ""
        return {"success": True, "message": "短信登录成功", "device_id": self._device_id}


__all__ = ["ShukGuangYaDisk"]
