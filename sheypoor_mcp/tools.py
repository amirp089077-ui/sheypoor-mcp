"""
Tool registry and executors for Sheypoor MCP Server.
"""

from typing import Dict, Any, List
from .client import SheypoorClient
from .auth_client import SheypoorAuth
from .resolve import resolve_city, get_cities_map, get_categories_data
from .analytics import analyze_prices, find_deals, appraise_listing
from .normalize import format_listing_markdown

client = SheypoorClient()

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "sheypoor_search",
        "description": "جستجوی آگهی‌های شیپور با پشتیبانی از چند شهر همزمان، فیلتر دسته‌بندی و محدوده قیمت",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "عبارت جستجو (مثلا 'پیکان وانت' یا 'آیفون 13')"},
                "cities": {"type": "string", "description": "نام شهر یا شهرهای مورد نظر (مثلا 'شیراز' یا 'شاهرود, شیراز')"},
                "category": {"type": "string", "description": "نام یا شناسه دسته‌بندی (مثلا 'خودرو' یا 'املاک')"},
                "page": {"type": "integer", "description": "شماره صفحه (پیش‌فرض: 1)", "default": 1},
                "min_price": {"type": "integer", "description": "حداقل قیمت به تومان"},
                "max_price": {"type": "integer", "description": "حداکثر قیمت به تومان"},
            },
        },
    },
    {
        "name": "sheypoor_get_listing",
        "description": "دریافت جزییات کامل یک آگهی در شیپور بر اساس شناسه آگهی",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string", "description": "شناسه آگهی (listingID)"},
            },
            "required": ["listing_id"],
        },
    },
    {
        "name": "sheypoor_get_contact",
        "description": "دریافت مستقیم شماره تماس فروشنده آگهی در شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string", "description": "شناسه آگهی (listingID)"},
                "contact_type": {"type": "string", "description": "نوع تماس ('call' یا 'sms')", "default": "call"},
            },
            "required": ["listing_id"],
        },
    },
    {
        "name": "sheypoor_similar_listings",
        "description": "یافتن آگهی‌های مشابه برای یک آگهی مشخص در شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string", "description": "شناسه آگهی"},
            },
            "required": ["listing_id"],
        },
    },
    {
        "name": "sheypoor_price_analysis",
        "description": "تحلیل آماری قیمت بازار (میانگین، میانه، حداقل و حداکثر) برای یک جستجو در شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "عبارت جستجو"},
                "cities": {"type": "string", "description": "شهر یا شهرهای مورد نظر"},
                "category": {"type": "string", "description": "دسته‌بندی"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "sheypoor_find_deals",
        "description": "یافتن آگهی‌های خوش‌قیمت و زیر قیمت بازار در شیپور (معاملات طلایی)",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "عبارت جستجو"},
                "cities": {"type": "string", "description": "شهر یا شهرهای مورد نظر"},
                "discount_percentage": {"type": "number", "description": "حداقل درصد تخفیف نسبت به میانگین بازار (پیش‌فرض: 15)", "default": 15},
            },
            "required": ["query"],
        },
    },
    {
        "name": "sheypoor_appraise_listing",
        "description": "ارزیابی قیمت یک آگهی مشخص و مقایسه آن با عرف بازار در شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string", "description": "شناسه آگهی مورد نظر"},
            },
            "required": ["listing_id"],
        },
    },
    {
        "name": "sheypoor_list_cities",
        "description": "مشاهده یا جستجوی شهرها و استان‌های کشور در دیتابیس شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "فیلتر نام شهر یا استان"},
                "province": {"type": "string", "description": "نام استان برای مشاهده شهرهای آن"},
            },
        },
    },
    {
        "name": "sheypoor_list_categories",
        "description": "مشاهده درخت دسته‌بندی‌های شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "parent_id": {"type": "integer", "description": "شناسه دسته‌بندی والد (اختیاری)"},
            },
        },
    },
    {
        "name": "sheypoor_auth_send_otp",
        "description": "ارسال کد تایید پیامکی (OTP) برای ورود به حساب کاربری شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "شماره تلفن همراه (مثلا '09121234567')"},
            },
            "required": ["phone"],
        },
    },
    {
        "name": "sheypoor_auth_verify_otp",
        "description": "تایید کد پیامکی دریافت شده و ورود به حساب شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "token": {"type": "string", "description": "توکن مرحله قبل که از sheypoor_auth_send_otp دریافت شد"},
                "pin": {"type": "string", "description": "کد تایید پیامکی (OTP)"},
            },
            "required": ["token", "pin"],
        },
    },
    {
        "name": "sheypoor_auth_set_token",
        "description": "تنظیم دستی توکن احراز هویت (xTicket) شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "token": {"type": "string", "description": "توکن xTicket"},
                "phone": {"type": "string", "description": "شماره موبایل مربوطه (اختیاری)"},
            },
            "required": ["token"],
        },
    },
    {
        "name": "sheypoor_auth_status",
        "description": "بررسی وضعیت ورود و اطلاعات حساب کاربری در شیپور",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "sheypoor_auth_logout",
        "description": "خروج از حساب کاربری شیپور و حذف توکن",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "sheypoor_get_my_listings",
        "description": "دریافت لیست آگهی‌های ثبت شده توسط کاربر در شیپور",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "sheypoor_get_my_bookmarks",
        "description": "دریافت لیست آگهی‌های نشان‌شده (علاقه‌مندی‌ها) در شیپور",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "sheypoor_bookmark_listing",
        "description": "نشان‌کردن یا حذف نشان یک آگهی در شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string", "description": "شناسه آگهی"},
            },
            "required": ["listing_id"],
        },
    },
    {
        "name": "sheypoor_chat_conversations",
        "description": "مشاهده لیست گفتگوهای چت کاربر در شیپور",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "sheypoor_chat_messages",
        "description": "مشاهده پیام‌های یک چت خاص در شیپور",
        "parameters": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string", "description": "شناسه اتاق گفتگو"},
            },
            "required": ["room_id"],
        },
    },
    {
        "name": "sheypoor_chat_send_message",
        "description": "ارسال پیام در چت شیپور به فروشنده آگهی",
        "parameters": {
            "type": "object",
            "properties": {
                "listing_id": {"type": "string", "description": "شناسه آگهی"},
                "message": {"type": "string", "description": "متن پیام"},
            },
            "required": ["listing_id", "message"],
        },
    },
    {
        "name": "sheypoor_status",
        "description": "بررسی سلامت سرور Sheypoor MCP و نسخه API",
        "parameters": {"type": "object", "properties": {}},
    },

]


