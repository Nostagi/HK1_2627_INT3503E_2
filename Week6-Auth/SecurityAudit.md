# Đặc tả & Báo Cáo Bảo Mật (Security Audit)

## 1. Đặc tả hệ thống

Một mạng xã hội tối giản lấy cảm hứng từ ứng dụng Threads, chỉ phục vụ nhu cầu chia sẻ nội dung công khai.

* **Đăng bài (post):** Người dùng có thể đăng tải bài viết (Post) văn bản. Tất cả bài viết theo mặc định là **công khai (Public)**, bất kỳ ai cũng có thể đọc.
* **Phản hồi (reply):** Không có tính năng bình luận độc lập. Người dùng tương tác bằng cách tạo một Post mới trỏ tới bài gốc thông qua thuộc tính `reply_to_id`.
* **Quyền hạn (Auth & Scopes):**
  * *Người đọc (Reader):* Có thể truy cập đọc bài viết mà không cần đăng nhập (Public access).
  * *Chủ sở hữu (Owner):* Có quyền tạo bài viết mới (scope: `write:posts`). Có đặc quyền chỉnh sửa (Edit) hoặc xóa (Delete) chính bài viết của mình, nhưng không thể can thiệp vào bài của người khác.

## 2. Tài liệu API

Xem chi tiết tại: [API Specs](./API-specs.md)

* **Nhóm Auth (Xác thực):**
  * `POST /auth/login`: Xác thực người dùng và cấp phát Token.
    * **Scope:** Không yêu cầu (Public).
  * `POST /auth/refresh`: Cấp lại Access Token mới từ Refresh Token.
    * **Scope:** Không yêu cầu (Public, chỉ cần payload chứa Refresh Token hợp lệ).
* **Nhóm Posts (Bài viết):**
  * `GET /posts/{id}`: Lấy chi tiết nội dung một bài viết.
    * **Scope:** Không yêu cầu (Public - mọi người dùng đều có thể đọc bài viết công khai).
  * `POST /posts`: Tạo bài viết mới hoặc Reply bài viết khác.
    * **Scope:** Yêu cầu xác thực Access Token (có scope `write:posts`).
  * `PUT /posts/{id}`: Chỉnh sửa nội dung bài viết.
    * **Scope:** Yêu cầu xác thực Access Token (có scope `write:posts`) và bắt buộc phải thỏa mãn quyền chủ sở hữu (Ownership).
  * `DELETE /posts/{id}`: Xóa bài viết.
    * **Scope:** Yêu cầu xác thực Access Token (có scope `write:posts`) và bắt buộc phải thỏa mãn quyền chủ sở hữu (Ownership).

## 3. Báo cáo Đánh giá Bảo mật (Security Audit)

### Lỗ hổng 1: Thiếu giới hạn tốc độ (Rate Limiting) dẫn đến tấn công Brute-force

* **Điểm trên hệ thống:** Endpoint `POST /auth/login`.
* **Kịch bản xảy ra:** Kẻ tấn công sử dụng công cụ tự động gửi hàng ngàn request đăng nhập mỗi giây với các mật khẩu khác nhau (Brute-force) hoặc dùng dữ liệu rò rỉ từ nơi khác (Credential Stuffing). Do không có giới hạn, máy chủ sẽ xử lý mọi request, dẫn đến nguy cơ tài khoản bị chiếm đoạt thành công hoặc hệ thống bị quá tải.
* **Cách sửa lỗi:** Sử dụng middleware Rate Limit

### Lỗ hổng 2: Quản lý vòng đời Refresh Token/Access Token lỏng lẻo

