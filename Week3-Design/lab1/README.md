# Thiết kế resource cho Blog API

## Bài toán

> Nền tảng blog đơn giản

Một blog cho phép người dùng đăng bài viết (posts), mỗi bài có bình luận (comments) và gắn thẻ (tags). Mỗi user có hồ sơ và đăng ký theo dõi (follow) tác giả khác.

Hãy thiết kế cấu trúc endpoint đầy đủ.
    1. Xác định resources trong miền
    2. Phân loại collection / item / sub-resource
    3. Vẽ sơ đồ cây endpoint và quyết định version segment
    4. Triển khai Flask routes cho collection /posts

## Thiết kế

### 1. Resource

    Item:
        user           -> Profile của user
        post           -> Bài viết
        comment, tag   -> (Optional)

    Collection & sub-resources:
        users
        user/followers -> Người theo dõi user này
        user/following -> Người được user này theo dõi
        
        user/posts     -> Bài viết do user này đăng tải
        post/comments
        post/tags

### 2. Sơ đồ endpoint

Sơ đồ endpoint được demo rỗng một phần bằng Flask [tại đây](./blog_routes.py).

    ```markdown

    /api/v1
    │
    └── /users
        ├── GET                         Lấy danh sách users
        ├── POST                        Tạo user
        │
        └── /{user_id}
            ├── GET                     Lấy thông tin user
            ├── PATCH                   Cập nhật user
            ├── DELETE                  Xóa user
            │
            ├── /posts
            │   └── GET                 Lấy các post của user
            │
            ├── /followers
            │   └── GET                 Lấy danh sách follower (user khác đang follow người này)
            │
            ├── /following
            │   ├── GET                 Lấy danh sách user đang following (người được user này follow)
            │   └── POST                Follow người dùng khác
            │
            └── /posts
                ├── GET                         Lấy danh sách posts do user này đăng tải
                ├── POST                        Tạo post mới
                │
                └── /{post_id}
                    ├── GET                     Lấy một post
                    ├── PATCH                   Cập nhật post
                    ├── DELETE                  Xóa post
                    │
                    ├── /comments
                    │   ├── GET                 Lấy comments của post
                    │   └── POST                Tạo comment cho post
                    │
                    └── /tags
                        ├── GET                 Lấy tags của post
                        └── POST                Gắn tag vào post             
    ```
