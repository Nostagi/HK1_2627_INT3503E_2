
import pytest

from app import create_app
from src.extensions import db

from src.models.product import Product
from src.models.order import Order, OrderItem

from src.handlers.config import DefaultConfig


class TestConfig(DefaultConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def product_factory():
    def create_product(
        sku="TEST-001",
        name="Test Product",
        description="Product for testing",
        category="Electronics",
        price_cents=10000,
        qty_in_stock=20,
        archived=False,
    ):
        product = Product(
            sku=sku,
            name=name,
            description=description,
            category=category,
            price_cents=price_cents,
            qty_in_stock=qty_in_stock,
            archived=archived,
        )

        db.session.add(product)
        db.session.commit()

        return product

    return create_product


@pytest.fixture
def sample_product(app, product_factory):
    return product_factory()
