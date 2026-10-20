import __future__

from flask import Flask
from .models import db, seed_data
from .routes.books import bp as books_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(books_bp, url_prefix='/books')

with app.app_context():
    db.create_all()
    seed_data() # Gọi hàm seed

if __name__ == '__main__':
    app.run(debug=True, port=5000)

