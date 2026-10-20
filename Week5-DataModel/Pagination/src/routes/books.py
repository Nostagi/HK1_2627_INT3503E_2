from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
import base64
import json

from ..models import db, Book, Category

bp = Blueprint('books', __name__)

# Whitelist sort keys (Chống SQLi)
SORT_KEYS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title
}

# ---------------------------------------------------------
# HELPER 1: Parse Sort
# ---------------------------------------------------------
def parse_sort(raw_sort):
    """
    Parse chuỗi sort (VD: "-price,title") thành list order_by clauses và config cho cursor.
    Hỗ trợ multi-key sort.
    """
    if not raw_sort:
        # Mặc định sort theo id ASC
        return [Book.id.asc()], [("id", True)]

    order_by_clauses = []
    cursor_config = [] # List of tuples: (key, is_ascending)

    for item in raw_sort.split(","):
        item = item.strip()
        is_asc = not item.startswith("-")
        key = item.lstrip("-")

        if key not in SORT_KEYS:
            raise ValueError(f"Invalid sort key: {key}")

        col = SORT_KEYS[key]
        order_by_clauses.append(col.asc() if is_asc else col.desc())
        cursor_config.append((key, is_asc))

    # Tie-breaker: Đảm bảo "id" luôn là key cuối cùng để cursor không bị trùng lặp (bug sort dup)
    if not cursor_config or cursor_config[-1][0] != "id":
        # Lấy hướng của sort key cuối cùng làm hướng cho id, hoặc mặc định ASC
        last_is_asc = cursor_config[-1][1] if cursor_config else True
        order_by_clauses.append(Book.id.asc() if last_is_asc else Book.id.desc())
        cursor_config.append(("id", last_is_asc))

    return order_by_clauses, cursor_config


# ---------------------------------------------------------
# HELPER 2: Apply Cursor
# ---------------------------------------------------------
def apply_cursor(query, cursor_str, sort_config):
    """
    Áp dụng điều kiện Keyset Pagination (Cursor) vào query.
    Sử dụng logic or_ / and_ để xử lý multi-key sort với hướng trộn lẫn (VD: price DESC, title ASC).
    """
    try:
        # Decode base64 cursor
        cursor_data = json.loads(base64.b64decode(cursor_str).decode())
        cursor_values = []
        
        # Lấy giá trị từ cursor theo đúng thứ tự sort_config
        for key, _ in sort_config:
            if key not in cursor_data:
                raise ValueError("Missing key in cursor")
            cursor_values.append(cursor_data[key])
            
    except Exception:
        raise ValueError("Invalid cursor format")

    # Xây dựng điều kiện SQL tương đương: (col1 > v1) OR (col1 = v1 AND col2 > v2) ...
    conditions = []
    for i in range(len(sort_config)):
        eq_conditions = []
        
        # Các cột trước đó phải BẰNG giá trị cursor
        for j in range(i):
            key_j, _ = sort_config[j]
            col_j = SORT_KEYS[key_j]
            eq_conditions.append(col_j == cursor_values[j])

        # Cột hiện tại phải LỚN HƠN hoặc NHỎ HƠN giá trị cursor (tùy thuộc ASC/DESC)
        key_i, is_asc = sort_config[i]
        col_i = SORT_KEYS[key_i]
        val_i = cursor_values[i]
        
        op = col_i > val_i if is_asc else col_i < val_i
        conditions.append(and_(*eq_conditions, op))

    return query.filter(or_(*conditions))


# ---------------------------------------------------------
# HELPER 3: Build Response
# ---------------------------------------------------------
def build_response(books, strategy, sort_config, limit, offset=0):
    """
    Format response và tạo next_cursor nếu cần.
    """
    if strategy == 'cursor':
        # Kiểm tra xem có data cho page tiếp theo không
        has_next = len(books) > limit
        books = books[:limit] # Cắt bỏ phần tử dư thừa dùng để check
        
        next_cursor = None
        if has_next and books:
            last_book = books[-1]
            # Tạo cursor data từ cuốn sách cuối cùng
            cursor_data = {}
            for key, _ in sort_config:
                if key == 'id': cursor_data['id'] = last_book.id
                elif key == 'price': cursor_data['price'] = last_book.price_vnd
                elif key == 'title': cursor_data['title'] = last_book.title
            
            # Encode base64
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        return {
            "data": [b.to_dict() for b in books],
            "pagination": {"strategy": "cursor", "next_cursor": next_cursor}
        }
    else:
        return {
            "data": [b.to_dict() for b in books],
            "pagination": {"strategy": "offset", "offset": offset, "limit": limit}
        }


# ---------------------------------------------------------
# MAIN ROUTE
# ---------------------------------------------------------
@bp.route('', methods=['GET'])
def list_books():
    # 1. Parse Sort (Phase 1)
    try:
        order_by, sort_config = parse_sort(request.args.get('sort'))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # 2. Khởi tạo Query & Filter
    query = Book.query
    
    genre = request.args.get('genre')
    if genre:
        # Hỗ trợ filter theo ID hoặc Tên category
        if genre.isdigit():
            query = query.filter(Book.category_id == int(genre))
        else:
            query = query.join(Category).filter(Category.name.ilike(f"%{genre}%"))

    # Apply Sort
    query = query.order_by(*order_by)

    # 3. Phân trang (Pagination Strategy)
    strategy = request.args.get('strategy', 'offset')
    limit = int(request.args.get('limit', 20))

    if strategy == 'cursor':
        cursor_str = request.args.get('cursor')
        if cursor_str:
            try:
                query = apply_cursor(query, cursor_str, sort_config)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
                
        # Lấy limit + 1 để check xem còn data ở trang sau không
        books = query.limit(limit + 1).all()
        response_data = build_response(books, strategy, sort_config, limit)
    else:
        offset = int(request.args.get('offset', 0))
        books = query.offset(offset).limit(limit).all()
        response_data = build_response(books, strategy, sort_config, limit, offset)

    return jsonify(response_data), 200