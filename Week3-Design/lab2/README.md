# Error Handler chuẩn RFC 7807/9457

## Đề bài

Bài tập: viết một Flask error handler thống nhất trả về *problem+json*, kèm exception class

Gợi ý:
    1. Định nghĩa *ProblemError(Exception)*
    2. Decorator *@app.errorhandler(ProblemError)*, và một handler fallback cho HTTPException

Kiểm thử:
    - Request tới /resources/{id} phải trả 404, status code HTTP là 404.
    - Body có type/title/detail/status/instance, không lộ stack trace.
    - Nếu thiếu Accept hoặc client Accept JSON, vẫn trả *problem+json* cho lỗi API.
    - Nếu gặp exception chưa bắt, trả 500 với message trung tính và log chi tiết server-side.

## Cấu trúc thư mục

```markdown
/lab2
├── /src
│    ├── exception.py           Exception Handler (custom ApiProblem, HTTPException và Exception chưa phân loại khác)
│    └── testing_app.py         Application giả để kiểm tra văng lõi.
└── README                 
```

## Kiểm thử

Khởi chạy application:
    ```terminal
    # Nếu đang ở tại dir: [/Week3-Design]
    python3 -m "lab2.src.testing_app"
    ```
