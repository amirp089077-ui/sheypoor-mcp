"""
Authentication client for Sheypoor MCP.
Handles phone OTP login, verification, and xTicket storage.
"""

import os
import json
import requests
from typing import Dict, Any, Optional

TOKEN_FILE = os.path.expanduser("~/.sheypoor_mcp_auth.json")
BASE_URL = "https://www.sheypoor.com/api/v7.0.7"

DEFAULT_HEADERS = {
    "User-Agent": "Sheypoor/7.0.7 (Android; Mobile; fa)",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-AGENT-TYPE": "Android App",
    "X-BUILD-MODE": "Release",
    "X-FLAVOR": "direct",
}


class SheypoorAuth:
    def __init__(self, token_file: str = TOKEN_FILE):
        self.token_file = token_file
        self._token: Optional[str] = None
        self._phone: Optional[str] = None
        self._user_id: Optional[int] = None
        self.load()

    def load(self):
        """Loads saved token from disk."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._token = data.get("xTicket") or data.get("token")
                    self._phone = data.get("phone")
                    self._user_id = data.get("userId")
            except Exception:
                pass

    def save(self):
        """Saves active auth state to disk."""
        data = {
            "xTicket": self._token,
            "phone": self._phone,
            "userId": self._user_id,
        }
        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @property
    def token(self) -> Optional[str]:
        return self._token

    def send_otp(self, phone: str) -> Dict[str, Any]:
        """
        Sends an OTP SMS code to the given mobile number.
        """
        phone = phone.strip()
        url = f"{BASE_URL}/auth/state-request"
        payload = {"username": phone}
        
        try:
            r = requests.post(url, json=payload, headers=DEFAULT_HEADERS, timeout=12)
            data = r.json()
            if r.status_code == 200:
                self._phone = phone
                return {
                    "success": True,
                    "token": data.get("token"),
                    "message": data.get("message") or "کد تایید ارسال شد",
                    "userState": data.get("userState"),
                    "isNewUser": data.get("isNewUser", False),
                }
            else:
                err = data.get("error", {}).get("errorMessage") if isinstance(data, dict) else r.text
                return {"success": False, "error": err or f"HTTP {r.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_otp(self, token: str, pin: str) -> Dict[str, Any]:
        """
        Verifies the received OTP code and obtains the xTicket authentication token.
        """
        url = f"{BASE_URL}/auth/number-verification"
        payload = {"token": token, "pin": pin}

        try:
            r = requests.post(url, json=payload, headers=DEFAULT_HEADERS, timeout=12)
            data = r.json()
            if r.status_code == 200:
                x_ticket = data.get("xTicket")
                user_id = data.get("userId")
                phone = data.get("mobileNumber") or self._phone
                
                self._token = x_ticket
                self._user_id = user_id
                self._phone = phone
                self.save()

                return {
                    "success": True,
                    "xTicket": x_ticket,
                    "userId": user_id,
                    "phone": phone,
                    "message": "ورود به حساب کاربری با موفقیت انجام شد",
                }
            else:
                err = data.get("error", {}).get("errorMessage") if isinstance(data, dict) else r.text
                return {"success": False, "error": err or f"HTTP {r.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_token(self, token: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Manually sets the auth token."""
        self._token = token.strip()
        if phone:
            self._phone = phone
        self.save()
        return {"success": True, "message": "توکن با موفقیت تنظیم شد"}

    def logout(self) -> Dict[str, Any]:
        """Logs out and deletes stored credentials."""
        self._token = None
        self._phone = None
        self._user_id = None
        if os.path.exists(self.token_file):
            try:
                os.remove(self.token_file)
            except Exception:
                pass
        return {"success": True, "message": "از حساب کاربری خارج شدید"}

    def get_status(self) -> Dict[str, Any]:
        """Checks authentication validity against Sheypoor API."""
        if not self._token:
            return {"authenticated": False, "message": "وارد حساب کاربری نشده‌اید"}

        headers = {**DEFAULT_HEADERS, "x-ticket": self._token}
        try:
            r = requests.get(f"{BASE_URL}/user/profile", headers=headers, timeout=10)
            if r.status_code == 200:
                profile = r.json()
                return {
                    "authenticated": True,
                    "phone": self._phone or profile.get("mobileNumber"),
                    "userId": self._user_id or profile.get("userId"),
                    "profile": profile,
                }
            else:
                return {
                    "authenticated": False,
                    "error": f"توکن منقضی یا نامعتبر است (کد {r.status_code})",
                }
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
