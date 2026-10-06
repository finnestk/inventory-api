import copy

from flask import Flask, jsonify, request

import off_client

app = Flask(__name__)

SEED_DATA = [
    {
        "id": 1,
        "barcode": "5449000000996",
        "product_name": "Coca-Cola Original",
        "brands": "Coca-Cola",
        "ingredients_text": "Carbonated water, sugar, colour (caramel E150d), acid (phosphoric acid), flavourings",
        "price": 1.50,
        "stock": 40,
    },
    {
        "id": 2,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts 13%, skimmed milk powder 8.7%, cocoa 7.4%, lecithin, vanillin",
        "price": 4.25,
        "stock": 18,
    },
    {
        "id": 3,
        "barcode": "0000000000001",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, locust bean gum",
        "price": 3.99,
        "stock": 25,
    },
]

inventory = []


def reset_inventory():
    inventory.clear()
    inventory.extend(copy.deepcopy(SEED_DATA))


reset_inventory()

ALLOWED_FIELDS = {"barcode", "product_name", "brands", "ingredients_text", "price", "stock"}


def error(message, status):
    return jsonify({"error": message}), status


def find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)


def next_id():
    return max((item["id"] for item in inventory), default=0) + 1


def validate(data, require_name):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    unknown = set(data) - ALLOWED_FIELDS
    if unknown:
        return f"Unknown field(s): {', '.join(sorted(unknown))}"

    if require_name and not str(data.get("product_name", "")).strip():
        return "product_name is required"

    if "product_name" in data and not str(data["product_name"]).strip():
        return "product_name cannot be empty"

    if "price" in data:
        p = data["price"]
        if isinstance(p, bool) or not isinstance(p, (int, float)) or p < 0:
            return "price must be a non-negative number"

    if "stock" in data:
        s = data["stock"]
        if isinstance(s, bool) or not isinstance(s, int) or s < 0:
            return "stock must be a non-negative integer"

    return None


@app.get("/")
def home():
    return jsonify({"message": "Inventory API is running. Try /inventory"}), 200


@app.get("/inventory")
def get_inventory():
    return jsonify(inventory), 200


@app.get("/inventory/<int:item_id>")
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return error("Item not found", 404)
    return jsonify(item), 200


@app.post("/inventory")
def add_item():
    data = request.get_json(silent=True)
    problem = validate(data, require_name=True)
    if problem:
        return error(problem, 400)

    item = {
        "id": next_id(),
        "barcode": data.get("barcode", ""),
        "product_name": data["product_name"].strip(),
        "brands": data.get("brands", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
    }

    warning = None
    if item["barcode"]:
        try:
            details = off_client.fetch_by_barcode(item["barcode"])
            if details:
                if not item["brands"]:
                    item["brands"] = details["brands"]
                if not item["ingredients_text"]:
                    item["ingredients_text"] = details["ingredients_text"]
            else:
                warning = "Barcode not found on OpenFoodFacts"
        except off_client.ExternalAPIError:
            warning = "OpenFoodFacts unavailable; item saved without extra details"

    inventory.append(item)
    response_body = dict(item)
    if warning:
        response_body["warning"] = warning
    return jsonify(response_body), 201


@app.patch("/inventory/<int:item_id>")
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return error("Item not found", 404)

    data = request.get_json(silent=True)
    problem = validate(data, require_name=False)
    if problem:
        return error(problem, 400)

    item.update(data)
    return jsonify(item), 200


@app.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return error("Item not found", 404)
    inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200


@app.get("/external/search")
def external_search():
    barcode = request.args.get("barcode", "").strip()
    name = request.args.get("name", "").strip()
    if not barcode and not name:
        return error("Provide a 'barcode' or 'name' query parameter", 400)

    try:
        if barcode:
            product = off_client.fetch_by_barcode(barcode)
            if product is None:
                return error("Product not found on OpenFoodFacts", 404)
            return jsonify({"status": 1, "product": product}), 200
        products = off_client.search_by_name(name)
        return jsonify({"count": len(products), "products": products}), 200
    except off_client.ExternalAPIError as exc:
        return error(str(exc), 502)


if __name__ == "__main__":
    app.run(debug=True, port=5001)