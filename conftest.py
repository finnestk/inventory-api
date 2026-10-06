import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.reset_inventory()
    with app_module.app.test_client() as c:
        yield c
