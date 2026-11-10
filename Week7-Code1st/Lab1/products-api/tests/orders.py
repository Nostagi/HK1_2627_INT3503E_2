
from sqlalchemy import event

from src.extensions import db
from src.models.order import Order, OrderItem


def create_order(product, quantity=2):
    order = Order()

    order.items.append(
        OrderItem(
            product=product,
            quantity=quantity,
            unit_price_cents=product.price_cents,
        )
    )

    db.session.add(order)
    db.session.commit()

    return order


# --------------------------------------------------
# POST /api/v1/orders/
# --------------------------------------------------

def test_create_order_success(
    client,
    sample_product,
):
    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": sample_product.id,
                    "quantity": 2,
                }
            ]
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["created_at"] is not None
    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["id"] is not None
    assert item["order_id"] == data["id"]
    assert item["product_id"] == sample_product.id
    assert item["quantity"] == 2
    assert item["unit_price_cents"] == sample_product.price_cents


def test_create_order_multiple_items(
    client,
    product_factory,
):
    product_1 = product_factory(
        sku="ORDER-001",
        price_cents=10000,
    )

    product_2 = product_factory(
        sku="ORDER-002",
        price_cents=20000,
    )

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_1.id,
                    "quantity": 2,
                },
                {
                    "product_id": product_2.id,
                    "quantity": 3,
                },
            ]
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert len(data["items"]) == 2

    items = {
        item["product_id"]: item
        for item in data["items"]
    }

    assert items[product_1.id]["unit_price_cents"] == 10000
    assert items[product_2.id]["unit_price_cents"] == 20000


def test_create_order_product_not_found(client):
    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 1,
                }
            ]
        },
    )

    assert response.status_code == 404


def test_create_order_archived_product(
    client,
    product_factory,
):
    product = product_factory(
        sku="ARCHIVED-001",
        archived=True,
    )

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 1,
                }
            ]
        },
    )

    assert response.status_code == 409


# --------------------------------------------------
# GET /api/v1/orders/
# --------------------------------------------------

def test_get_orders_success(
    client,
    sample_product,
):
    create_order(sample_product, quantity=2)
    create_order(sample_product, quantity=3)

    response = client.get("/api/v1/orders/")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 2

    for order in data:
        assert order["id"] is not None
        assert order["created_at"] is not None
        assert isinstance(order["items"], list)

        for item in order["items"]:
            assert item["id"] is not None
            assert item["order_id"] == order["id"]
            assert item["product_id"] == sample_product.id
            assert item["quantity"] > 0
            assert item["unit_price_cents"] >= 0


def test_get_orders_pagination(
    client,
    sample_product,
):
    for _ in range(5):
        create_order(sample_product)

    response = client.get(
        "/api/v1/orders/?page=1&per_page=2"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2

    assert response.headers["X-Total-Count"] == "5"
    assert response.headers["X-Page"] == "1"
    assert response.headers["X-Per-Page"] == "2"
    assert response.headers["X-Total-Pages"] == "3"


# --------------------------------------------------
# GET /api/v1/orders/<order_id>
# --------------------------------------------------

def test_get_order_by_id(
    client,
    sample_product,
):
    order = create_order(sample_product, quantity=4)

    response = client.get(
        f"/api/v1/orders/{order.id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == order.id
    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["order_id"] == order.id
    assert item["product_id"] == sample_product.id
    assert item["quantity"] == 4


def test_get_order_not_found(client):
    response = client.get(
        "/api/v1/orders/999999"
    )

    assert response.status_code == 404


# --------------------------------------------------
# DELETE /api/v1/orders/<order_id>
# --------------------------------------------------

def test_delete_order_success(
    client,
    sample_product,
):
    order = create_order(sample_product)

    order_id = order.id

    response = client.delete(
        f"/api/v1/orders/{order_id}"
    )

    assert response.status_code == 204
    assert response.data == b""

    assert db.session.get(Order, order_id) is None

    remaining_items = db.session.scalars(
        db.select(OrderItem).where(
            OrderItem.order_id == order_id
        )
    ).all()

    assert remaining_items == []


def test_delete_order_not_found(client):
    response = client.delete(
        "/api/v1/orders/999999"
    )

    assert response.status_code == 404


# --------------------------------------------------
# N+1 QUERY TEST
# --------------------------------------------------

def count_select_queries(client, per_page):
    queries = []

    def before_cursor_execute(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ):
        if statement.lstrip().upper().startswith("SELECT"):
            queries.append(statement)

    engine = db.engine

    event.listen(
        engine,
        "before_cursor_execute",
        before_cursor_execute,
    )

    try:
        response = client.get(
            f"/api/v1/orders/?page=1&per_page={per_page}"
        )
    finally:
        event.remove(
            engine,
            "before_cursor_execute",
            before_cursor_execute,
        )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == per_page

    # Đảm bảo response thực sự serialize relationship items.
    assert all(order["items"] for order in data)

    return len(queries)


def test_orders_eager_loading_prevents_n_plus_one(
    app,
    client,
    product_factory,
):
    product = product_factory(
        sku="NPLUS-001",
        name="N+1 Test Product",
    )

    for _ in range(10):
        create_order(product)

    queries_for_2 = count_select_queries(
        client,
        per_page=2,
    )

    queries_for_10 = count_select_queries(
        client,
        per_page=10,
    )

    assert queries_for_2 > 0

    assert queries_for_10 <= queries_for_2 + 1, (
        "Potential N+1 detected: "
        f"2 orders = {queries_for_2} SELECT, "
        f"10 orders = {queries_for_10} SELECT"
    )
