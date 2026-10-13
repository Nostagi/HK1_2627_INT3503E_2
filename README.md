# Kiến trúc hướng dịch vụ

Repository lưu trữ các bài thực hành và bài tập của môn **Kiến trúc hướng dịch vụ (Service-Oriented Architecture)**.

- **Thực hiện bởi:** Nguyễn Trường Sơn
- **Mã sinh viên:** 23021686
- **Mã học phần:** HKI_2627_INT3505E_2

## Danh sách bài tập

| Tuần   | Nội dung                 | Thư mục                                               |
| ------ | -------------------------| ------------------------------------------------------|
| Tuần 1 | Flask                    | [`Week 1: Get into Flask`](./Week1-Flask)             |
| Tuần 2 | REST                     | [`Week 2: REST`](./Week2-REST)                        |
| Tuần 3 | REST Design              | [`Week 3: REST API Design`](./Week3-Design)           |
| Tuần 4 | REST API Specification   | [`Week 4: REST API Specification`](./Week4-Swagger/)  |

## Hướng dẫn cài đặt

### Khởi chạy trên Linux / macOS

    ``` terminal
    # Tạo môi trường ảo
    python3 -m venv .venv
    source .venv/bin/activate

    # Di chuyển tới demo 
    # Tùy chỉnh lại theo tên thư mục cần chạy. Ví dụ với Week 1:
    cd "Week1-Flask"        

    # Cài đặt dependencies yêu cầu của thư mực đó
    pip install -r requirements.txt
    ```

### Thực hiện chạy server

    ```terminal
    # Khởi chạy application
    python3 -m '<tên file>'

    ```

Các server mặc định chạy tại: [http://127.0.0.1:5000] hay localhost:5000.

### Thực hiện testing

Mỗi folder từng tuần sẽ cung cấp đi kèm command được sử dụng cho việc kiểm thử hoạt động. Hãy mở một tab terminal khác với tab ban đầu (đang chạy application phía trên), và paste command cần chạy để tạo request tương ứng.
