"""
Normalization helpers for Sheypoor listings, prices, attributes, and locations.
"""

import re
from typing import Dict, Any, Optional, List

PERSIAN_TO_ENGLISH_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
ARABIC_TO_ENGLISH_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def convert_digits(text: str) -> str:
    """Converts Persian and Arabic digits to standard ASCII digits."""
    if not text:
        return ""
    return str(text).translate(PERSIAN_TO_ENGLISH_DIGITS).translate(ARABIC_TO_ENGLISH_DIGITS)


def parse_price(price_str: Optional[str]) -> Optional[int]:
    """Extracts integer price in Tomans from Persian price string."""
    if not price_str:
        return None
    cleaned = convert_digits(price_str)
    # Check for توافقی (negotiable) or مجانی (free)
    if any(k in price_str for k in ["توافقی", "رایگان", "مجانی", "جهت معاوضه"]):
        return None
    # Remove commas, currency words, whitespace
    digits = re.sub(r"[^\d]", "", cleaned)
    if digits:
        try:
            return int(digits)
        except ValueError:
            return None
    return None


def normalize_listing(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a Sheypoor raw listing (from search or details) into a standard schema.
    """
    listing_id = item.get("listingID") or item.get("id")
    title = item.get("title", "")
    price_str = item.get("priceString") or ""
    price_val = parse_price(price_str)

    loc = item.get("location", {}) or {}
    city = loc.get("city") or ""
    city_id = loc.get("cityId") or loc.get("cityID")
    province = loc.get("region") or loc.get("province") or ""
    neighbourhood = loc.get("neighbourhood") or ""

    cat = item.get("category", {}) or {}
    category_name = cat.get("c3") or cat.get("c2") or cat.get("c1") or cat.get("categoryTitle") or ""
    category_id = cat.get("categoryID") or cat.get("id")

    # Images
    images = []
    if "images" in item and isinstance(item["images"], list):
        for img in item["images"]:
            if isinstance(img, dict):
                url = img.get("imageURL") or img.get("originalURL") or img.get("thumbnailURL")
                if url:
                    images.append(url)
            elif isinstance(img, str):
                images.append(img)
    elif item.get("thumbImageURL"):
        images.append(item["thumbImageURL"])

    # Attributes
    attributes = {}
    if "attributes" in item and isinstance(item["attributes"], list):
        for attr in item["attributes"]:
            if isinstance(attr, dict):
                k = attr.get("attributeTitle") or attr.get("title") or attr.get("attributeLocalyticsKey")
                v = attr.get("attributeValue") or attr.get("value")
                if k and v:
                    attributes[k] = v

    description = item.get("description", "")
    time_str = item.get("sortInfo", "") or item.get("date", "")
    contact_types = item.get("contactInfo", [])

    return {
        "id": str(listing_id),
        "title": title,
        "price": price_val,
        "price_string": price_str,
        "city": city,
        "city_id": city_id,
        "province": province,
        "neighbourhood": neighbourhood,
        "category": category_name,
        "category_id": category_id,
        "time": time_str,
        "description": description,
        "images": images,
        "attributes": attributes,
        "contact_types": contact_types if isinstance(contact_types, list) else [],
        "url": f"https://www.sheypoor.com/v/{listing_id}.html" if listing_id else "",
    }


def format_listing_markdown(listing: Dict[str, Any]) -> str:
    """Formats a normalized listing as a clean Markdown card."""
    lines = [
        f"### [{listing['title']}]({listing['url']})",
        f"- **شناسه:** `{listing['id']}`",
        f"- **قیمت:** {listing['price_string'] or 'نامشخص'}",
        f"- **موقعیت:** {listing['province']} / {listing['city']}" + (f" ({listing['neighbourhood']})" if listing['neighbourhood'] else ""),
        f"- **دسته‌بندی:** {listing['category']}",
    ]
    if listing.get("time"):
        lines.append(f"- **زمان ثبت:** {listing['time']}")
    if listing.get("attributes"):
        attr_strs = [f"{k}: {v}" for k, v in listing["attributes"].items()]
        lines.append(f"- **ویژگی‌ها:** {', '.join(attr_strs[:5])}")
    if listing.get("description"):
        desc = listing["description"].strip().replace("\n", " ")
        lines.append(f"- **توضیحات:** {desc[:200]}..." if len(desc) > 200 else f"- **توضیحات:** {desc}")
    return "\n".join(lines)
