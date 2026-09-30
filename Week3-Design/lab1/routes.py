from __future__ import annotations

from flask import Flask, jsonify, request, make_response

import _ as services

app = Flask(__name__)


LOCALHOST: dict = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": True,
}

# ============================================================
# PAGINATION
# ============================================================

DEFAULT_SIZE, MAX_SIZE = 20, 100

@app.get("/users")
def list_users():
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

    flt = services.get_user(query)

    # paginate
    total = len(flt);
    start=(page-1)*size; end=start+size
    items = flt[start:end] 
    last=(total+size-1)//size

    
    resp = make_response(jsonify({
        "items": items,
        "pages": page,
        "last": last
    }), 200)
    resp.headers["Cache-Control"]="public, max-age=30"
    return resp




# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":
    app.run(**LOCALHOST)