def execute_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Dispatches tool execution to appropriate handler."""
    if name == "sheypoor_search":
        res = client.search(
            query=arguments.get("query"),
            cities=arguments.get("cities"),
            category=arguments.get("category"),
            page=arguments.get("page", 1),
            min_price=arguments.get("min_price"),
            max_price=arguments.get("max_price"),
        )
        return res

    elif name == "sheypoor_get_listing":
        return client.get_listing(arguments["listing_id"])

    elif name == "sheypoor_get_contact":
        return client.get_contact(
            arguments["listing_id"],
            arguments.get("contact_type", "call"),
        )

    elif name == "sheypoor_similar_listings":
        return client.get_similar_listings(arguments["listing_id"])

    elif name == "sheypoor_price_analysis":
        res = client.search(
            query=arguments.get("query"),
            cities=arguments.get("cities"),
            category=arguments.get("category"),
        )
        listings = res.get("listings", [])
        stats = analyze_prices(listings)
        return {
            "query": arguments.get("query"),
            "cities": arguments.get("cities"),
            "analysis": stats,
            "sample_size": len(listings),
        }

    elif name == "sheypoor_find_deals":
        res = client.search(
            query=arguments.get("query"),
            cities=arguments.get("cities"),
        )
        listings = res.get("listings", [])
        thresh = float(arguments.get("discount_percentage", 15)) / 100.0
        deals = find_deals(listings, discount_threshold=thresh)
        return {
            "query": arguments.get("query"),
            "deals_count": len(deals),
            "deals": deals,
        }

    elif name == "sheypoor_appraise_listing":
        lid = arguments["listing_id"]
        ad_res = client.get_listing(lid)
        if not ad_res.get("success"):
            return ad_res
        target = ad_res["listing"]
        # Search for similar market listings by title / category
        market_res = client.search(
            query=target.get("title"),
            cities=target.get("city"),
        )
        market_listings = market_res.get("listings", [])
        return {
            "listing": target,
            "appraisal": appraise_listing(target, market_listings),
        }

    elif name == "sheypoor_list_cities":
        cities_map = get_cities_map()
        search_kw = arguments.get("search", "").strip().lower()
        province_kw = arguments.get("province", "").strip().lower()

        results = []
        for k, info in cities_map.items():
            if not isinstance(info, dict) or not info.get("name"):
                continue
            c_name = info.get("name", "").lower()
            p_name = (info.get("province") or "").lower()
            
            if search_kw and search_kw not in c_name and search_kw not in p_name:
                continue
            if province_kw and province_kw not in p_name:
                continue
            results.append(info)

        # De-duplicate by ID
        seen = set()
        unique = []
        for r in results:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique.append(r)

        return {"count": len(unique), "cities": unique[:100]}

    elif name == "sheypoor_list_categories":
        return {"categories": get_categories_data()}


    elif name == "sheypoor_auth_send_otp":
        return client.auth.send_otp(arguments["phone"])

    elif name == "sheypoor_auth_verify_otp":
        return client.auth.verify_otp(arguments["token"], arguments["pin"])

    elif name == "sheypoor_auth_set_token":
        return client.auth.set_token(arguments["token"], arguments.get("phone"))

    elif name == "sheypoor_auth_status":
        return client.auth.get_status()

    elif name == "sheypoor_auth_logout":
        return client.auth.logout()

    elif name == "sheypoor_get_my_listings":
        return client.get_my_listings()

    elif name == "sheypoor_get_my_bookmarks":
        return client.get_bookmarks()

    elif name == "sheypoor_bookmark_listing":
        return client.toggle_bookmark(arguments["listing_id"])

    elif name == "sheypoor_chat_conversations":
        return client.get_chat_conversations()

    elif name == "sheypoor_chat_messages":
        return client.get_chat_messages(arguments["room_id"])

    elif name == "sheypoor_chat_send_message":
        return client.send_chat_message(arguments["listing_id"], arguments["message"])

    elif name == "sheypoor_status":

        auth_st = client.auth.get_status()
        return {
            "server": "Sheypoor MCP Server",
            "version": "1.0.0",
            "sheypoor_api_version": "v7.0.7",
            "authenticated": auth_st.get("authenticated", False),
            "user_phone": auth_st.get("phone"),
            "endpoints_healthy": True,
        }

    else:
        return {"error": f"ابزار ناشناخته: {name}"}
