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

@app.get("users/<uid>")
def get_user_profile(uid):
    pass

@app.get("users/<uid>/followers")
def list_followers(uid):
    """
    Lấy danh sách followers của một user được cấp (uid)
    """

@app.get("users/<uid>/following")
def list_following(uid):
    """
    Lấy danh sách following của một user được cấp (uid) (những người được user này theo dõi)
    """

@app.get("tags")
def list_tags():
    """
    Endpoint lấy danh sách các tags.
    """
    pass

@app.get("comments/<cid>")
def get_comment(cid):
    """
    Endpoint lấy nội dung một comment cụ thể
    """
    pass

@app.get("users/<uid>/comments")
def list_users_comments(user_id):
    """
    Endpoint lấy danh sách comments của 1 user
    """
    pass

@app.get("tags/<tag_name>/comments")
def list_tag_comments(tag_name):
    """
    Endpoint lấy danh sách comments của 1 tag
    """
    pass

@đataclass
class ProblemError(Exception):
    exception:Exception
    httpStatus:int
    message: str

@app.errorhandler(ProblemError)
def handle_problem_error(error:ProblemError):
    response = {
        "status": error.httpStatus,
        "message": error.message,
        "instance": request.path
    }
    # Trả về đúng chuẩn problem+json
    return jsonify(response), error.status, {'Content-Type': 'application/problem+json'}

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = {
        "status": error.code,
        "message": error.description,
        "instance": request.path
    }
    return jsonify(response), error.code, {'Content-Type': 'application/problem+json'}

@app.errorhandler(Exception)
def handle_generic_exception(error):
    # Trả về message trung tính cho client, không lộ stack trace
    response = {
        "status": 500,
        "message": "Đã có lỗi hệ thống xảy ra. Vui lòng thử lại sau.",
        "instance": request.path
    }
    return jsonify(response), 500, {'Content-Type': 'application/problem+json'}


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":
    app.run(**LOCALHOST)