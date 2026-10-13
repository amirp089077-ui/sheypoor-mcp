"""
Market price intelligence, deal hunting, and valuation analysis for Sheypoor listings.
"""

from typing import List, Dict, Any, Optional
import statistics


def analyze_prices(listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes market price distribution, median, mean, and range for a set of listings.
    """
    valid_prices = [
        item["price"]
        for item in listings
        if item.get("price") is not None and isinstance(item.get("price"), (int, float)) and item["price"] > 0
    ]

    if not valid_prices:
        return {
            "total_listings": len(listings),
            "priced_listings": 0,
            "min_price": None,
            "max_price": None,
            "avg_price": None,
            "median_price": None,
            "p25": None,
            "p75": None,
        }

    valid_prices.sort()
    n = len(valid_prices)
    avg = int(sum(valid_prices) / n)
    med = int(statistics.median(valid_prices))
    p25 = valid_prices[int(n * 0.25)]
    p75 = valid_prices[int(n * 0.75)]

    return {
        "total_listings": len(listings),
        "priced_listings": n,
        "min_price": valid_prices[0],
        "max_price": valid_prices[-1],
        "avg_price": avg,
        "median_price": med,
        "p25": p25,
        "p75": p75,
    }


def find_deals(
    listings: List[Dict[str, Any]], discount_threshold: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Finds listings priced below market median by at least `discount_threshold` (e.g. 15%).
    """
    stats = analyze_prices(listings)
    med = stats.get("median_price")
    if not med or med <= 0:
        return []

    deals = []
    for item in listings:
        p = item.get("price")
        if p and p > 0 and p <= med * (1.0 - discount_threshold):
            diff = med - p
            pct = round((diff / med) * 100, 1)
            deals.append({
                **item,
                "market_median": med,
                "savings": diff,
                "discount_percentage": pct,
            })

    deals.sort(key=lambda x: x["discount_percentage"], reverse=True)
    return deals


def appraise_listing(
    target: Dict[str, Any], market_listings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Appraises whether a target listing is underpriced, fairly priced, or overpriced.
    """
    stats = analyze_prices(market_listings)
    med = stats.get("median_price")
    target_price = target.get("price")

    if not target_price or not med:
        return {
            "verdict": "UNKNOWN",
            "message": "قیمت آگهی یا میانگین بازار برای ارزیابی کافی نیست",
            "market_stats": stats,
        }

    ratio = target_price / med
    diff = target_price - med
    pct = round(abs(ratio - 1.0) * 100, 1)

    if ratio <= 0.85:
        verdict = "GREAT_DEAL"
        msg = f"قیمت {pct}٪ زیر میانگین بازار است (معامله عالی)"
    elif ratio <= 1.05:
        verdict = "FAIR_PRICE"
        msg = f"قیمت منصفانه و منطبق بر عرف بازار است (تفاضل حدود {pct}٪)"
    else:
        verdict = "ABOVE_MARKET"
        msg = f"قیمت {pct}٪ بالاتر از میانگین بازار است"

    return {
        "verdict": verdict,
        "message": msg,
        "target_price": target_price,
        "market_median": med,
        "difference": diff,
        "market_stats": stats,
    }
