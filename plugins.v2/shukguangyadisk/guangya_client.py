"""光鸭云盘 HTTP 客户端兼容层。

文件 API 继续复用原实现；认证流程参考 DDSRem-Dev/guangyaclient 当前实现，
提供扫码授权与手机号短信验证码登录。
"""

from secrets import token_hex
from typing import Any, Dict, Optional

from .guangya_client_legacy import GuangYaClient as _LegacyGuangYaClient


class GuangYaClient(_LegacyGuangYaClient):
    """在原客户端之上补充当前认证流程。"""

    def _account_web_headers(self) -> Dict[str, str]:
        """构造与当前光鸭 Web 账号认证一致的请求头。"""
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": "https://www.guangyapan.com",
            "Referer": "https://www.guangyapan.com/",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/147.0.0.0 Safari/537.36"
            ),
            "X-Client-Id": self._client_id,
            "X-Client-Version": "0.0.1",
            "X-Device-Id": self._device_id,
            "X-Device-Model": "chrome%2F147.0.0.0",
            "X-Device-Name": "PC-Chrome",
            "X-Device-Sign": f"wdi10.{self._device_id}{token_hex(16)}",
            "X-Net-Work-Type": "NONE",
            "X-OS-Version": "MacIntel",
            "X-Platform-Version": "1",
            "X-Protocol-Version": "301",
            "X-Provider-Name": "NONE",
            "X-SDK-Version": "9.0.2",
        }

    @staticmethod
    def _valid_device_code_result(result: Dict[str, Any]) -> bool:
        if not isinstance(result, dict):
            return False
        data = result.get("data") if isinstance(result.get("data"), dict) else result
        return bool(
            data.get("device_code")
            and (data.get("verification_uri_complete") or data.get("verification_uri"))
        )

    def get_device_code(self) -> Optional[Dict[str, Any]]:
        """获取扫码授权设备码。

        扫码接口并不属于 guangyaclient 的短信登录实现，因此保留兼容探测逻辑。
        """
        request_bodies = [
            {
                "client_id": self._client_id,
                "device_id": self._device_id,
                "scope": "user profile sso offline_access",
            },
            {"client_id": self._client_id},
            {"client_id": self._client_id, "scope": "all"},
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
                data = (
                    last_result.get("data")
                    if isinstance(last_result.get("data"), dict)
                    else last_result
                )
                return data
        return last_result or None

    def poll_device_code(self, device_code: str) -> Optional[Dict[str, Any]]:
        """轮询扫码授权状态并获取 access_token / refresh_token。"""
        body = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": self._client_id,
        }
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
        """按 guangyaclient 示例规范化大陆手机号为 '+86 138...'。"""
        value = str(phone or "").strip()
        if not value:
            return ""
        compact = value.replace(" ", "")
        if compact.startswith("+86"):
            return "+86 " + compact[3:]
        digits = "".join(ch for ch in compact if ch.isdigit())
        if len(digits) == 11:
            return "+86 " + digits
        return value

    def login_sms_init(self, phone_number: str, captcha_token: Optional[str] = None) -> Dict[str, Any]:
        """短信登录步骤 1：初始化 captcha。"""
        phone = self._normalize_phone(phone_number)
        body: Dict[str, Any] = {
            "client_id": self._client_id,
            "action": "POST:/v1/auth/verification",
            "device_id": self._device_id,
            "meta": {"phone_number": phone},
        }
        if captcha_token:
            body["captcha_token"] = captcha_token
        return self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/shield/captcha/init",
            data=body,
            headers=self._account_web_headers(),
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}

    def login_sms_send(
        self,
        phone_number: str,
        captcha_token: str,
        target: str = "ANY",
    ) -> Dict[str, Any]:
        """短信登录步骤 2：发送短信验证码。"""
        phone = self._normalize_phone(phone_number)
        headers = self._account_web_headers()
        headers["X-Captcha-Token"] = captcha_token
        return self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/auth/verification",
            data={
                "phone_number": phone,
                "target": target,
                "client_id": self._client_id,
            },
            headers=headers,
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}

    def login_sms_verify(self, verification_id: str, verification_code: str) -> Dict[str, Any]:
        """短信登录步骤 3：验证短信验证码。"""
        return self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/auth/verification/verify",
            data={
                "verification_id": str(verification_id or "").strip(),
                "verification_code": str(verification_code or "").strip(),
                "client_id": self._client_id,
            },
            headers=self._account_web_headers(),
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}

    def login_sms_signin(
        self,
        verification_code: str,
        verification_token: str,
        username: str,
        captcha_token: str,
    ) -> Dict[str, Any]:
        """短信登录步骤 4：完成登录并取得 access/refresh token。"""
        phone = self._normalize_phone(username)
        headers = self._account_web_headers()
        headers["X-Captcha-Token"] = captcha_token
        result = self._request(
            method="POST",
            url=f"{self.ACCOUNT_BASE_URL}/v1/auth/signin",
            data={
                "verification_code": str(verification_code or "").strip(),
                "verification_token": str(verification_token or "").strip(),
                "username": phone,
                "client_id": self._client_id,
            },
            headers=headers,
            need_auth=False,
            treat_http_error_as_response=True,
        ) or {}
        access_token = str(result.get("access_token") or "").strip()
        if access_token:
            self._access_token = access_token
            self._refresh_token = str(result.get("refresh_token") or "").strip()
            if self._on_token_refresh:
                try:
                    self._on_token_refresh(self._access_token, self._refresh_token)
                except Exception:
                    pass
        return result

    def request_sms_code(self, phone_number: str, captcha_token: str = "") -> Dict[str, Any]:
        """面向 MoviePilot 的两阶段短信登录：先初始化 captcha，再发送验证码。"""
        phone = self._normalize_phone(phone_number)
        captcha = str(captcha_token or "").strip()
        if not captcha:
            init_result = self.login_sms_init(phone)
            captcha = str(
                init_result.get("captcha_token")
                or init_result.get("captchaToken")
                or (init_result.get("data") or {}).get("captcha_token")
                or ""
            ).strip()
            if not captcha:
                return {
                    "success": False,
                    "stage": "captcha_init",
                    "upstream": f"{self.ACCOUNT_BASE_URL}/v1/shield/captcha/init",
                    "error": init_result.get("error") or "captcha_init_failed",
                    "message": init_result.get("error_description")
                    or init_result.get("msg")
                    or init_result.get("error")
                    or "无法获取 captcha token",
                    "raw": init_result,
                }

        send_result = self.login_sms_send(phone, captcha)
        verification_id = str(
            send_result.get("verification_id")
            or send_result.get("verificationId")
            or (send_result.get("data") or {}).get("verification_id")
            or ""
        ).strip()
        if not verification_id:
            return {
                "success": False,
                "stage": "verification_send",
                "upstream": f"{self.ACCOUNT_BASE_URL}/v1/auth/verification",
                "error": send_result.get("error") or "verification_failed",
                "message": send_result.get("error_description")
                or send_result.get("msg")
                or send_result.get("error")
                or "发送验证码失败",
                "captcha_token": captcha,
                "raw": send_result,
            }
        return {
            "success": True,
            "verification_id": verification_id,
            "captcha_token": captcha,
            "phone_number": phone,
        }

    def signin_by_sms(
        self,
        phone_number: str,
        verification_id: str,
        verification_code: str,
        captcha_token: str,
    ) -> Dict[str, Any]:
        """面向 MoviePilot 的短信登录完成步骤。"""
        phone = self._normalize_phone(phone_number)
        code = str(verification_code or "").strip()
        verify_result = self.login_sms_verify(verification_id, code)
        verification_token = str(
            verify_result.get("verification_token")
            or verify_result.get("verificationToken")
            or (verify_result.get("data") or {}).get("verification_token")
            or ""
        ).strip()
        if not verification_token:
            return {
                "success": False,
                "stage": "verification_verify",
                "upstream": f"{self.ACCOUNT_BASE_URL}/v1/auth/verification/verify",
                "error": verify_result.get("error") or "verify_code_failed",
                "message": verify_result.get("error_description")
                or verify_result.get("msg")
                or verify_result.get("error")
                or "验证码校验失败",
                "raw": verify_result,
            }

        result = self.login_sms_signin(
            verification_code=code,
            verification_token=verification_token,
            username=phone,
            captcha_token=captcha_token,
        )
        access_token = str(result.get("access_token") or "").strip()
        if not access_token:
            return {
                "success": False,
                "stage": "signin",
                "upstream": f"{self.ACCOUNT_BASE_URL}/v1/auth/signin",
                "error": result.get("error") or "signin_failed",
                "message": result.get("error_description")
                or result.get("msg")
                or result.get("error")
                or "登录失败",
                "raw": result,
            }

        return {
            "success": True,
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "expires_in": result.get("expires_in"),
        }


__all__ = ["GuangYaClient"]
