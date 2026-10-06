# Inventory Management System

Flask REST API with a CLI and OpenFoodFacts integration.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API
```bash
python app.py
```
Runs on http://127.0.0.1:5001

## API endpoints
| Method | Route | Purpose |
|---|---|---|
| GET | /inventory | Fetch all items |
| GET | /inventory/<id> | Fetch one item |
| POST | /inventory | Add an item (a barcode pulls extra details from OpenFoodFacts) |
| PATCH | /inventory/<id> | Update an item |
| DELETE | /inventory/<id> | Delete an item |
| GET | /external/search?barcode=... or ?name=... | Look up a product on OpenFoodFacts |

## CLI
```bash
python cli.py list
python cli.py view 1
python cli.py add --name "Oat Milk" --price 3.5 --stock 10 --barcode 7394376616228
python cli.py update 1 --price 2.00 --stock 50
python cli.py delete 1
python cli.py find --barcode 3017620422003
python cli.py find --name nutella
```

## Tests
```bash
pytest -v
```
Uses pytest and unittest.mock to simulate OpenFoodFacts and API responses.