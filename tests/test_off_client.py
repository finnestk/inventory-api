from unittest.mock import MagicMock, patch

import pytest
import requests

import off_client


def fake_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


@patch("off_client.requests.get")
def test_fetch_by_barcode_success(mock_get):
    mock_get.return_value = fake_response({
        "status": 1,
        "product": {
            "code": "123",
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds",
        },
    })
    product = off_client.fetch_by_barcode("123")
    assert product["product_name"] == "Organic Almond Milk"
    assert product["brands"] == "Silk"


@patch("off_client.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_get.return_value = fake_response({"status": 0})
    assert off_client.fetch_by_barcode("000") is None


@patch("off_client.requests.get", side_effect=requests.ConnectionError("no network"))
def test_fetch_by_barcode_network_error(mock_get):
    with pytest.raises(off_client.ExternalAPIError):
        off_client.fetch_by_barcode("123")


@patch("off_client.requests.get")
def test_fetch_by_barcode_http_error(mock_get):
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("503")
    mock_get.return_value = response
    with pytest.raises(off_client.ExternalAPIError):
        off_client.fetch_by_barcode("123")


@patch("off_client.requests.get")
def test_search_by_name_success(mock_get):
    mock_get.return_value = fake_response({
        "products": [
            {"code": "1", "product_name": "Nutella", "brands": "Ferrero"},
            {"code": "2", "product_name": "Nutella B-ready", "brands": "Ferrero"},
        ]
    })
    results = off_client.search_by_name("nutella")
    assert len(results) == 2
    assert results[0]["product_name"] == "Nutella"


@patch("off_client.requests.get")
def test_search_by_name_no_results(mock_get):
    mock_get.return_value = fake_response({"products": []})
    assert off_client.search_by_name("zzzz") == []


@patch("off_client.requests.get", side_effect=requests.Timeout("too slow"))
def test_search_by_name_failure(mock_get):
    with pytest.raises(off_client.ExternalAPIError):
        off_client.search_by_name("nutella")