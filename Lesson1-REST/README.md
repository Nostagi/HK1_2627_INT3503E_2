# Introduction to REST/json with Flask

## 1. Setup virtual environment

Linux / macOS

``` terminal

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# move to demo folder
cd "Lesson1-REST"   
```

Thực hiện chạy server

```terminal

python3 -m '<tên file>'

```

Các server mặc định chạy tại: [http://127.0.0.1:5000] hay localhost:5000

## 2. [App](./app.py)

Thực hiện bài 1. Demo cơ bản "Hello API", bao gồm hàm echo và health-check.

```terminal

# Hello API 
curl -i http://127.0.0.1:5000/ 

# Health check 
curl -i http://127.0.0.1:5000/health 

# Echo JSON 
curl -i -X POST http://127.0.0.1:5000/echo 
    \ -H "Content-Type: application/json" 
    \ -d '{"message":"Hello Flask"}'

```

## 3. Students

Student API hỗ trợ tạo, tìm kiếm theo tên, lấy theo ID, cập nhật GPA và xóa student.

```terminal

# Create a student
curl -i -X POST http://127.0.0.1:5000/students \
  -H "Content-Type: application/json" \
  -d '{"name":"Son","gpa":3.4}'

# Create another student
curl -i -X POST http://127.0.0.1:5000/students \
  -H "Content-Type: application/json" \
  -d '{"name":"An","gpa":3.6}'

# Search students by name
curl -i "http://127.0.0.1:5000/students?q=inev&limit=1"

# Get student by ID
curl -i http://127.0.0.1:5000/students/testcase_d

# Update student GPA
curl -i -X PUT http://127.0.0.1:5000/students \
  -H "Content-Type: application/json" \
  -d '{"id":"testcase_d","gpa":3.6}'

# Delete a student
curl -i -X DELETE http://127.0.0.1:5000/students \
  -H "Content-Type: application/json" \
  -d '{"id":"testcase_d"}'

```

## 4. [Books](./books.py)

Thực hiện Bài 6+. Demo đầy đủ cho một API quản lý sách cơ bản. Áp dụng pydantic cho input validation, chia layer routing và service.

```terminal
# Listing several (2) books
curl -i http://127.0.0.1:5000/books

# Search books
curl -i "http://127.0.0.1:5000/books?search=web&sort_by=year&order=desc&limit=10"

# Get a book by ID=1
curl -i http://127.0.0.1:5000/books/1

# Create a book
curl -i -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Something wrong","author":"John Doe","year":1800}'

# Update a book
curl -i -X PUT http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"API Design Patterns","author":"JJ. Geewax","year":2021}'


# Delete a book
curl -i -X DELETE http://127.0.0.1:5000/books/1


# Test validation
curl -i "http://127.0.0.1:5000/books?sort_by=invalid"
curl -i "http://127.0.0.1:5000/books?limit=-1"
curl -i -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"","author":""}'

```
