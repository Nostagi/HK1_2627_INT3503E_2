# Pagination với cursor-based

## Đề bài

Triển khai /orders có cursor pagination
Endpoint: GET /orders
    1. cursor;
    2. filter: status, customer_id;
    3. sort;
    4. sparse fieldsets.
    5. Hỗ trợ chức năng Sort

## Cấu trúc thư mục

```markdown
/lab3
├── exception.py           Exception Handler (copy từ lab2)
├── orders_api.py          Implement `/orders` với pagination    
├── orders_db.py           Database mẫu với SQLite 
├── orders_api.py          Implement `/orders` với pagination
└── README                 
```

## Kiểm thử

Giả định Flask đang chạy tại `localhost:5000` (việc khởi chạy cũng sẽ tự tạo database với dữ liệu giả).

Minh chứng chạy thử sẽ đính kèm tại tiêu đề từng mục, hoặc [tại thư mục `/figures`](./figures/).

### 1. Filter `status`

**Command**

```bash
curl -i 'localhost:5000/orders?status=paid'
```

**Kết quả mong muốn**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "data": [
    {
      "id": 2,
      "customer_id": 1001,
      "status": "paid",
      "cart": ["laptop", "mouse", "usb-c-cable"]
    }
  ],
  "next_cursor": null,
  "has_more": false
}
```

Các giá trị dữ liệu thực tế có thể khác. Cần kiểm tra rằng mọi order trong `data` đều có `status = "paid"`.

### 2. Pagination bằng `limit`

**Command**

```bash
curl -i 'localhost:5000/orders?limit=5'
```

**Kết quả mong muốn**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "data": [
    {
      "id": 1,
      "customer_id": 1000,
      "status": "pending",
      "cart": ["keyboard", "mouse"]
    },
    ...
  ],
  "next_cursor": "<CURSOR_1>",
  "has_more": true
}
```

Với database có nhiều hơn 5 order, `data` phải có đúng 5 phần tử, `has_more` phải là `true` và `next_cursor` phải khác `null`.

### 3. Sparse fieldset

Trong schema hiện tại không có trường `total`; order chỉ có `id`, `customer_id`, `status` và `cart`. Vì vậy dùng một fieldset hợp lệ:

**Command**

```bash
curl -i 'localhost:5000/orders?fields=id,customer_id'
```

**Kết quả mong muốn**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "data": [
    {
      "id": 1,
      "customer_id": 1000
    },
    {
      "id": 2,
      "customer_id": 1001
    }
  ],
  "next_cursor": "<CURSOR_1>",
  "has_more": true
}
```

Mỗi phần tử chỉ được chứa `id` và `customer_id`.

### 4. Cursor pagination

Đây là test chính.

Trước tiên lấy trang đầu:

**Command**

```bash
curl -i 'localhost:5000/orders?limit=5'
```

Giả sử response có:

```json
{
  "data": [
    {"id": 1, "customer_id": 1000, "status": "pending", "cart": ["keyboard", "mouse"]},
    {"id": 2, "customer_id": 1001, "status": "paid", "cart": ["laptop", "mouse", "usb-c-cable"]},
    {"id": 3, "customer_id": 1002, "status": "shipped", "cart": ["monitor"]},
    {"id": 4, "customer_id": 1003, "status": "cancelled", "cart": ["headset", "webcam"]},
    {"id": 5, "customer_id": 1004, "status": "pending", "cart": ["keyboard", "desk-mat"]}
  ],
  "next_cursor": "<CURSOR_1>",
  "has_more": true
}
```

Lấy giá trị thực tế của `next_cursor`, sau đó gọi:

**Command**

```bash
curl -i 'localhost:5000/orders?limit=5&cursor=<CURSOR_1>'
```

**Kết quả mong muốn**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "data": [
    {
      "id": 6,
      "customer_id": 1005,
      "status": "paid",
      "cart": ["mouse", "usb-c-cable"]
    }
  ],
  "next_cursor": "<CURSOR_2>",
  "has_more": true
}
```

Điểm cần kiểm tra là trang thứ hai tiếp tục sau order cuối của trang thứ nhất và không lặp lại các order đã trả về. Tiếp tục sử dụng `next_cursor` cho đến khi `has_more` là `false` và `next_cursor` là `null`.

### 5. Cursor kết hợp với filter

**Command trang đầu**

```bash
curl -i 'localhost:5000/orders?status=paid&limit=5'
```

Lấy `next_cursor`, sau đó:

```bash
curl -i 'localhost:5000/orders?status=paid&limit=5&cursor=<CURSOR_1>'
```

**Kết quả mong muốn**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "data": [
    {
      "id": 6,
      "customer_id": 1005,
      "status": "paid",
      "cart": ["mouse", "usb-c-cable"]
    }
  ],
  "next_cursor": "<CURSOR_2>",
  "has_more": true
}
```

Tất cả order ở mọi trang vẫn phải thỏa `status = "paid"`.

### 6. Cursor kết hợp với sort

Chỉ cần kiểm tra một kiểu sort, ví dụ `id` giảm dần.

**Command trang đầu**

```bash
curl -i 'localhost:5000/orders?limit=5&sort=-id'
```

**Kết quả mong muốn**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "data": [
    {
      "id": 50,
      "customer_id": 1001,
      "status": "paid",
      "cart": ["keyboard", "mouse"]
    },
    {
      "id": 49,
      "customer_id": 1000,
      "status": "pending",
      "cart": ["desk-mat"]
    }
  ],
  "next_cursor": "<CURSOR_1>",
  "has_more": true
}
```

Các order phải được sắp xếp `id` giảm dần. Sau đó:

```bash
curl -i 'localhost:5000/orders?limit=5&sort=-id&cursor=<CURSOR_1>'
```

Trang tiếp theo phải tiếp tục theo đúng thứ tự giảm dần và không lặp dữ liệu.

### 7. Cursor bị hỏng — phải trả 400

**Command**

```bash
curl -i 'localhost:5000/orders?limit=5&cursor=invalid-cursor'
```

**Kết quả mong muốn**

```http
HTTP/1.1 400 BAD REQUEST
Content-Type: application/problem+json
```

```json
{
  "type": "/errors/invalid-cursor",
  "title": "Invalid cursor",
  "status": 400,
  "instance": "/orders",
  "detail": "The cursor is malformed or invalid.",
  "trace_id": "..."
}
```

Điểm cần kiểm tra: không được trả `500` và không được trả HTML.

### 8. Cursor không khớp với sort

Tạo cursor với `sort=id`:

```bash
curl -i 'localhost:5000/orders?limit=5&sort=id'
```

Sau đó cố tình đổi sort khi sử dụng cursor:

```bash
curl -i 'localhost:5000/orders?limit=5&sort=-id&cursor=<CURSOR_1>'
```

**Kết quả mong muốn**

```http
HTTP/1.1 400 BAD REQUEST
Content-Type: application/problem+json
```

```json
{
  "type": "/errors/cursor-sort-mismatch",
  "title": "Invalid cursor",
  "status": 400,
  "instance": "/orders",
  "detail": "Cursor does not match the requested sort.",
  "trace_id": "..."
}
```
