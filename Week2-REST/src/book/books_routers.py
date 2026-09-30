from __future__ import annotations

from flask import Flask, jsonify, request, make_response

import books_services as services

app = Flask(__name__)


LOCALHOST: dict = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": True,
}

# ─── GET /books —— trả danh sách
@app.get("/books/all")
def list_books():
    all_books = services.get_all_books()
    return jsonify({
        "data": all_books,
        "total": len(all_books)
    }), 200


# ─── POST /books —— tạo mới
@app.post("/books")
def create_book():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or"").strip()
    a = (p.get("author") or"").strip()

    if not t or not a:
        return jsonify(error="title and author required"), 422
    
    book = services.create_book({
        'title': t,
        'author': a
    })

    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"
    return resp

# ─── GET /books/<id> ─── cache 60s
@app.get("/books/<int:bid>")
def fetch(bid):
    _, book = services.find_by_id(bid) 
    if book is None: 
        return jsonify(error="not found"), 404

    resp = make_response(jsonify(book), 200)
    resp.headers["Cache-Control"]="max-age=60"
    return resp

# ─── PUT /books/<id> ─── thay toàn bộ, title+author bắt buộc
@app.put("/books/<int:bid>")
def put(bid):
    i, _ = services.find_by_id(bid) 
    if i is None: 
        return jsonify(error="not found"), 404
    
    p = request.get_json(silent=True) or {}
    t,a = p.get("title"), p.get("author")

    if not t or not a: 
        return jsonify(error="need title+author"), 422
    
    new_data = services.update_book(
        i, 
        {
            "id":bid,
            "title":t.strip(),
            "author":a.strip(),
            "isbn":p.get("isbn"),
            "price":p.get("price")
        }, 
        replacement=True
    )
    return jsonify(new_data), 200

# ─── PATCH /books/<id> ─── chỉ cập nhật field có trong body
@app.patch("/books/<int:bid>")
def patch(bid):
    i, _ = services.find_by_id(bid) 
    if i is None: 
        return jsonify(error="not found"), 404
        
    p = request.get_json(silent=True) or {}
    t,a = p.get("title"), p.get("author")
    
    if not t or not a: 
        return jsonify(error="need title+author"), 422

    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422
    
    new_data = services.update_book(
        i,
        {k: p[k]
            for k in "title author isbn price".split() if k in p
        },
        replacement=False
    )
    return jsonify(new_data), 200

# ─── DELETE /books/<id> ─── idempotent, trả 204
@app.delete("/books/<int:bid>")
def delete(bid):
    i, _ = services.find_by_id(bid) 
    if i is None: 
        return jsonify(error="not found"), 404

    services.delete_book(i)
    return"", 204



# ============================================================
# PAGINATION
# ============================================================

DEFAULT_SIZE, MAX_SIZE = 20, 100

@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400
        
    page = max(page, 1); size = max(min(size, MAX_SIZE), 1)

    query = {
        "author": request.args.get("author"),
        "q": (request.args.get("q")or"").lower()
    }

    flt = services.get_book(query)

    # paginate
    total = len(flt);
    start=(page-1)*size; end=start+size
    items = flt[start:end] 
    last=(total+size-1)//size

    # HATEOAS links
    def u(p): 
        return f"/books?page={p}&size={size}"
    
    links = {
        "self":{"href":u(page)},
        "first":{"href":u(1)},
        "last":{"href":u(max(last, 1))}
        }
    
    if page > 1: 
        links["prev"]={"href":u(page-1)}
    if end < total: 
        links["next"]={"href":u(page+1)}

    body = {
        "data":items,
        "pagination":{
            "page":page,
            "size":size,
            "total":total,
            "total_pages":last},
    "_links":links}
    
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"]="public, max-age=30"
    return resp


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":
    app.run(**LOCALHOST)