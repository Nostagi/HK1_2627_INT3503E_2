"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

from jsonschema import validate, ValidationError
import pytest
from tools import get_book_schema


def test_empty_database(client):
    # --- ARRANGE: pre-condition ---

    # --- ACT ---
    response = client.get("/books")

    # --- ASSERT ---
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_nonexistent_book(client):
    # --- ARRANGE: pre-condition ---

    # --- ACT ---
    response = client.get("/books/9999")

    # --- ASSERT ---
    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"

def test_post_book_missing_title(client):
    # --- ARRANGE: pre-condition ---

    # --- ACT ---
    response = client.post("/books", json={"author": "Kleppmann"})

    # --- ASSERT ---
    assert response.status_code == 400
    assert response.get_json()["code"] == "VALIDATION_ERROR"
    assert "title" in response.get_json()["errors"][0]["field"]

def test_deleted_book_is_gone(client):
    # --- ARRANGE: pre-condition ---
    created = client.post(
        "/books",
        json={
            "title": "DDIA", ""
            "author": "Kleppmann", 
            "year": 2017
            })
    assert created.status_code == 201          # chốt pre-condition đã thật sự được tạo
    book_id = created.get_json()["id"]

    assert client.get(f"/books/{book_id}").status_code == 200  # sách đang tồn tại

    # --- ACT ---
    deleted = client.delete(f"/books/{book_id}")

    # --- ASSERT ---
    assert deleted.status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404
