import sys
import pytest
import os

sys.path.append("./")
import vendOmatic as vom
import datafuncs as dataf


@pytest.fixture
def app():
    # app = create_app()
    config = {"TESTING": True}
    app = vom.createApp(config)

    dataf.createDB("test", True)
    os.environ["DBNAME"] = "test"
    dataf.setupDB()
    yield app

    del os.environ["DBNAME"]
    dataf.dropDB("test")


@pytest.fixture
def client(app):
    return app.test_client()


# def test_coin_insert_success(client):
#    response = client.put("/", json={"coin": 1})
#    response = client.put("/", json={"coin": 1})
#    assert response.headers[0] == ("X-Coins", "1")
#    assert response.status_code == 204


def test_coin_return(client):
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.delete("/")
    assert response.headers[0] == ("X-Coins", "2")
    assert response.status_code == 204


def test_coin_insert_not_json_failure(client):
    response = client.put("/")
    assert response.status_code == 415
    response = client.put("/", json={"wombat": 1})
    assert response.status_code == 415


def test_coin_insert_more_than_one(client):
    response = client.put("/", json={"coin": 4})
    assert response.headers[0] == ("X-Coins", "1")
    assert response.status_code == 204


def test_inventory(client):
    response = client.get("/inventory/0")
    assert response.get_json() == 5
    response = client.get("/inventory")
    assert response.get_json() == [5, 5, 5]
    response = client.get("/inventory/100")
    assert response.get_json() == 0


def test_purchasing(client):
    response = client.put("/inventory/1")
    assert response.headers[0] == ("X-Coins", "0")
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/1")
    assert response.headers[0] == ("X-Coins", "1")
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/1")
    assert response.headers[0] == ("X-Coins", "0")
    assert response.headers[1] == ("X-Inventory-Remaining", "4")


def test_purchaseing_exceptions(client):
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/2")
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/2")
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/2")
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/2")
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/2")
    assert response.headers[0] == ("X-Coins", "1")
    assert response.headers[1] == ("X-Inventory-Remaining", "0")
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/2")
    assert response.headers[0] == ("X-Coins", "2")
    assert response.status_code == 404
