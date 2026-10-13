"""
City and category resolver for Sheypoor MCP.
Resolves Persian names, English slugs, and fuzzy spelling variants to Sheypoor IDs.
"""

import json
import os
import re
from typing import Optional, Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

_CITIES_MAP: Optional[Dict[str, Any]] = None
_CATEGORIES_DATA: Optional[List[Dict[str, Any]]] = None


def normalize_persian(text: str) -> str:
    """Normalize Arabic/Persian letters, zero-width spaces, and whitespace."""
    if not text:
        return ""
    text = text.strip()
    # Normalize yeh
    text = text.replace("\u064a", "\u06cc").replace("\u0649", "\u06cc")
    # Normalize kaf
    text = text.replace("\u0643", "\u06a9")
    # Normalize heh yeh
    text = text.replace("\u06c0", "\u0647\u0654")
    # Remove half-space / zero-width non-joiner
    text = text.replace("\u200c", " ").replace("\u200f", "")
    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _load_data():
    global _CITIES_MAP, _CATEGORIES_DATA
    if _CITIES_MAP is None:
        path = os.path.join(DATA_DIR, "cities.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _CITIES_MAP = json.load(f)
        else:
            _CITIES_MAP = {}

    if _CATEGORIES_DATA is None:
        path = os.path.join(DATA_DIR, "categories.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _CATEGORIES_DATA = json.load(f)
        else:
            _CATEGORIES_DATA = []


def get_cities_map() -> Dict[str, Any]:
    global _CITIES_MAP
    if _CITIES_MAP is None:
        _load_data()
    return _CITIES_MAP or {}



def get_categories_data() -> List[Dict[str, Any]]:
    global _CATEGORIES_DATA
    if _CATEGORIES_DATA is None:
        _load_data()
    return _CATEGORIES_DATA or []



def resolve_city(name_or_slug: str) -> Optional[Dict[str, Any]]:
    """
    Resolves a city name (Persian or English slug) to Sheypoor city info.
    Returns: {"id": int, "name": str, "slug": str, "provinceId": int, "province": str}
    """
    _load_data()
    if not name_or_slug:
        return None

    raw = name_or_slug.strip().lower()
    norm = normalize_persian(name_or_slug)

    # 1. Exact match
    if raw in _CITIES_MAP:
        return _CITIES_MAP[raw]
    if norm in _CITIES_MAP:
        return _CITIES_MAP[norm]

    # 2. Check normalized keys
    for k, v in _CITIES_MAP.items():
        if normalize_persian(k) == norm:
            return v

    # 3. Common aliases
    aliases = {
        "تهران": "tehran",
        "مشهد": "mashhad",
        "اصفهان": "isfahan",
        "شیراز": "shiraz",
        "تبریز": "tabriz",
        "کرج": "karaj",
        "قم": "qom",
        "اهواز": "ahvaz",
        "کرمانشاه": "kermanshah",
        "ارومیه": "urmia",
        "رشت": "rasht",
        "زاهدان": "zahedan",
        "همدان": "hamedan",
        "کرمان": "kerman",
        "یزد": "yazd",
        "اردبیل": "ardabil",
        "بندرعباس": "bandar-abbas",
        "اراک": "arak",
        "زنجان": "zanjan",
        "سنندج": "sanandaj",
        "قزوین": "qazvin",
        "خرم اباد": "khorramabad",
        "خرم‌آباد": "khorramabad",
        "گرگان": "gorgan",
        "ساری": "sari",
        "بجنورد": "bojnurd",
        "بوشهر": "bushehr",
        "بیرجند": "birjand",
        "ایلام": "ilam",
        "شهرکرد": "shahrekord",
        "یاسوج": "yasuj",
        "سمنان": "semnan",
        "شاهرود": "shahroud",
        "سبزوار": "sabzevar",
        "نیشابور": "neyshabur",
        "بابل": "babol",
        "امل": "amol",
        "آمل": "amol",
        "قائمشهر": "qaem-shahr",
        "قائم شهر": "qaem-shahr",
        "کاشان": "kashan",
    }
    
    if norm in aliases and aliases[norm] in _CITIES_MAP:
        return _CITIES_MAP[aliases[norm]]
    if raw in aliases and aliases[raw] in _CITIES_MAP:
        return _CITIES_MAP[aliases[raw]]

    # 4. Partial substring matching
    for k, v in _CITIES_MAP.items():
        nk = normalize_persian(k)
        if norm and (norm in nk or nk in norm):
            return v

    return None


def resolve_category(name_or_id: str) -> Optional[int]:
    """
    Resolves a category name or ID string to Sheypoor's numeric category ID.
    """
    _load_data()
    if not name_or_id:
        return None

    if str(name_or_id).isdigit():
        return int(name_or_id)

    norm = normalize_persian(str(name_or_id))

    def search_in_tree(items):
        for item in items:
            title = normalize_persian(item.get("categoryTitle", "") or item.get("name", ""))
            if norm == title or norm in title:
                return item.get("categoryID") or item.get("id")
            subs = item.get("subCategories", []) or item.get("children", [])
            found = search_in_tree(subs)
            if found:
                return found
        return None

    return search_in_tree(_CATEGORIES_DATA)
