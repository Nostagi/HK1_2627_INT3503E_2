from __future__ import annotations

from flask import Flask, jsonify, request
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


app = Flask(__name__)


LOCALHOST: dict = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": True,
}
BOOKS: list[dict] = [
    {
        "id": 0,
        "title": "Clean Code",
        "author": "R. Martin",
        "year": 2008,
    },
    {
        "id": 1,
        "title": "API Design Patterns",
        "author": "JJ. Geewax",
        "year": None,
    },
    {
        "id": 2,
        "title": "Principles of Web API Design",
        "author": "J. Higginbotham",
        "year": 2022,
    },
]

_next = len(BOOKS)


# ============================================================
# PYDANTIC MODELS
# ============================================================

class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    year: int | None = Field(default=None, ge=1900)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    author: str | None = Field(default=None, min_length=1)
    year: int | None = Field(default=None, ge=1900)


class BookListQuery(BaseModel):
    search: str | None = None

    sort_by: Literal["id", "title", "author", "year"] = "id"

    order: Literal["asc", "desc"] = "asc"

    limit: int = Field(default=2, ge=1, le=100)


# ============================================================
# ROUTING LAYER
# ============================================================

@app.route("/books", methods=["GET"])
def list_books():
    try:
        query = BookListQuery(
            search=request.args.get("search"),
            sort_by=request.args.get("sort_by", "id"),
            order=request.args.get("order", "asc"),
            limit=request.args.get("limit", 2),
        )
    except ValueError as e:
        return {"error": "invalid query parameters", "details": str(e)}, 400

    books = get_books(query)

    return jsonify(books), 200


@app.route("/books/<int:bid>", methods=["GET"])
def get_book_route(bid: int):
    book = get_book(bid)

    if book is None:
        return {"error": "not found"}, 404

    return jsonify(book), 200


@app.route("/books", methods=["POST"])
def create_book_route():
    body = request.get_json(silent=True) or {}

    try:
        data = BookCreate.model_validate(body)
    except ValueError as e:
        return {"error": "validation error", "details": str(e)}, 400

    book = create_book(data)

    return (
        jsonify(book),
        201,
        {"Location": f"/books/{book['id']}"},
    )


@app.route("/books/<int:bid>", methods=["PUT"])
def update_book_route(bid: int):
    book = get_book(bid)

    if book is None:
        return {"error": "not found"}, 404

    body = request.get_json(silent=True) or {}

    try:
        data = BookUpdate.model_validate(body)
    except ValueError as e:
        return {"error": "validation error", "details": str(e)}, 400

    updated = update_book(bid, data)

    return jsonify(updated), 200


@app.route("/books/<int:bid>", methods=["DELETE"])
def delete_book_route(bid: int):
    book = get_book(bid)

    if book is None:
        return {"error": "not found"}, 404

    delete_book(bid)

    return "", 204


# ============================================================
# SERVICE LAYER
# ============================================================

def find_book(bid: int) -> dict | None:
    return next(
        (book for book in BOOKS if book["id"] == bid),
        None,
    )


def get_books(query: BookListQuery) -> list[dict]:
    books = BOOKS.copy()

    # ----------------------------
    # Search
    # ----------------------------

    if query.search:
        keyword = query.search.lower()

        books = [
            book
            for book in books
            if keyword in book["title"].lower()
            or keyword in book["author"].lower()
        ]

    # ----------------------------
    # Sort
    # ----------------------------

    reverse = query.order == "desc"

    if query.sort_by == "year":
        # Books without year are placed at the end.
        books.sort(
            key=lambda book: (
                book["year"] is None,
                book["year"] if book["year"] is not None else 0,
            ),
            reverse=reverse,
        )
    else:
        books.sort(
            key=lambda book: book[query.sort_by],
            reverse=reverse,
        )

    # ----------------------------
    # Limit
    # ----------------------------

    return books[:query.limit]


def get_book(bid: int) -> dict | None:
    return find_book(bid)


def create_book(data: BookCreate) -> dict:
    global _next

    book = {
        "id": _next,
        "title": data.title,
        "author": data.author,
        "year": data.year,
    }

    _next += 1
    BOOKS.append(book)

    return book


def update_book(bid: int, data: BookUpdate) -> dict:
    book = find_book(bid)

    if book is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    book.update(update_data)

    return book


def delete_book(bid: int) -> None:
    book = find_book(bid)

    if book is not None:
        BOOKS.remove(book)


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":
    app.run(**LOCALHOST)