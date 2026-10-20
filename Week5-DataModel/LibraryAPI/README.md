# Thiết kế API Nghiệp vụ Thư viện số (Library API Design)

## 1. Mô tả sơ bộ nghiệp vụ

**Bối cảnh:**

Hệ thống là một nền tảng thư viện số, cho phép người dùng tìm kiếm, đọc sách trực tuyến và thực hiện các giao dịch mượn/trả tài liệu số (theo chương hoặc theo sách).

Người dùng (`User`) sẽ thực hiện tạo yêu cầu mượn (`Requests`) có liên kết trực tiếp đến từng chương sách (`Chapters`) thay vì toàn bộ quyển sách (`Book`).

Và người dùng (`User`) có thể viết đánh giá (`Review`) cho cả toàn bộ quyển sách (`Book`), hoặc chương (`Chapter`), thậm chí phản hồi lại đánh giá khác (`Review`) (thông qua `TargetType` và `TargetID`).

**Các tác nhân (actor) chính:**

* **User (Độc giả):** Đăng ký tài khoản, tìm kiếm sách, quản lý danh sách đọc, đọc các chương sách, gửi yêu cầu mượn, gia hạn, trả sách và viết đánh giá (review).

* **Quản lý (Admin/Moderator):** Quản lý trạng thái yêu cầu (Requests), tính toán thời gian hết hạn (Expiration), tính phí (Fee).

**Các luồng nghiệp vụ:**

1. **Duyệt & Đọc:** Người dùng tìm kiếm sách (`SearchBooks`), xem sách mới (`NewFeed`), xem lại sách vừa truy cập (`Recent`). Khi xem một cuốn sách, người dùng có thể xem danh sách chương và đọc nội dung từng chương (`Read`).
2. **Mượn & Trả:**

    * Người dùng tạo yêu cầu mượn (`Request`). Hệ thống ghi nhận `IssueDate`, tính toán `Expiration` (ngày hết hạn) và `Fee` (nếu có).
    * Người dùng có thể **Gia hạn (Renew)** để kéo dài thời gian mượn nếu chưa quá hạn.
    * Người dùng có thể **Trả sách (Return)**, giải phóng quyền truy cập.

3. **Tương tác:** Người dùng viết đánh giá (Reviews). Hệ thống hỗ trợ đa hình (polymorphic) cho phép review nhắm vào `Book` hoặc `Chapter`, và tương tác giữa các bình luận.

**Entity-Relationship Diagram (ERD):**
![Library API ERD](./Thiết%20kế%20API%20-%20Library.drawio.png)

---

## 2. Danh sách Endpoint (Resource Set)

| STT | Method | Endpoint | Mô tả | Tags |
|:---|:---|:---|:---|:---|
| 1 | `POST` | `/user` | **Registry**: Đăng ký tài khoản người dùng mới. | User |
| 2 | `GET` | `/user/{username}` | Lấy thông tin cá nhân của người dùng. | User |
| 3 | `GET` | `/books` | **SearchBooks**: Tìm kiếm sách (hỗ trợ query params như `?query=...`). | Browse |
| 4 | `GET` | `/books/newFeed` | Lấy danh sách các sách mới xuất bản/cập nhật. | Browse |
| 5 | `GET` | `/books/recent` | Lấy danh sách các sách người dùng vừa truy cập gần đây. | Browse |
| 6 | `GET` | `/books/{bid}` | Lấy thông tin chi tiết của một cuốn sách (bao gồm metadata và danh mục chương). | Book/Chapter |
| 7 | `GET` | `/books/{bid}/chapters` | Lấy danh sách toàn bộ chương của một cuốn sách. | Book/Chapter |
| 8 | `GET` | `/books/{bid}/chapters/{cid}` | Lấy nội dung chi tiết của một chương (yêu cầu quyền truy cập hợp lệ). | Book/Chapter |
| 9 | `POST` | `/request/make` | Tạo yêu cầu mượn sách/chương mới. | Request |
| 10 | `GET` | `/request/{rid}` | Lấy thông tin chi tiết của một yêu cầu mượn (trạng thái, ngày hết hạn, phí). | Request |
| 11 | `POST` | `/request/{rid}` | Cập nhật thông tin yêu cầu (dùng để thay đổi trạng thái nếu cần thiết). | Request |
| 12 | `POST` | `/request/{rid}/return` | **Return**: Trả sách/chương (kết thúc giao dịch mượn sớm). | Request |
| 13 | `POST` | `/request/{rid}/renew` | **Renew**: Gia hạn thời gian mượn. | Request |
| 14 | `GET` | `/user/{username}/requests` | Lấy lịch sử/tất cả các yêu cầu mượn của một người dùng. | Request |
| 15 | `POST` | `/reviews` | Tạo một đánh giá mới (nhắm vào `Book` hoặc `Chapter`). | Interaction |
| 16 | `GET` | `/reviews` | Lấy danh sách đánh giá (filter theo `targetType` và `targetId`). | Interaction |
