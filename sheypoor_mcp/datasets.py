import os
import json
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Sheypoor/7.0.7 (Android; Mobile; fa)",
    "Accept": "application/json",
    "X-AGENT-TYPE": "Android App",
    "X-BUILD-MODE": "Release",
    "X-FLAVOR": "direct",
}

def fetch_and_save():
    print("Fetching Sheypoor locations...")
    r_loc = requests.get("https://www.sheypoor.com/api/v7.0.7/general/locations", headers=HEADERS, timeout=15)
    r_loc.raise_for_status()
    locations = r_loc.json()
    
    # Flatten city map: name -> cityID, slug, province
    cities_map = {}
    for prov in locations:
        prov_name = prov.get("name")
        prov_id = prov.get("provinceID")
        for city in prov.get("cities", []):
            c_name = city.get("name")
            c_id = city.get("cityID")
            c_slug = city.get("slug")
            cities_map[c_name] = {
                "id": c_id,
                "name": c_name,
                "slug": c_slug,
                "provinceId": prov_id,
                "province": prov_name,
            }
            # Also lowercase ascii slug mapping
            if c_slug:
                cities_map[c_slug.lower()] = cities_map[c_name]

    with open(os.path.join(DATA_DIR, "locations.json"), "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA_DIR, "cities.json"), "w", encoding="utf-8") as f:
        json.dump(cities_map, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(locations)} provinces and {len(cities_map)} city index entries.")

    print("Fetching Sheypoor categories...")
    r_cat = requests.get("https://www.sheypoor.com/api/v7.0.7/general/categories", headers=HEADERS, timeout=15)
    r_cat.raise_for_status()
    categories = r_cat.json()

    with open(os.path.join(DATA_DIR, "categories.json"), "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    print(f"Saved categories data.")

if __name__ == "__main__":
    fetch_and_save()
