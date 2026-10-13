# API Specification

## Bài 1. Pet-store API

Thiết kế đặc tả với Swagger Editor. Kết quả lưu [tại đây](./petstore/pestore.yaml)

## Bài 2. Tasks API

Đề bài: Tasks API phục vụ quản lý task nội bộ — title, status, priority, dueDate, assignedID

-> Danh sách endpoint: GET /tasks, POST, GET /:id, PATCH, DELETE

### Mã nguồn: [tasks](./tasks/)

### Cấu trúc thư mục

```markdown
/tasks
├── /src
│    ├── handler                # Exception Handler
│    ├── database               # SQLite tạo và seeding dữ liệu giả
│    ├── repositories           # Truy vấn 
│    ├── services
│    ├── routes                 # Khai báo endpoint và contracts
│    └── schemas                # Các Schemas được sử dụng (theo specification)
│
├── taskApi.yaml        # Specification thủ công
├── openapi.yaml        # Specification xuất từ flask_smorest
├── SwaggerUI.pdf       # Tài liệu API (đã Try it Out)
└── README                 
```

### Hướng dẫn chạy chương trình:

Sử dụng:

```terminal
python3 -m tasks.app

# Hoặc:
# Không sử dụng khi DB chưa được khởi tạo (nếu chạy lần đầu)
flask --app app run --debug
```
