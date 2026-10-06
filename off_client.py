import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryManager/1.0"}


class ExternalAPIError(Exception):
    pass


def clean(product):
    return {
        "barcode": product.get("code", ""),
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
    }


def fetch_by_barcode(barcode):
    try:
        response = requests.get(
            f"{BASE_URL}/api/v0/product/{barcode}.json", headers=HEADERS, timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ExternalAPIError(f"OpenFoodFacts request failed: {exc}")
    if data.get("status") != 1:
        return None
    return clean(data["product"])


def search_by_name(name):
    try:
        response = requests.get(
            f"{BASE_URL}/cgi/search.pl",
            params={"search_terms": name, "search_simple": 1, "action": "process", "json": 1, "page_size": 5},
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ExternalAPIError(f"OpenFoodFacts request failed: {exc}")
    return [clean(p) for p in data.get("products", [])]