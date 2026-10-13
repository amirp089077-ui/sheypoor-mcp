"""
Core API client for Sheypoor platform reverse-engineered from Android APK v7.0.7.
"""

import requests
from typing import Dict, Any, Optional, List, Union
from .resolve import resolve_city, resolve_category
from .normalize import normalize_listing, parse_price
from .auth_client import SheypoorAuth

BASE_URL = "https://www.sheypoor.com/api/v7.0.7"

DEFAULT_HEADERS = {
    "User-Agent": "Sheypoor/7.0.7 (Android; Mobile; fa)",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-AGENT-TYPE": "Android App",
    "X-BUILD-MODE": "Release",
    "X-FLAVOR": "direct",
}


class SheypoorClient:
    def __init__(self, auth: Optional[SheypoorAuth] = None):
        self.auth = auth or SheypoorAuth()
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _get_headers(self, authenticated: bool = False) -> Dict[str, str]:
        headers = dict(DEFAULT_HEADERS)
        if authenticated or self.auth.token:
            token = self.auth.token
            if token:
                headers["x-ticket"] = token
                headers["Cookie"] = f"xTicket={token}"
        return headers

    def search(
        self,
        query: Optional[str] = None,
        cities: Optional[Union[str, List[str]]] = None,
        category: Optional[str] = None,
        page: int = 1,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Searches listings across Sheypoor with multi-city support, filters, and pagination.
        """
        params = []
        if query:
            params.append(("q", query.strip()))
        if page and page > 1:
            params.append(("p", str(page)))

        # Handle cities
        if cities:
            if isinstance(cities, str):
                # Could be comma-separated or single
                city_list = [c.strip() for c in cities.split(",") if c.strip()]
            else:
                city_list = cities

            for c in city_list:
                info = resolve_city(c)
                if info and info.get("id"):
                    params.append(("cities[]", str(info["id"])))

        # Handle category
        if category:
            cat_id = resolve_category(category)
            if cat_id:
                params.append(("c", str(cat_id)))

        if min_price:
            params.append(("pr[from]", str(min_price)))
        if max_price:
            params.append(("pr[to]", str(max_price)))

        url = f"{BASE_URL}/listings"
        try:
            r = self.session.get(url, params=params, headers=self._get_headers(), timeout=15)
            data = r.json()
            
            raw_listings = []
            for block in data.get("data", []):
                if block.get("type") == "serp":
                    sub = block.get("data", {})
                    if isinstance(sub, dict):
                        raw_listings.extend(sub.get("listings", []))
                    elif isinstance(sub, list):
                        raw_listings.extend(sub)

            normalized = [normalize_listing(item) for item in raw_listings]

            return {
                "success": True,
                "totalCount": data.get("totalCount", len(normalized)),
                "count": len(normalized),
                "page": page,
                "listings": normalized,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "listings": []}

    def get_listing(self, listing_id: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves detailed information for a specific listing by ID.
        """
        url = f"{BASE_URL}/listings/{listing_id}"
        try:
            r = self.session.get(url, headers=self._get_headers(), timeout=12)
            if r.status_code == 200:
                data = r.json()
                return {"success": True, "listing": normalize_listing(data), "raw": data}
            else:
                return {"success": False, "error": f"آگهی یافت نشد یا حذف شده است (کد {r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_similar_listings(self, listing_id: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves similar / related listings for a given listing ID.
        """
        url = f"{BASE_URL}/listings/{listing_id}/relateds"
        try:
            r = self.session.get(url, headers=self._get_headers(), timeout=12)
            if r.status_code == 200:
                data = r.json()
                items = data if isinstance(data, list) else data.get("listings", [])
                normalized = [normalize_listing(item) for item in items]
                return {"success": True, "listings": normalized}
            else:
                return {"success": False, "error": f"خطا در دریافت آگهی‌های مشابه ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_contact(self, listing_id: Union[int, str], contact_type: str = "call") -> Dict[str, Any]:
        """
        Fetches contact info (phone number) for a listing.
        """
        url = f"{BASE_URL}/listings/{listing_id}/contact/{contact_type}"
        params = {"referrer": "listing"}
        try:
            r = self.session.get(url, params=params, headers=self._get_headers(), timeout=10)
            data = r.json()
            if r.status_code == 200 and "contactInfo" in data:
                return {
                    "success": True,
                    "phone": data.get("contactInfo"),
                    "listing_id": str(listing_id),
                }
            else:
                err = data.get("error", {}).get("errorMessage") if isinstance(data, dict) else r.text
                return {"success": False, "error": err or f"دریافت شماره با خطا مواجه شد ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def price_control(self, attribute_id: int, attribute_value: str) -> Dict[str, Any]:
        """
        Evaluates Sheypoor price control / valuation estimation for an item attribute.
        """
        url = f"{BASE_URL}/listings/priceControl"
        payload = {"attributeId": attribute_id, "attributeValue": attribute_value}
        try:
            r = self.session.post(url, json=payload, headers=self._get_headers(), timeout=10)
            data = r.json()
            if r.status_code == 200:
                return {"success": True, "result": data}
            else:
                return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_my_listings(self) -> Dict[str, Any]:
        """
        Fetches listings belonging to the authenticated user.
        """
        url = f"{BASE_URL}/user/listings"
        try:
            r = self.session.get(url, headers=self._get_headers(authenticated=True), timeout=12)
            if r.status_code == 200:
                data = r.json()
                items = data if isinstance(data, list) else data.get("data", [])
                normalized = [normalize_listing(item) for item in items]
                return {"success": True, "listings": normalized}
            else:
                return {"success": False, "error": f"نیاز به ورود به حساب کاربری دارد ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_bookmarks(self) -> Dict[str, Any]:
        """
        Fetches bookmarked / favorite ads for the authenticated user.
        """
        url = f"{BASE_URL}/listings/favorites"
        try:
            r = self.session.get(url, headers=self._get_headers(authenticated=True), timeout=12)
            if r.status_code == 200:
                data = r.json()
                items = data if isinstance(data, list) else data.get("listings", [])
                normalized = [normalize_listing(item) for item in items]
                return {"success": True, "bookmarks": normalized}
            else:
                return {"success": False, "error": f"نیاز به ورود به حساب کاربری دارد ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_bookmark(self, listing_id: Union[int, str]) -> Dict[str, Any]:
        """
        Bookmarks or unbookmarks a listing on Sheypoor.
        """
        url = f"{BASE_URL}/listings/favorites"
        payload = {"listingId": str(listing_id)}
        try:
            r = self.session.post(url, json=payload, headers=self._get_headers(authenticated=True), timeout=10)
            data = r.json()
            if r.status_code == 200:
                return {"success": True, "message": "نشان‌گذاری با موفقیت تغییر کرد", "result": data}
            else:
                return {"success": False, "error": f"خطا در نشان‌گذاری ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_chat_conversations(self) -> Dict[str, Any]:
        """
        Fetches chat conversation rooms for the authenticated user.
        """
        url = f"{BASE_URL}/chat/rooms"
        try:
            r = self.session.get(url, headers=self._get_headers(authenticated=True), timeout=12)
            if r.status_code == 200:
                data = r.json()
                return {"success": True, "conversations": data}
            else:
                return {"success": False, "error": f"نیاز به ورود به حساب کاربری دارد ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_chat_messages(self, room_id: Union[int, str]) -> Dict[str, Any]:
        """
        Fetches messages in a specific chat room.
        """
        url = f"{BASE_URL}/chat/rooms/{room_id}"
        try:
            r = self.session.get(url, headers=self._get_headers(authenticated=True), timeout=12)
            if r.status_code == 200:
                return {"success": True, "messages": r.json()}
            else:
                return {"success": False, "error": f"خطا در دریافت پیام‌ها ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
