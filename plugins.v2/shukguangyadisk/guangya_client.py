"""光鸭云盘 HTTP 客户端兼容层。

保留原有文件 API，实现扫码授权与短信验证码两种登录方式。
"""

from typing import Any, Dict, Optional

from .guangya_client_legacy import GuangYaClient as _LegacyGuangYaClient


class GuangYaClient(_LegacyGuangYaClient):
    """在原客户端之上补充当前认证流程。"""

    def _account_web_headers(self) -> Dict[str, str]:
        """当前光鸭网页/扫码认证使用的基础请求头。"""
        return {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.guangyapan.com",
            "Referer": "https://www.guangyapan.com/",
            "X-Client-Id": self._client_id,
            "X-Client-Version": "0.0.1",
            "X-Device-Id": self._device_id,
        }

    @staticmethod
    def _valid_device_code_result(result: Dict[str, Any]) -> bool:
        if not isinstance(result, dict):
            return False
        data = result.get("data") if isinstance(result.get("data"), dict) else result
        return bool(data.get("device_code") and (data.get("verification_uri_complete") or data.get("verification_uri")))

    def get_device_code(self) -> Optional[Dict[str, Any]]:
        """获取光鸭 App 可识别的设备码二维码信息。

        光鸭不同网页/客户端版本出现过多种 device/code 请求体，这里按兼容顺序
        探测，避免单一 scope 或 device_id 组合变化导致二维码直接获取失败。
        """
        request_bodies = [
            {
                "client_id": self._client_id,
                "device_id": self._device_id,
                "scope": "user profile sso offline_access",
            },
            {
                "client_id": self._client_id,
            },
            {
                "client_id": self._client_id,
                "scope": "all",
            },
        ]
        last_result: Dict[str, Any] = {}
        for body in request_bodies:
            result = self._request(
                method="POST",
                url=f"{self.ACCOUNT_BASE_URL}/v1/auth/device/code",
                data=body,
                headers=self._account_web_headers(),
                need_auth=False,
                treat_http_error_as_response=True,
            ) or {}
            last_result = result if isinstance(result, dict) else {}
            if self._valid_device_code_result(last_result):
                data = last_result.get("data") if isinstance(last_result.get("data"), dict) else last_result
                return data
        return last_result or None

    def poll_device_code(self, device_code: str) -> Optional[Dict[str, Any]]:
        """轮询扫码授权状态并获取 access_token / refresh_token。"""
        body = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": self._client_id,
        }
        # 当前网页实现主要使用 /v1/auth/token；部分客户端曾使用 /v1/auth/device/token。
        endpoints = ["/v1/auth/token", "/v1/auth/device/token"]
        last_result: Dict[str, Any] = {}
        for endpoint in endpoints:
            result = self._request(
                method="POST",
                url=f"{self.ACCOUNT_BASE_URL}{endpoint}",
                data=body,
                headers=self._account_web_headers(),
                need_auth=False,
                treat_http_error_as_response=True,
            ) or {}
            if isinstance(result.get("data"), dict) and result.get("data"):
                result = result.get("data")
            last_result = result if isinstance(result, dict) else {}
            error = str(last_result.get("error") or "")
            if last_result.get("access_token"):
                self._access_token = last_result.get("access_token") or ""
                self._refresh_token = last_result.get("refresh_token") or ""
                if self._on_token_refresh:
                    try:
                        self._on_token_refresh(self._access_token, self._refresh_token)
                    except Exception:
                        pass
                return last_result
            if error in ("authorization_pending", "slow_down", ""):
                return {
                    "waiting": True,
                    "slow_down": error == "slow_down",
                    "message": "等待扫码确认..." if error != "slow_down" else "轮询过快，稍后继续...",
                }
            if error == "expired_token":
                return {"expired": True, "message": "二维码已过期，请重新获取"}
            if error == "access_denied":
                return {"denied": True, "message": "授权已取消，请重新扫码"}
        return last_result or None

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        value = str(phone or "").strip().replace(" ", "")
        if not value:
            return ""
        if value.startswith("+86"):
            return "+86 " + value[3:]
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) == 11:
            return "+86 " + digits
        return value

    def init_captcha(self, phone_number: str) -> Dict[str, Any]:
        phone = self._normalize_phone(phone_number)
        return self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/shield/captcha/init",
            data={
                "client_id": self._client_id,
                "action": "POST:/v1/auth/verification",
                "device_id": self._device_id,
                "meta": {
                    "username": phone,
                    "phone_number": phone,
                    "VERIFICATION_PHONE": phone,
                },
            },
            headers=self._account_web_headers(),
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}

    def request_sms_code(self, phone_number: str, captcha_token: str = "") -> Dict[str, Any]:
        phone = self._normalize_phone(phone_number)
        captcha = str(captcha_token or "").strip()
        if not captcha:
            captcha_result = self.init_captcha(phone)
            captcha = str(
                captcha_result.get("captcha_token")
                or captcha_result.get("captchaToken")
                or (captcha_result.get("data") or {}).get("captcha_token")
                or ""
            ).strip()
            if not captcha:
                return {
                    "success": False,
                    "error": captcha_result.get("error") or "captcha_init_failed",
                    "message": captcha_result.get("error_description") or captcha_result.get("msg") or "无法获取 captcha token",
                }

        headers = self._account_web_headers()
        headers["X-Captcha-Token"] = captcha
        result = self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/auth/verification",
            data={
                "phone_number": phone,
                "target": "ANY",
                "client_id": self._client_id,
                "device_id": self._device_id,
            },
            headers=headers,
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}
        verification_id = str(
            result.get("verification_id")
            or result.get("verificationId")
            or (result.get("data") or {}).get("verification_id")
            or ""
        ).strip()
        if not verification_id:
            return {
                "success": False,
                "error": result.get("error") or "verification_failed",
                "message": result.get("error_description") or result.get("msg") or "发送验证码失败",
                "captcha_token": captcha,
            }
        return {
            "success": True,
            "verification_id": verification_id,
            "captcha_token": captcha,
            "phone_number": phone,
        }

    def signin_by_sms(self, phone_number: str, verification_id: str, verification_code: str) -> Dict[str, Any]:
        phone = self._normalize_phone(phone_number)
        code = str(verification_code or "").strip()
        verify_result = self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/auth/verification/verify",
            data={
                "verification_id": str(verification_id or "").strip(),
                "verification_code": code,
                "client_id": self._client_id,
            },
            headers=self._account_web_headers(),
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}
        verification_token = str(
            verify_result.get("verification_token")
            or verify_result.get("verificationToken")
            or (verify_result.get("data") or {}).get("verification_token")
            or ""
        ).strip()
        if not verification_token:
            return {
                "success": False,
                "error": verify_result.get("error") or "verify_code_failed",
                "message": verify_result.get("error_description") or verify_result.get("msg") or "验证码校验失败",
            }

        result = self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/auth/signin",
            data={
                "verification_code": code,
                "verification_token": verification_token,
                "username": phone,
                "client_id": self._client_id,
            },
            headers=self._account_web_headers(),
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}
        access_token = str(result.get("access_token") or "").strip()
        if not access_token:
            return {
                "success": False,
                "error": result.get("error") or "signin_failed",
                "message": result.get("error_description") or result.get("msg") or "登录失败",
            }

        self._access_token = access_token
        self._refresh_token = str(result.get("refresh_token") or "").strip()
        if self._on_token_refresh:
            try:
                self._on_token_refresh(self._access_token, self._refresh_token)
            except Exception:
                pass
        return {
            "success": True,
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "expires_in": result.get("expires_in"),
        }


__all__ = ["GuangYaClient"]