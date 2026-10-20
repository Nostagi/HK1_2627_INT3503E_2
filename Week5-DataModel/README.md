# Data Model

## Bài 1. Thiết kế Library API

Thiết kế sơ bộ data model cho API quản lý thư viện/sách online. Nội dung [tại đây](./LibraryAPI/README.md)

## Bài 2. Pagination

Implement một BookAPI đơn giản và áp dụng sort và pagination (theo 2 chiến lược: offset và cursor).

-> Danh sách endpoint: GET /tasks, POST, GET /:id, PATCH, DELETE

### Mã nguồn: [tasks](./tasks/)

### Cấu trúc thư mục

```markdown
/tasks
├── /src
│    ├── app.py                 # Khởi chạy application tại đây
│    ├── models.py              # Database entities model và seed dữ liệu giả
│    ├── /schemas               # Mô tả entity được sử dụng (json) 
│    └── /routes                # Endpoint và logic phân trang
│
└── Pagination.postman_collection.json          # Postman Collection được sử dụng cho testing (Export từ Postman)
             
```

### Hướng dẫn chạy chương trình

Sử dụng:

```terminal
# Di chuyển tới thư mục chứa mã nguồn
cd "Week5-DataModel/Pagination"

# Khởi chạy (trên Linux) kèm khởi tạo DB
python3 -m src.app

```
