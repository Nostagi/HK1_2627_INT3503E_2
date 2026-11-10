
from src.extensions import db
from src.models.product import Product


def test_create_product_success(client):
    payload = {
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "Product for testing",
        "category": "Electronics",
        "price_cents": 10000,
        "qty_in_stock": 20,
    }

    response = client.post(
        "/api/v1/products/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["sku"] == payload["sku"]
    assert data["name"] == payload["name"]
    assert data["category"] == payload["category"]
    assert data["price_cents"] == payload["price_cents"]
    assert data["qty_in_stock"] == payload["qty_in_stock"]
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    product = db.session.scalar(
        db.select(Product).where(
            Product.sku == payload["sku"]
        )
    )

    assert product is not None


def test_get_products_success(
    client,
    product_factory,
):
    product_factory(sku="TEST-001", name="Product One")
    product_factory(sku="TEST-002", name="Product Two")

    response = client.get("/api/v1/products/")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 2

    for product in data:
        assert product["id"] is not None
        assert product["sku"] is not None
        assert product["name"] is not None
        assert product["category"] is not None
        assert product["price_cents"] >= 0
        assert product["qty_in_stock"] >= 0
        assert product["created_at"] is not None
        assert product["updated_at"] is not None


def test_get_products_pagination(
    client,
    product_factory,
):
    for index in range(5):
        product_factory(
            sku=f"PAGE-{index:03d}",
            name=f"Product {index}",
        )

    response = client.get(
        "/api/v1/products/?page=1&per_page=2"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 2


def test_get_products_filter_by_category(
    client,
    product_factory,
):
    product_factory(
        sku="ELEC-001",
        category="Electronics",
    )

    product_factory(
        sku="BOOK-001",
        category="Books",
    )

    response = client.get(
        "/api/v1/products/?category=Electronics"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["category"] == "Electronics"


def test_get_products_search(
    client,
    product_factory,
):
    product_factory(
        sku="PHONE-001",
        name="Samsung Phone",
    )

    product_factory(
        sku="BOOK-001",
        name="Python Book",
    )

    response = client.get(
        "/api/v1/products/?q=Samsung"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert "Samsung" in data[0]["name"]


def test_get_product_by_id(
    client,
    sample_product,
):
    response = client.get(
        f"/api/v1/products/{sample_product.id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == sample_product.id
    assert data["sku"] == sample_product.sku
    assert data["name"] == sample_product.name


def test_get_product_not_found(client):
    response = client.get(
        "/api/v1/products/999999"
    )

    assert response.status_code == 404


def test_update_product_success(
    client,
    sample_product,
):
    payload = {
        "name": "Updated Product",
        "price_cents": 15000,
        "qty_in_stock": 50,
    }

    response = client.patch(
        f"/api/v1/products/{sample_product.id}",
        json=payload,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == sample_product.id
    assert data["name"] == "Updated Product"
    assert data["price_cents"] == 15000
    assert data["qty_in_stock"] == 50


def test_delete_product_success(
    client,
    sample_product,
):
    product_id = sample_product.id

    response = client.delete(
        f"/api/v1/products/{product_id}"
    )

    assert response.status_code == 204
    assert response.data == b""

    product = db.session.get(Product, product_id)

    assert product is None


def test_delete_product_not_found(client):
    response = client.delete(
        "/api/v1/products/999999"
    )

    assert response.status_code == 404
