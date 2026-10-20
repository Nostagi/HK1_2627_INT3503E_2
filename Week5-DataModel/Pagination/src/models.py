from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Table, Column

db = SQLAlchemy()

# Bảng trung gian cho quan hệ nhiều-nhiều giữa Book và Author
book_authors = db.Table('book_authors',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Book(db.Model):
    __tablename__ = 'book'
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(200), nullable=False)
    isbn = mapped_column(String(13), unique=True, nullable=False)
    price_vnd = mapped_column(Integer, nullable=False)
    stock = mapped_column(Integer, default=0)
    category_id = mapped_column(ForeignKey("category.id"))
    
    category = relationship("Category")
    authors = relationship("Author", secondary=book_authors)

    def to_dict(self):
        return {
            "id": f"book_{self.id}", 
            "title": self.title,
            "price_vnd": self.price_vnd,
            "isbn": self.isbn,
            "stock": self.stock,
            "category_id": self.category_id
        }

def seed_data():
    """Hàm tạo dữ liệu mẫu (chỉ chạy nếu DB trống)"""
    if Book.query.first():
        print("Database đã có dữ liệu, bỏ qua bước seed.")
        return

    print("Đang tạo dữ liệu mẫu...")

    # 1. Tạo Categories
    c_fiction = Category(name="Fiction")
    c_science = Category(name="Science")
    c_tech = Category(name="Technology")
    c_history = Category(name="History")
    db.session.add_all([c_fiction, c_science, c_tech, c_history])

    # 2. Tạo Authors
    a_rowling = Author(name="J.K. Rowling")
    a_asimov = Author(name="Isaac Asimov")
    a_harari = Author(name="Yuval Noah Harari")
    a_martin = Author(name="Robert C. Martin")
    a_orwell = Author(name="George Orwell")
    a_tolkien = Author(name="J.R.R. Tolkien")
    db.session.add_all([a_rowling, a_asimov, a_harari, a_martin, a_orwell, a_tolkien])
    
    # Phải commit để lấy được ID của Category và Author
    db.session.commit()

    # 3. Tạo 15 cuốn sách mẫu với giá và tồn kho ngẫu nhiên
    books_data = [
        {"title": "Harry Potter and the Philosopher's Stone", "isbn": "9780747532699", "price": 250000, "stock": 50, "cat": c_fiction, "authors": [a_rowling]},
        {"title": "Harry Potter and the Chamber of Secrets", "isbn": "9780747538493", "price": 260000, "stock": 40, "cat": c_fiction, "authors": [a_rowling]},
        {"title": "Foundation", "isbn": "9780553293357", "price": 180000, "stock": 30, "cat": c_science, "authors": [a_asimov]},
        {"title": "I, Robot", "isbn": "9780553294385", "price": 190000, "stock": 25, "cat": c_science, "authors": [a_asimov]},
        {"title": "Sapiens: A Brief History of Humankind", "isbn": "9780062316097", "price": 300000, "stock": 100, "cat": c_history, "authors": [a_harari]},
        {"title": "Homo Deus: A Brief History of Tomorrow", "isbn": "9780062464316", "price": 310000, "stock": 80, "cat": c_history, "authors": [a_harari]},
        {"title": "Clean Code", "isbn": "9780132350884", "price": 450000, "stock": 15, "cat": c_tech, "authors": [a_martin]},
        {"title": "Clean Architecture", "isbn": "9780134494166", "price": 480000, "stock": 20, "cat": c_tech, "authors": [a_martin]},
        {"title": "1984", "isbn": "9780451524935", "price": 150000, "stock": 60, "cat": c_fiction, "authors": [a_orwell]},
        {"title": "Animal Farm", "isbn": "9780452284241", "price": 120000, "stock": 75, "cat": c_fiction, "authors": [a_orwell]},
        {"title": "The Hobbit", "isbn": "9780547928227", "price": 220000, "stock": 45, "cat": c_fiction, "authors": [a_tolkien]},
        {"title": "The Lord of the Rings", "isbn": "9780544003415", "price": 350000, "stock": 35, "cat": c_fiction, "authors": [a_tolkien]},
        {"title": "The Robots of Dawn", "isbn": "9780553299496", "price": 210000, "stock": 10, "cat": c_science, "authors": [a_asimov]},
        {"title": "The Clean Coder", "isbn": "9780137081073", "price": 420000, "stock": 5, "cat": c_tech, "authors": [a_martin]},
        {"title": "21 Lessons for the 21st Century", "isbn": "9780525512172", "price": 290000, "stock": 55, "cat": c_history, "authors": [a_harari]}
    ]

    for data in books_data:
        book = Book(
            title=data["title"],
            isbn=data["isbn"],
            price_vnd=data["price"],
            stock=data["stock"],
            category=data["cat"],
            authors=data["authors"]
        )
        db.session.add(book)

    db.session.commit()
    print(f"Đã tạo thành công {len(books_data)} cuốn sách mẫu!")