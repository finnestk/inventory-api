def test_get_all(client):
    r = client.get("/inventory")
    assert r.status_code == 200
    assert len(r.get_json()) == 3


def test_get_one(client):
    r = client.get("/inventory/2")
    assert r.status_code == 200
    assert r.get_json()["product_name"] == "Nutella"


def test_get_one_not_found(client):
    r = client.get("/inventory/999")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_post_creates_item(client):
    r = client.post("/inventory", json={"product_name": "Oat Milk", "price": 3.5, "stock": 10})
    assert r.status_code == 201
    assert r.get_json()["id"] == 4
    assert client.get("/inventory").get_json()[-1]["product_name"] == "Oat Milk"


def test_post_missing_name(client):
    r = client.post("/inventory", json={"price": 3})
    assert r.status_code == 400


def test_post_invalid_price(client):
    r = client.post("/inventory", json={"product_name": "X", "price": -1})
    assert r.status_code == 400


def test_post_invalid_stock_type(client):
    r = client.post("/inventory", json={"product_name": "X", "stock": "ten"})
    assert r.status_code == 400


def test_post_no_json_body(client):
    r = client.post("/inventory", data="not json")
    assert r.status_code == 400


def test_patch_updates_price_and_stock(client):
    r = client.patch("/inventory/1", json={"price": 2.0, "stock": 5})
    assert r.status_code == 200
    assert r.get_json()["price"] == 2.0
    assert client.get("/inventory/1").get_json()["stock"] == 5


def test_patch_not_found(client):
    r = client.patch("/inventory/999", json={"price": 1})
    assert r.status_code == 404


def test_patch_invalid_data(client):
    r = client.patch("/inventory/1", json={"price": "free"})
    assert r.status_code == 400


def test_patch_unknown_field(client):
    r = client.patch("/inventory/1", json={"colour": "red"})
    assert r.status_code == 400


def test_patch_cannot_change_id(client):
    r = client.patch("/inventory/1", json={"id": 50})
    assert r.status_code == 400


def test_delete(client):
    assert client.delete("/inventory/1").status_code == 200
    assert client.get("/inventory/1").status_code == 404
    assert len(client.get("/inventory").get_json()) == 2


def test_delete_not_found(client):
    assert client.delete("/inventory/999").status_code == 404