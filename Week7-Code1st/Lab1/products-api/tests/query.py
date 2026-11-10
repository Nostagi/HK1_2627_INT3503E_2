
from sqlalchemy import event

from src.extensions import db
from src.models.order import Order, OrderItem


def create_orders(product, number):
    for _ in range(number):
        order = Order()

        order.items.append(
            OrderItem(
                product=product,
                quantity=1,
                unit_price_cents=product.price_cents,
            )
        )

        db.session.add(order)

    db.session.commit()


def count_select_queries(app, client, per_page):
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

    with app.app_context():
        event.listen(
            db.engine,
            "before_cursor_execute",
            before_cursor_execute,
        )

        try:
            response = client.get(
                f"/api/v1/orders/?page=1&per_page={per_page}"
            )
        finally:
            event.remove(
                db.engine,
                "before_cursor_execute",
                before_cursor_execute,
            )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)

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

    create_orders(product, 10)

    queries_for_2 = count_select_queries(
        app,
        client,
        per_page=2,
    )

    queries_for_10 = count_select_queries(
        app,
        client,
        per_page=10,
    )

    assert queries_for_2 > 0

    assert queries_for_10 <= queries_for_2 + 1, (
        "Potential N+1 detected: "
        f"2 orders = {queries_for_2} SELECT, "
        f"10 orders = {queries_for_10} SELECT"
    )
