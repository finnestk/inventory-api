from flask import Flask, jsonify

app = Flask(__name__)

# Simulated database: a plain list of dictionaries.
# Field names mirror OpenFoodFacts (product_name, brands, ingredients_text).
inventory = [
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


@app.get("/inventory")
def get_inventory():
    return jsonify(inventory), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)