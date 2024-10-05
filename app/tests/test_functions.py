import sys

sys.path.append("./")
import pytest
import sqlalchemy as sql

import schema as sch
import devUtils as dev
import main as mn


def itemGen(idx, name, sold, cost, inventory):
    return {"id": idx, "name": name, "sold": sold, "cost": cost, "inventory": inventory}


@pytest.fixture
def app():
    # app = create_app()
    app = mn.app
    db = sch.db
    app.config.update(
        {
            "TESTING": True,
        }
    )

    config = {
        "DBNAME": "testing",
        "DBURL": "postgres",
        "DBPASS": "devtest",
        "DBUSER": "postgres",
    }

    dev.setupDB(config)

    app.config["SQLALCHEMY_DATABASE_URI"] = dev.createSQLAlcURL(config)
    if "sqlalchemy" not in app.extensions:
        db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()
        items = [
            itemGen(i, x, 0, 0.50, 5)
            for i, x in enumerate(
                ["Milk Tea 500mL", "Green Tea 500mL", "Boba Tea 500mL"]
            )
        ]
        stmt = sql.insert(sch.Items).values(items)
        db.session.execute(stmt)
        quarter = sch.Cash(id="quarter_usd", banked=0, number=0, denomination=0.25)
        db.session.add(quarter)
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_coin_insert_success(client):
    response = client.put("/", json={"coin": 1})
    assert response.headers[0] == ("X-Coins:", "1")
    assert response.status_code == 204


def test_coin_return(client):
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.delete("/")
    assert response.headers[0] == ("X-Coins:", "2")
    assert response.status_code == 204


def test_coin_insert_not_json_failure(client):
    response = client.put("/")
    assert response.status_code == 415
    response = client.put("/", json={"wombat": 1})
    assert response.status_code == 415


def test_coin_insert_more_than_one(client):
    response = client.put("/", json={"coin": 4})
    assert response.headers[0] == ("X-Coins:", "1")
    assert response.status_code == 204


def test_inventory(client):
    response = client.get("/inventory/0")
    assert response.get_json() == 5
    response = client.get("/inventory")
    assert response.get_json() == [5, 5, 5]
    response = client.get("/inventory/100")
    assert response.status_code == 404


def test_purchasing(client):
    response = client.put("/inventory/1")
    assert response.headers[0] == ("X-Coins:", "0")
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/1")
    assert response.headers[0] == ("X-Coins:", "1")
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/1")
    assert response.headers[0] == ("X-Coins:", "0")
    assert response.headers[1] == ("X-Inventory-Remaining:", "4")


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
    assert response.headers[0] == ("X-Coins:", "1")
    assert response.headers[1] == ("X-Inventory-Remaining:", "0")
    response = client.put("/", json={"coin": 1})
    response = client.put("/", json={"coin": 1})
    response = client.put("/inventory/2")
    assert response.headers[0] == ("X-Coins:", "2")
    assert response.status_code == 404
