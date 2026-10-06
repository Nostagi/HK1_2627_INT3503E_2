# WEEK 3: API Design Principles and Best Practices

## [Lab 1](./lab1/): Thiết kế resource cho Blog API

## [Lab 2](./lab2/): Error handler

## [Lab 3](./lab3/): Cursor pagination

## Vận dụng: review một public API

### Danh sách 9 tiêu chí Review API

Case study được thực hiện với: **Stripe API**

### Giới thiệu về Stripe API

Stripe API là một RESTful API được tổ chức chặt chẽ, cho phép các nhà phát triển tích hợp các giải pháp thanh toán, quản lý khách hàng và vận hành các mô hình kinh doanh định kỳ vào ứng dụng của họ.

Base URL: [https://api.stripe.com](https://api.stripe.com)

Định dạng dữ liệu:
    - Request dạng application/x-www-form-urlencoded
    - Response dạng JSON.

Hiện tồn tại 2 version:
    - API v1 (/v1): Chứa hầu hết các endpoint hiện có của Stripe, phục vụ hầu hết các nghiệp vụ thanh toán, khách hàng, subscription.
    - API v2 (/v2): Chứa các endpoint sử dụng các mẫu thiết kế mới hơn, thường dành cho các tính năng nâng cao như quản lý tài khoản, cấu hình người dùng, v.v
Trong bài này thì ta sẽ chỉ tập trung vào version 1 (v1).

Sơ đồ Endpoint (một số thành phần tiêu biểu):

    ```markdown
    /v1
     ├── /customers
     │       ├── GET                     → Liệt kê danh sách khách hàng
     │       │    └── GET /search?query               → Tìm kiếm khách hàng theo các tiêu chí
     │       ├── POST                    → Tạo một khách hàng mới
     │       ├── GET /{id}               → Lấy thông tin (profile) một khách hàng
     │       ├── POST /{id}              → Cập nhật thông tin khách hàng
     │       └── DELETE /{id}            → Xóa vĩnh viễn một khách hàng
     │
     ├── /payment_intents
     │       ├── POST                    → Tạo một PaymentIntent mới
     │       ├── GET                     → Liệt kê các PaymentIntent
     │       ├── GET /{intent_id}        → Truy xuất một PaymentIntent
     │       └── POST /{intent_id}       → Cập nhật một PaymentIntent
     │            ├── POST /{intent_id}/confirm       → Xác nhận thanh toán
     │            ├── POST /{intent_id}/capture       → Capture (nếu dùng manual capture)
     │            └── POST /{intent_id}/cancel        → Hủy PaymentIntent
     │
     └── /subcriptions
             ├── GET                     → Liệt kê các subscription
             │   └── GET /search?query               → Tìm kiếm subscription
             ├── POST                    → Tạo subscription mới
             ├── GET /{sub_id}           → Truy xuất một subscription
             ├── POST /{sub_id}          → Cập nhật subscription
             │   └── POST /{sub_id}/resume           → Tiếp tục subscription đã tạm dừng
             └── DELETE /{sub_id}        → Hủy subscription
    ```

### 1. *Tài nguyên là danh từ*

URLs chỉ chứa danh từ, không chứa động từ. Hành động được diễn đạt thông qua HTTP Method (GET, POST, PUT, DELETE...).

**Đánh giá**: Đạt.
Như sơ đồ endpoint ta cũng có thể thấy, các resource (ví dụ: customers, payment_intents, subcriptions,...) đều mô tả bằng danh từ số nhiều (Collections), và định danh item bằng `id` bổ sung trong endpoint.

### 2. *Naming nhất quán*

Sử dụng lowercase, kebab-case cho path; snake_case cho query; dùng dạng số nhiều (plurals) cho collection (ví dụ: /users thay vì /user).

**Đánh giá**: Nhất quán, nhưng theo convention khác.
Các endpoint đều được lower-case và duy trì xuyên suốt mô tả Collection bằng danh từ số nhiều. Việc truy cập item (số ít) thực hiện phải thông qua bổ sung `<id>`. Tuy nhiên, họ sử dụng *Snake_case* thay vì *Kebab-case* cho path (ví dụ: payment_intents), nhưng các endpoint trong hệ thống vẫn thống nhất theo quy ước riêng đó.  

### 3. *Status code đúng nghĩa*

Mỗi response phải trả về HTTP status code phù hợp. Tuyệt đối không trả về 200 OK kèm theo lỗi trong body.

**Đánh giá**: Tốt
Stripe sử dụng standard HTTP status codes một cách chính xác. Ví dụ:
    - 200 OK – Request thành công.
    - 201 Created – Tạo mới thành công.
    - 400 Bad Request – Lỗi validation, thiếu tham số.
    - 402 Payment Required – Thẻ bị từ chối.

Stripe cũng không trả về 200 OK kèm lỗi trong body. Khi có lỗi, status code sẽ là 4xx hoặc 5xx tương ứng.

### 4. *Idempotency rõ ràng*

POST cần có Idempotency-Key. PUT/DELETE phải đảm bảo tính idempotent (gọi nhiều lần kết quả vẫn giống nhau). Cần tài liệu hóa rõ ràng.

**Đánh giá**: Mạnh mẽ và rõ ràng:

Tất cả POST requests đều chấp nhận header Idempotency-Key (tối đa 255 ký tự). Key này sẽ được lưu trữ ít nhất 24 giờ. Nếu cùng key được gửi lại với cùng body, Stripe trả về kết quả của request gốc mà không thực hiện lại nghiệp vụ. Stripe khuyến nghị thêm idempotency-key cho mọi POST request, đặc biệt là các request tạo thanh toán (POST /v1/charges, POST /v1/payment_intents).

### 5. *Error response có cấu trúc*

Tuân thủ chuẩn RFC 7807 (problem+json). Cấu trúc lỗi nhất quán, bao gồm các trường: type, title, detail, instance.

**Đánh giá**: Rõ ràng, khác tiêu chuẩn

Stripe trả về error response với cấu trúc nhất quán, bao gồm các trường sau:

| Trường            | Mô tả                                                             |
| ------            | -------------                                                     |
| type	            | Loại lỗi (ví dụ: card_error, invalid_request_error, api_error)    |
| code	            | Mã lỗi cụ thể (ví dụ: card_declined, parameter_missing)           |
| message           |	Mô tả lỗi dạng human-readable                                   |
| param	            | Tham số gây lỗi (nếu có)                                          |
| doc_url           |	Link đến documentation của Stripe cho mã lỗi đó                 |
| request_log_url   |	Link đến dashboard để xem log chi tiết                          |

Mặc dù cấu trúc rõ ràng như vậy, Stripe sử dụng format riêng (không có application/problem+json media type theo RFC 7807).

### 6. *Pagination rõ ràng*

Mọi collection đều phải có phân trang (cursor hoặc offset). Phải có giới hạn trên (max limit) cho mỗi page.

**Đánh giá**: Chuẩn hóa

Stripe sử dụng cursor-based pagination cho tất cả các list API:

Parameters:
    - limit – Số lượng object trả về (mặc định 10, tối đa 100).
    - starting_after – Cursor để lấy trang tiếp theo (object ID).
    - ending_before – Cursor để lấy trang trước đó.

Định dạng response:
    ```json
    {
        "object": "list",
        "url": "/v1/customers",
        "has_more": true,
        "data": [...]
    }
    ```

### 7. *Filter/Sort đa dạng*

Hỗ trợ lọc (filter) theo các field chính, sắp xếp (sort) theo nhiều field, và hỗ trợ sparse fieldsets (chỉ lấy các field cần thiết).

**Đánh giá**: Vừa đủ

Stripe hỗ trợ filtering và sorting khá linh hoạt trên các list endpoints. Nhưng không hỗ trựo *custom sort field* và *sparse fieldsets*. Ít nhất thì hạn chế này vẫn tồn tại hết v1, và được cải thiện dần ở v2.

### 8. *Authentication & security*

Token phải nằm ở header (không lộ qua URL). Có cơ chế Rate limit rõ ràng.

**Đánh giá**: Cực mạnh

Stripe xác thực thông qua API key (Secret Key) truyền qua header. Hỗ trợ đầy đủ Publishable Key, Restricted Key, Rate Limit và cả Webhook (hỗ trợ cho chữ ký số).

### 9. *Versioning + deprecation*

Có tiền tố version ngay từ đầu (ví dụ: /v1/). Có lộ trình rõ ràng cho việc ngừng hỗ trợ (deprecation) các phiên bản cũ.

**Đánh giá**: Tốt, chuyên nghiệp

Stripe có chính sách versioning rất chặt chẽ và rõ ràng. Không chỉ áp dụng v1 và v2 trên path endpoint, mà còn cần khai báo bổ sung thêm Version header (Mọi request có thể chỉ định Stripe-Version). Policy của họ nói rằng API sẽ được cập nhật version hàng tháng, không có breaking change đột ngột. Và Deprecations được thông báo trong changelog và có lộ trình rõ ràng, nhưng sau đó vẫn tiếp tục hỗ trợ các phiên bản cũ đó.
