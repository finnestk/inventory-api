import argparse
import os
import sys

import requests

BASE_URL = os.environ.get("INVENTORY_API_URL", "http://127.0.0.1:5001")


def call(method, path, **kwargs):
    response = requests.request(method, f"{BASE_URL}{path}", timeout=15, **kwargs)
    try:
        body = response.json()
    except ValueError:
        body = {"error": "Server returned an invalid response"}
    return response.status_code, body


def show_item(item):
    print(f"[{item['id']}] {item['product_name']}  ({item.get('brands') or 'no brand'})")
    print(f"    Barcode: {item.get('barcode') or '-'} | Price: ${item['price']:.2f} | Stock: {item['stock']}")
    if item.get("ingredients_text"):
        print(f"    Ingredients: {item['ingredients_text']}")


def show_external(product):
    print(f"{product.get('product_name') or '(no name)'} - {product.get('brands') or 'no brand'}")
    print(f"    Barcode: {product.get('barcode') or '-'}")
    if product.get("ingredients_text"):
        print(f"    Ingredients: {product['ingredients_text']}")


def fail(body, status):
    print(f"Error ({status}): {body.get('error', 'Unknown error')}", file=sys.stderr)
    return 1


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory Management CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all items")

    p = sub.add_parser("view", help="View one item")
    p.add_argument("id", type=int)

    p = sub.add_parser("add", help="Add an item")
    p.add_argument("--name", required=True)
    p.add_argument("--price", type=float, default=0.0)
    p.add_argument("--stock", type=int, default=0)
    p.add_argument("--barcode", default="")
    p.add_argument("--brand", default="")

    p = sub.add_parser("update", help="Update price and/or stock")
    p.add_argument("id", type=int)
    p.add_argument("--price", type=float)
    p.add_argument("--stock", type=int)

    p = sub.add_parser("delete", help="Delete an item")
    p.add_argument("id", type=int)

    p = sub.add_parser("find", help="Find a product on OpenFoodFacts")
    p.add_argument("--barcode")
    p.add_argument("--name")

    return parser


def run(args):
    if args.command == "list":
        status, body = call("GET", "/inventory")
        if status != 200:
            return fail(body, status)
        if not body:
            print("Inventory is empty.")
        for item in body:
            show_item(item)
        return 0

    if args.command == "view":
        status, body = call("GET", f"/inventory/{args.id}")
        if status != 200:
            return fail(body, status)
        show_item(body)
        return 0

    if args.command == "add":
        payload = {"product_name": args.name, "price": args.price, "stock": args.stock}
        if args.barcode:
            payload["barcode"] = args.barcode
        if args.brand:
            payload["brands"] = args.brand
        status, body = call("POST", "/inventory", json=payload)
        if status != 201:
            return fail(body, status)
        print("Item added:")
        show_item(body)
        if body.get("warning"):
            print(f"Note: {body['warning']}")
        return 0

    if args.command == "update":
        payload = {}
        if args.price is not None:
            payload["price"] = args.price
        if args.stock is not None:
            payload["stock"] = args.stock
        if not payload:
            print("Error: provide --price and/or --stock", file=sys.stderr)
            return 1
        status, body = call("PATCH", f"/inventory/{args.id}", json=payload)
        if status != 200:
            return fail(body, status)
        print("Item updated:")
        show_item(body)
        return 0

    if args.command == "delete":
        status, body = call("DELETE", f"/inventory/{args.id}")
        if status != 200:
            return fail(body, status)
        print(body["message"])
        return 0

    if args.command == "find":
        if not (args.barcode or args.name):
            print("Error: provide --barcode or --name", file=sys.stderr)
            return 1
        params = {"barcode": args.barcode} if args.barcode else {"name": args.name}
        status, body = call("GET", "/external/search", params=params)
        if status != 200:
            return fail(body, status)
        if "product" in body:
            show_external(body["product"])
        else:
            if not body["products"]:
                print("No products found.")
            for product in body["products"]:
                show_external(product)
        return 0

    return 1


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except requests.ConnectionError:
        print(f"Error: cannot reach the API at {BASE_URL}. Is the server running?", file=sys.stderr)
        return 1
    except requests.Timeout:
        print("Error: the API request timed out.", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Error: request failed ({exc})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())