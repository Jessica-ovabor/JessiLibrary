from flask import Flask ,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import os
from dotenv import load_dotenv


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///library.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
db = SQLAlchemy(app)
load_dotenv()

# Define your Book model with a UUID field
class Book(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
@app.route('/')
def index():
    return jsonify(message="I love books-Welcome to the world of psycopathic mini  novels")
# Create a book
@app.route('/create/books', methods=['POST'])
def create_book():
    data = request.get_json()
    isbn = data.get('isbn')  # Extracts ISBN from JSON request data

    # Check if a book with the provided ISBN exists
    isbn_exists = Book.query.filter_by(isbn=isbn).first()

    if isbn_exists:
        return jsonify({'message': f"Book with ISBN {isbn} already exists. Choose a new one"})

    # Create a new book only if the ISBN doesn't exist
    new_book = Book(title=data['title'], author=data['author'], isbn=isbn)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book created successfully'})


# Search for books
@app.route('/search/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    book_list = []
    
    for book in books:
        book_list.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn
        })
    return jsonify(book_list)
#search books using isbn
@app.route('/search/books/<string:isbn>', methods=['GET'])
def search_book_by_isbn(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn
        })
    return jsonify({'message': 'Book not found'})

# Delete a book by ISBN
@app.route('/delete/books/<string:isbn>', methods=['DELETE'])
def delete_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'})
    return jsonify({'message': 'Book not found'})

#Update a book by ISBN
@app.route('/update/books/<string:isbn>', methods=['PUT'])
def update_book(isbn):
    data = request.get_json()
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        book.title = data['title']
        book.author = data['author']
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})
    return jsonify({'message': 'Book not found'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

