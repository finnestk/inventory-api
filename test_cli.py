from unittest.mock import patch

import pytest
import requests

import cli

ITEM = {
    "id": 1,
    "product_name": "Nutella",
    "brands": "Ferrero",
    "barcode": "301",
    "price": 4.25,
    "stock": 18,
    "ingredients_text": "Sugar",
}


def mock_call(status, body):
    return patch("cli.call", return_value=(status, body))


def test_list(capsys):
    with mock_call(200, [ITEM]):
        assert cli.main(["list"]) == 0
    assert "Nutella" in capsys.readouterr().out


def test_list_empty(capsys):
    with mock_call(200, []):
        cli.main(["list"])
    assert "empty" in capsys.readouterr().out.lower()


def test_view(capsys):
    with mock_call(200, ITEM) as m:
        assert cli.main(["view", "1"]) == 0
    m.assert_called_with("GET", "/inventory/1")
    assert "$4.25" in capsys.readouterr().out


def test_view_not_found(capsys):
    with mock_call(404, {"error": "Item not found"}):
        assert cli.main(["view", "99"]) == 1
    assert "Item not found" in capsys.readouterr().err


def test_add():
    with mock_call(201, ITEM) as m:
        code = cli.main(["add", "--name", "Nutella", "--price", "4.25", "--stock", "18"])
    assert code == 0
    assert m.call_args[0] == ("POST", "/inventory")
    assert m.call_args.kwargs["json"] == {"product_name": "Nutella", "price": 4.25, "stock": 18}


def test_add_shows_warning(capsys):
    with mock_call(201, {**ITEM, "warning": "Barcode not found"}):
        cli.main(["add", "--name", "X", "--barcode", "1"])
    assert "Barcode not found" in capsys.readouterr().out


def test_add_validation_error():
    with mock_call(400, {"error": "price must be a non-negative number"}):
        assert cli.main(["add", "--name", "X", "--price", "-5"]) == 1


def test_invalid_number_exits():
    with pytest.raises(SystemExit) as exc:
        cli.main(["add", "--name", "X", "--price", "abc"])
    assert exc.value.code == 2


def test_update():
    with mock_call(200, ITEM) as m:
        assert cli.main(["update", "1", "--price", "2", "--stock", "5"]) == 0
    assert m.call_args.kwargs["json"] == {"price": 2.0, "stock": 5}


def test_update_nothing_given(capsys):
    assert cli.main(["update", "1"]) == 1
    assert "provide" in capsys.readouterr().err.lower()


def test_delete(capsys):
    with mock_call(200, {"message": "Item 1 deleted"}):
        assert cli.main(["delete", "1"]) == 0
    assert "deleted" in capsys.readouterr().out


def test_find_by_barcode(capsys):
    body = {"status": 1, "product": {"product_name": "Nutella", "brands": "Ferrero", "barcode": "301"}}
    with mock_call(200, body) as m:
        assert cli.main(["find", "--barcode", "301"]) == 0
    assert m.call_args.kwargs["params"] == {"barcode": "301"}
    assert "Nutella" in capsys.readouterr().out


def test_find_by_name(capsys):
    body = {"count": 1, "products": [{"product_name": "Oat Drink", "brands": "Oatly"}]}
    with mock_call(200, body):
        assert cli.main(["find", "--name", "oat"]) == 0
    assert "Oat Drink" in capsys.readouterr().out


def test_find_requires_argument():
    assert cli.main(["find"]) == 1


def test_find_external_api_failure(capsys):
    with mock_call(502, {"error": "OpenFoodFacts request failed"}):
        assert cli.main(["find", "--name", "x"]) == 1
    assert "OpenFoodFacts" in capsys.readouterr().err


def test_server_down(capsys):
    with patch("cli.requests.request", side_effect=requests.ConnectionError()):
        assert cli.main(["list"]) == 1
    assert "cannot reach" in capsys.readouterr().err.lower()


def test_timeout(capsys):
    with patch("cli.requests.request", side_effect=requests.Timeout()):
        assert cli.main(["list"]) == 1
    assert "timed out" in capsys.readouterr().err.lower()