* **Điểm trên hệ thống:** Endpoint `POST /auth/refresh` và luồng cấp phát JWT.
* **Kịch bản xảy ra:** Hệ thống cấp một Access Token có thời gian sống (exp) lên đến nhiều tháng, hoặc cấp Refresh Token nhưng không lưu trạng thái (state) trong DB. Nếu thiết bị của người dùng bị hack, kẻ xấu trộm được Token và có thể giả danh người dùng mãi mãi vì máy chủ không có cơ chế chặn/thu hồi Token đó.
* **Cách sửa lỗi:** Cần thiết lập exp ngắn cho Access Token (ví dụ: 15 phút) và duy trì Refresh Token. Đồng thời, triển khai danh sách chặn (Blocklist) cho các Token bị nghi ngờ. Khi đăng xuất hoặc phát hiện lộ lọt, hệ thống đưa ID này vào blocklist, biến Token thành vô giá trị lập tức.

### Lỗ hổng 3: Gán dữ liệu tràn lan (Broken Object Property Level Auth/Mass Assignment)

* **Điểm trên hệ thống:** Endpoint `POST /posts` hoặc `PUT /posts/{id}`.
* **Kịch bản xảy ra:** Client gửi request tạo bài viết bằng một cục JSON lớn. Nếu API map thẳng toàn bộ dữ liệu này vào CSDL mà không qua bộ lọc, hacker có thể bí mật chèn thêm các trường không mong muốn (vd: `{"content": "Hello", "views_count": 999999, "author_id": "admin-id"}`).
* **Cách sửa lỗi:** Theo OWASP API3:2023 (Broken Object Property Level Auth), tuyệt đối không "echo raw DB row". Cần áp dụng danh sách trắng (whitelist) giới hạn các trường chỉ định được phép ghi (vd: chỉ được truyền content và reply_to_id), hoặc/và serialize qua Data Transfer Object (DTO) trước khi xử lý logic.

### Lỗ hổng 4: Thiếu kiểm tra quyền sở hữu đối tượng (Broken Object Level Authorization - BOLA)

* **Điểm trên hệ thống:** Endpoint `DELETE /posts/{id}` hoặc `PUT /posts/{id}`.
* **Kịch bản xảy ra:** Một tài khoản thường (User A) đăng nhập hợp lệ và được cấp Access Token có scope write:posts. User A phân tích API và gọi lệnh `DELETE /posts/` ID_CỦA_USER_B. Nếu backend chỉ kiểm tra xem Token có hiệu lực hay không mà không kiểm tra ai là chủ bài viết, bài viết của User B sẽ bị xóa oan.
* **Cách sửa lỗi:** Lỗ hổng kinh điển Broken Object Level Authorization (BOLA) thuộc OWASP API1:2023. Cách khắc phục là áp dụng 3 lớp check: AuthN -> AuthZ scope -> Ownership. Bắt buộc viết các decorator (ví dụ: `@user_owns_resource`) để kiểm tra owner_id của record trong Database có khớp với id của user đang gửi request hay không trước khi thực thi thao tác sửa/xóa.

### Lỗ hổng 5: Bypass xác thực do cấu hình thuật toán JWT sai

* **Điểm trên hệ thống:** Các middleware bảo vệ API yêu cầu xác thực (`jwt_required()` check tại `POST /posts`).
* **Kịch bản xảy ra:** Token ban đầu được ký bằng `HS256`. Kẻ tấn công sửa đổi phần Header của JWT thành {"alg": "none"}, giữ nguyên phần Payload đóng giả người dùng khác, và xóa bỏ phần chữ ký (Signature). Hoặc kịch bản xác thực chéo từ một PUBLIC KEY thay vì PRIVATE KEY đúng quy trình. Nếu thư viện xác minh của hệ thống tin tưởng một cách mù quáng vào khai báo của Header, nó sẽ bỏ qua bước check chữ ký và chấp nhận Token giả mạo.
* **Cách sửa lỗi:** Để tránh trường hợp xảy ra "Algorithm confusion", phải luôn luôn đối chiếu `alg` trên token với danh sách allowlist (thuật toán được cấu hình tin cậy) trong lúc verify. Không sử dụng chung secret cho nhiều loại mã hóa và sử dụng các thư viện uy tín được duy trì tốt.
